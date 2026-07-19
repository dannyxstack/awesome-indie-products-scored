"""抓取一个或多个 README 原始 Markdown。

用 raw.githubusercontent.com 直接取原文，避免 GitHub API 的未认证限流。
支持可选的 GITHUB_TOKEN（放在环境变量里）以提高稳定性。
"""
import os
import urllib.request

USER_AGENT = "indie-product-analyzer/0.1 (+local script)"


def fetch(raw_url: str, timeout: int = 30) -> str:
    """抓取单个 raw README，返回 Markdown 文本。"""
    headers = {"User-Agent": USER_AGENT}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(raw_url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def fetch_sources(sources: list[dict]) -> list[dict]:
    """按配置抓取多个数据源，返回 [{repo, label, raw_url, markdown}]。"""
    results = []
    for src in sources:
        md = fetch(src["raw_url"])
        results.append({**src, "markdown": md})
        print(f"[scraper] {src['label']} ({src['repo']}): {len(md)} chars")
    return results


if __name__ == "__main__":
    from config import SOURCES

    for item in fetch_sources(SOURCES):
        print(item["repo"], "->", len(item["markdown"]), "chars")
