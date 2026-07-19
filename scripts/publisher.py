"""把报告与数据提交到本仓库（本地 git commit）。

只做 add + commit，**不 push**——推送到远程需你手动执行/确认。
"""
import subprocess
from datetime import datetime

import config

# 需要纳入版本的产物（相对仓库根）
TRACKED = [
    "reports",
    "README.md",
    "data/analysis.db",
    "data/projects.json",
    "data/source_state.json",
]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=config.ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def commit_reports(message: str | None = None) -> str:
    """暂存报告与数据并提交。返回提交后的简短状态。"""
    existing = [p for p in TRACKED if (config.ROOT / p).exists()]
    if existing:
        _git("add", *existing)

    if not _git("status", "--porcelain"):
        return "无变更，未提交"

    msg = message or f"docs(report): update reports {datetime.now():%Y-%m-%d}"
    _git("commit", "-m", msg)
    return _git("log", "-1", "--oneline")


if __name__ == "__main__":
    print(commit_reports())
