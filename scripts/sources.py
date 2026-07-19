"""多来源采集适配器：按 source["type"] 分派到对应的"抓取+解析"实现，
产出统一的 Project 结构，供下游 analyzer/renderer 使用（下游对来源无感知）。

Project 统一字段：
    id, name, url, repo_url, desc, status, author, author_github,
    date, source_repo, source_label

新增来源 = 写一个 collect_* 函数并在 REGISTRY 注册，其余不动。
"""
import json
import os
import urllib.parse
import urllib.request

import ids
import scraper
import parser as md_parser


# ---------- 类型一：1c7 主/子版面，以及同格式的 GitHub markdown ----------
def collect_1c7(src: dict) -> tuple[list[dict], list[str]]:
    md = scraper.fetch(src["raw_url"])
    return md_parser.parse(md, src.get("repo", ""), src.get("label", ""))


# ---------- 类型二：V2EX 节点（如创意节点 create） ----------
V2EX_UA = "indie-product-analyzer/0.1 (+local script)"


def _v2ex_topic_to_project(t: dict, node: str, label: str, warnings: list[str]) -> dict | None:
    """把一条 V2EX 主题（v1 或 v2 API 结构通用）映射为统一 Project；无标题/链接返回 None。"""
    from datetime import datetime, timezone
    title = (t.get("title") or "").strip()
    tid = t.get("id")
    # v2 的节点主题列表可能不带 url，用 id 兜底拼出主题链接
    url = (t.get("url") or (f"https://www.v2ex.com/t/{tid}" if tid else "")).strip()
    if not title or not url:
        warnings.append(f"[v2ex:{node}] 跳过无标题/链接的主题 id={tid}")
        return None
    desc = (t.get("content") or "").strip().replace("\r", " ").replace("\n", " ")
    member = t.get("member")
    author = member.get("username") if isinstance(member, dict) else None
    created = t.get("created")
    date = (datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d")
            if created else None)
    return {
        "id": ids.make_id(url, title),
        "name": title,
        "url": url,
        "repo_url": None,
        "desc": desc[:300],
        "status": "idea",           # V2EX 是点子/讨论，非已上线产品
        "author": author,
        "author_github": None,
        "date": date,
        "source_repo": f"v2ex/{node}",
        "source_label": label,
    }


