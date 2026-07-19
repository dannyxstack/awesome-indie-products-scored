"""把 README Markdown 解析成结构化项目列表。

层级结构（主版面）：
    ## 3. 项目列表                         <- 列表开始锚点
    ### 2026 年 7 月 17 号添加             <- 日期分组
    #### 作者名(地区) - [Github](url)      <- 作者
    * :white_check_mark: [名](url)：描述   <- 项目条目

解析失败/异常的行会收集到 warnings 里，供人工抽查，不静默丢弃。
"""
import re

import ids

# 列表开始锚点：## 3. 项目列表 / ## 项目列表
RE_LIST_START = re.compile(r"^##\s+.*项目列表\s*$")
# 日期分组：### 2026 年 7 月 17 号添加
RE_DATE = re.compile(r"^###\s+.*?(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[号日]")
# 其它 ### 标题（非日期），出现时清空当前日期上下文
RE_H3 = re.compile(r"^###\s+")
# 作者行：#### 作者名 ...
RE_AUTHOR = re.compile(r"^####\s+(.+?)\s*$")
# 项目行：* :status: 其余内容
RE_PROJECT = re.compile(r"^\*\s+:([a-z0-9_]+):\s*(.+?)\s*$")
# 从项目内容里取首个 [名](url)：描述
RE_NAME_URL = re.compile(r"^\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\s*[：:]?\s*(?P<desc>.*)$")
# 从任意文本取第一个 [Github]/[GitHub](url) 链接
RE_GH_LINK = re.compile(r"\[(?:Github|GitHub)\]\((https?://[^)]+)\)")
# 描述末尾的 " - [查看仓库](url)"
RE_REPO_SUFFIX = re.compile(r"\s*-\s*\[查看仓库\]\((https?://[^)]+)\)\s*$")

STATUS_MAP = {
    "white_check_mark": "online",   # 已上线
    "clock8": "in_dev",             # 开发中
    "x": "closed",                  # 已关闭/缺乏维护
}


def _parse_author(header: str) -> tuple[str, str | None]:
    """返回 (作者名, 作者github链接或None)。作者名去掉 ' - [xxx](...)' 部分。"""
    gh = RE_GH_LINK.search(header)
    author_github = gh.group(1) if gh else None
    name = re.split(r"\s*-\s*\[", header, maxsplit=1)[0].strip()
    return name, author_github


def _parse_project_body(body: str) -> dict | None:
    """解析 '[名](url)：描述 - [查看仓库](url)'。失败返回 None。"""
    m = RE_NAME_URL.match(body)
    if not m:
        return None
    name = m.group("name").strip()
    url = m.group("url").strip()
    desc = m.group("desc").strip()

    repo_url = None
    suffix = RE_REPO_SUFFIX.search(desc)
    if suffix:
        repo_url = suffix.group(1)
        desc = RE_REPO_SUFFIX.sub("", desc).strip()
    # 若项目主链接本身就是 github 仓库，也记为 repo_url
    if repo_url is None and "github.com" in url:
        repo_url = url
    return {"name": name, "url": url, "desc": desc, "repo_url": repo_url}


def parse(markdown: str, source_repo: str = "", source_label: str = "") -> tuple[list[dict], list[str]]:
    """解析单个 README。返回 (projects, warnings)。"""
    projects: list[dict] = []
    warnings: list[str] = []

    in_list = False
    cur_date: str | None = None
    cur_author: str | None = None
    cur_author_github: str | None = None

    for lineno, raw in enumerate(markdown.splitlines(), start=1):
        line = raw.rstrip()
        if not in_list:
            if RE_LIST_START.match(line):
                in_list = True
            continue

        dm = RE_DATE.match(line)
        if dm:
            y, mo, d = dm.groups()
            cur_date = f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
            cur_author = None
            continue
        if RE_H3.match(line):  # 其它三级标题，重置日期上下文
            cur_date = None
            cur_author = None
            continue

        am = RE_AUTHOR.match(line)
        if am:
            cur_author, cur_author_github = _parse_author(am.group(1))
            continue

        pm = RE_PROJECT.match(line)
        if pm:
            status_raw, body = pm.groups()
            parsed = _parse_project_body(body)
            if parsed is None:
                warnings.append(f"[{source_repo}:L{lineno}] 项目行解析失败: {body[:80]}")
                continue
            projects.append({
                "id": ids.make_id(parsed["url"], parsed["name"]),
                "name": parsed["name"],
                "url": parsed["url"],
                "repo_url": parsed["repo_url"],
                "desc": parsed["desc"],
                "status": STATUS_MAP.get(status_raw, status_raw),
                "author": cur_author,
                "author_github": cur_author_github,
                "date": cur_date,
                "source_repo": source_repo,
                "source_label": source_label,
            })

    return projects, warnings


def parse_sources(scraped: list[dict]) -> tuple[list[dict], list[str]]:
    """解析多个已抓取的数据源，合并结果。"""
    all_projects: list[dict] = []
    all_warnings: list[str] = []
    for item in scraped:
        projects, warnings = parse(item["markdown"], item["repo"], item["label"])
        all_projects.extend(projects)
        all_warnings.extend(warnings)
        print(f"[parser] {item['label']}: {len(projects)} 个项目, {len(warnings)} 条警告")
    return all_projects, all_warnings
