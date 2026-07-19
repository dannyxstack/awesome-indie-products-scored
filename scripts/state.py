"""来源状态与更新检测。

data/source_state.json 结构：
    {
      "known_ids": ["<pid>", ...],          # 已见过的所有项目 ID（跨来源）
      "commits":   { "<repo>@<path>": "<sha>" }  # 各 GitHub 文件上次已知 commit
    }

- record_and_diff(projects)      : 比对已知 ID，返回本次新增，并更新 known_ids
- github_latest_commit(...)       : 查某文件最新 commit sha
- any_github_changed(sources)     : 是否有 GitHub 来源发生变化（用于跳过无谓抓取）
- update_commits(sources)         : 抓取后记录各 GitHub 来源当前 commit
"""
import json

import config
import scraper

STATE_JSON = config.DATA_DIR / "source_state.json"


def load() -> dict:
    if STATE_JSON.exists():
        return json.loads(STATE_JSON.read_text(encoding="utf-8"))
    return {"known_ids": [], "commits": {}}


def save(st: dict) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def record_and_diff(projects: list[dict]) -> list[str]:
    """返回本次相对历史新增的项目 ID，并把它们并入 known_ids。"""
    st = load()
    known = set(st.get("known_ids", []))
    new_ids = [p["id"] for p in projects if p["id"] not in known]
    if new_ids:
        st["known_ids"] = list(known | set(new_ids))
        save(st)
    return new_ids


def _commit_key(src: dict) -> str:
    return f"{src.get('repo', '')}@{src.get('path', '')}"


def github_latest_commit(repo: str, branch: str, path: str) -> str | None:
    """查 GitHub 上某文件的最新 commit sha；失败返回 None（不阻断流程）。"""
    api = (f"https://api.github.com/repos/{repo}/commits"
           f"?path={path}&sha={branch}&per_page=1")
    try:
        data = json.loads(scraper.fetch(api))
        return data[0]["sha"] if data else None
    except Exception:
        return None


def _github_sources(sources: list[dict]) -> list[dict]:
    return [s for s in sources
            if s.get("type") in ("1c7_readme", "github_markdown", "github_md_ai")
            and s.get("repo") and s.get("path")]


def any_github_changed(sources: list[dict]) -> bool:
    """任一 GitHub 来源的最新 commit 与上次记录不同则返回 True。
    查不到 commit（如网络/限流）时保守地返回 True（宁可多跑一次）。"""
    st = load()
    stored = st.get("commits", {})
    for s in _github_sources(sources):
        sha = github_latest_commit(s["repo"], s.get("branch", "master"), s["path"])
        if sha is None or stored.get(_commit_key(s)) != sha:
            return True
    return False


def update_commits(sources: list[dict]) -> None:
    """抓取完成后记录各 GitHub 来源当前 commit sha。"""
    st = load()
    commits = st.setdefault("commits", {})
    for s in _github_sources(sources):
        sha = github_latest_commit(s["repo"], s.get("branch", "master"), s["path"])
        if sha:
            commits[_commit_key(s)] = sha
    save(st)