def _v2ex_api2(node: str, label: str, token: str, pages: int) -> tuple[list[dict], list[str]]:
    """V2EX API 2.0：GET nodes/{node}/topics?p=，带 Bearer token，可翻页取历史。"""
    projects, warnings, seen = [], [], set()
    for p in range(1, max(1, pages) + 1):
        api = (f"https://www.v2ex.com/api/v2/nodes/{urllib.parse.quote(node)}"
               f"/topics?p={p}")
        req = urllib.request.Request(api, headers={
            "User-Agent": V2EX_UA, "Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 — 某页失败就停，保留已取到的
            warnings.append(f"[v2ex:{node}] 第 {p} 页请求失败: {e}")
            break
        if not data.get("success", True):
            warnings.append(f"[v2ex:{node}] API 返回失败: {data.get('message')}")
            break
        topics = data.get("result") or []
        if not topics:
            break  # 没有更多历史主题
        for t in topics:
            proj = _v2ex_topic_to_project(t, node, label, warnings)
            if proj and proj["id"] not in seen:
                seen.add(proj["id"])
                projects.append(proj)
    return projects, warnings


def _v2ex_api1(node: str, label: str) -> tuple[list[dict], list[str]]:
    """V2EX API 1.0（无需 token）：只返回该节点最新 10 条，作为无 token 时的回退。"""
    api = f"https://www.v2ex.com/api/topics/show.json?node_name={urllib.parse.quote(node)}"
    raw = scraper.fetch(api)
    topics = json.loads(raw)
    projects, warnings = [], []
    for t in topics:
        proj = _v2ex_topic_to_project(t, node, label, warnings)
        if proj:
            projects.append(proj)
    return projects, warnings


def collect_v2ex(src: dict) -> tuple[list[dict], list[str]]:
    """取某节点主题，每个主题映射为一个 Project。

    有 V2EX_API_TOKEN 时走官方 API 2.0（支持 pages 翻页取历史）；
    没有则回退 API 1.0（仅最新 10 条）。
    """
    node = src.get("node", "create")
    label = src.get("label", f"V2EX·{node}")
    token = os.environ.get("V2EX_API_TOKEN")
    if token:
        return _v2ex_api2(node, label, token, int(src.get("pages", 1)))
    return _v2ex_api1(node, label)


# ---------- 类型三：任意格式 markdown，交给 AI 抽取 ----------
def collect_github_md_ai(src: dict) -> tuple[list[dict], list[str]]:
    """抓取任意 markdown，用 OpenAI 兼容模型抽取项目列表。"""
    import extractor  # 延迟导入，避免无 key 时也强依赖
    md = scraper.fetch(src["raw_url"])
    items, warnings = extractor.extract_projects(md, platform_name=src.get("platform"))
    max_items = int(src.get("max_items", 0) or 0)   # 0 = 不限
    if max_items:
        items = items[:max_items]
    projects = []
    for it in items:
        url = (it.get("url") or "").strip()
        name = (it.get("name") or "").strip()
        if not name or not url:
            continue
        projects.append({
            "id": ids.make_id(url, name),
            "name": name,
            "url": url,
            "repo_url": url if "github.com" in url else None,
            "desc": (it.get("desc") or "").strip(),
            "status": "unknown",
            "author": it.get("author"),
            "author_github": None,
            "date": None,
            "source_repo": src.get("repo", ""),
            "source_label": src.get("label", "AI抽取"),
        })
    return projects, warnings


REGISTRY = {
    "1c7_readme": collect_1c7,
    "github_markdown": collect_1c7,   # 同格式子版面，直接复用
    "v2ex_node": collect_v2ex,
    "github_md_ai": collect_github_md_ai,
}

# 每种来源类型声明的可调参数：(参数键, 中文名, 默认值, 最小, 最大)。
# UI 据此为所选来源渲染输入框；适配器仍从 src.get(键) 读取，互不耦合。
# 新增类型 = 注册 REGISTRY + 在此加一行（无可调参数则留空列表）。
TYPE_PARAMS: dict[str, list[tuple]] = {
    "1c7_readme": [],
    "github_markdown": [],
    "v2ex_node": [("pages", "翻页数", 1, 1, 30)],
    "github_md_ai": [("max_items", "最多条数(0不限)", 0, 0, 5000)],
}


def params_for(src: dict) -> list[tuple]:
    """返回某来源可调参数的声明列表（供 UI 渲染）。"""
    return TYPE_PARAMS.get(src.get("type", "1c7_readme"), [])


def collect_one(src: dict) -> tuple[list[dict], list[str]]:
    fn = REGISTRY.get(src.get("type", "1c7_readme"))
    if fn is None:
        return [], [f"未知来源类型: {src.get('type')}"]
    return fn(src)


def collect_all(sources: list[dict]) -> tuple[list[dict], list[str]]:
    """采集所有来源并按规范化 URL 跨来源去重（先到先留）。"""
    seen: set[str] = set()
    all_projects: list[dict] = []
    all_warnings: list[str] = []
    for src in sources:
        try:
            projects, warnings = collect_one(src)
        except Exception as e:  # noqa: BLE001 — 单个来源失败不影响其它
            all_warnings.append(f"[{src.get('label', src.get('type'))}] 采集失败: {e}")
            continue
        kept = 0
        for p in projects:
            if p["id"] in seen:
                continue
            seen.add(p["id"])
            all_projects.append(p)
            kept += 1
        all_warnings.extend(warnings)
        dup = len(projects) - kept
        print(f"[sources] {src.get('label', src.get('type'))}: {kept} 个"
              + (f"（去重 {dup}）" if dup else "") + f"，{len(warnings)} 条警告")
    return all_projects, all_warnings
