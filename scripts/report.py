"""从 SQLite 幂等生成 Markdown 报告。

产出：
- reports/daily/YYYY-MM-DD.md   每日报告（近3月最新10总览 + 5维度近3月Top10）
- reports/rankings/<dim>-top100.md  5 个全量维度 Top100
- reports/monthly/YYYY-MM.md     每月全量（增量：按项目添加月份分组）
- 主 README.md 顶部「分析报告」索引（标记块内幂等替换）

各平台分数分别列出、不融合；排序/机会分用跨平台均值维度计算，
综合机会分按全库最大原始值归一化到 0-100（跨报告一致）。
"""
import json
from datetime import date, datetime

import config
import db
import prompts

# 5 个维度排行：(dim, 标题, ascending=低者更优)
RANKINGS = [
    ("demand",       "需求指数最高",                False),
    ("competition",  "竞争度最低（最蓝海）",        True),
    ("cost",         "成本指数最低（最省钱）",      True),
    ("monetization", "变现预估最强",                False),
    ("execution",    "执行+推广难度最低（推广最友好）", True),
]
DIM_CN = {k: v[0] for k, v in prompts.DIMENSIONS.items()}

REPORTS_DIR = config.ROOT / "reports"
DAILY_DIR = REPORTS_DIR / "daily"
RANK_DIR = REPORTS_DIR / "rankings"
MONTH_DIR = REPORTS_DIR / "monthly"
RECENT_MONTHS = 3
DAILY_TOPN = 10
FULL_TOPN = 100

MARK_START = "<!-- REPORTS:START -->"
MARK_END = "<!-- REPORTS:END -->"


# ---------- 从 DB 组装项目级聚合 ----------
class Agg:
    def __init__(self, projects, scores):
        self.proj = projects                     # id -> project row
        self.by_pid: dict[str, list] = {}
        for s in scores:
            self.by_pid.setdefault(s["project_id"], []).append(s)
        self.gmax = max((db.opportunity_raw(self._srow(r)) for rows in self.by_pid.values()
                         for r in rows), default=1.0) or 1.0

    @staticmethod
    def _srow(r):  # score row -> dims dict
        return {k: r[k] for k in db.DIMS}

    def scored_ids(self):
        return [pid for pid in self.by_pid if pid in self.proj]

    def dims_avg(self, pid) -> dict:
        rows = self.by_pid[pid]
        return {k: sum(r[k] for r in rows) / len(rows) for k in db.DIMS}

    def opp(self, pid) -> float:
        raw = db.opportunity_raw(self.dims_avg(pid))
        return min(100.0, raw / self.gmax * 100)

    def platforms(self, pid):
        return {r["platform"]: r for r in self.by_pid[pid]}


def _cutoff_recent() -> str:
    d = date.today()
    m = d.month - RECENT_MONTHS
    y = d.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}-{d.day:02d}"


# ---------- 表格片段 ----------
def _overview_table(agg: Agg, pids: list[str]) -> list[str]:
    dims = list(prompts.DIMENSIONS.items())
    header = ["项目", "一句话介绍"] + [cn for _, (cn, *_r) in dims] + ["综合机会分"]
    L = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for pid in pids:
        p = agg.proj[pid]
        plats = agg.platforms(pid)
        row = [f"[{p['name']}]({p['url']})", _desc(agg, pid)]
        for key, _ in dims:
            row.append(" · ".join(str(r[key]) for r in plats.values()))
        row.append(f"{agg.opp(pid):.0f}")
        L.append("| " + " | ".join(row) + " |")
    return L


def _ranking_rows(agg: Agg, pids: list[str], dim: str, ascending: bool, limit: int):
    ordered = sorted(pids, key=lambda x: agg.dims_avg(x)[dim], reverse=not ascending)
    return ordered[:limit]


def _details_section(agg: Agg, pids: list[str]) -> list[str]:
    """逐项详情：每个项目的简介 + 各平台打分与理由。"""
    L = ["## 逐项详情", ""]
    for pid in pids:
        p = agg.proj[pid]
        L.append(f"### [{p['name']}]({p['url']})　综合机会分 {agg.opp(pid):.0f}")
        L.append("")
        L.append(f"- 简介：{p.get('desc') or '—'}")
        meta = f"- 作者：{p.get('author') or '—'} ｜ 添加日期：{p.get('date') or '—'}"
        if p.get("repo_url"):
            meta += f" ｜ [仓库]({p['repo_url']})"
        L += [meta, ""]
        for plat, r in agg.platforms(pid).items():
            reasons = json.loads(r["reasons"] or "{}")
            opp_p = min(100.0, db.opportunity_raw({k: r[k] for k in db.DIMS}) / agg.gmax * 100)
            L.append(f"AI评测的综合机会分 {opp_p:.0f}：{r.get('overall_comment') or ''}")
            L.append("")
            for key, (cn, *_r) in prompts.DIMENSIONS.items():
                L.append(f"  - {cn} `{r[key]}` — {reasons.get(key, '')}")
            L.append("")
    return L


def _dim_meanings() -> list[str]:
    arrow = {"up": "↑高优", "down": "↓低优"}
    out = []
    for key, (cn, hi, lo, d) in prompts.DIMENSIONS.items():
        out.append(f"- **{cn}**（{arrow[d]}）：100={hi}；0={lo}")
    return out


def _desc(agg: "Agg", pid: str, limit: int = 42) -> str:
    """一句话介绍：清理换行与竖线，避免破坏表格；超长截断。"""
    d = (agg.proj[pid].get("desc") or "").replace("\r", " ").replace("\n", " ")
    d = d.replace("|", "/").strip()
    return (d[:limit] + "…") if len(d) > limit else (d or "—")


def _scoring_note() -> list[str]:
    """指标如何评估/计算——排名文档顶部统一说明。"""
    L = ["## 评分与指标说明", "",
         "- **维度打分**：每个维度由 AI 依据下方「100/0 含义」对项目在 **0-100** 打分；"
         "多平台各自打分、表中并列展示（不融合），排序用各平台均值。",
         "- **综合机会分**：`需求指数 × 变现预估 ÷ (竞争度 × 执行+推广难度)`，"
         "再按全库最大原始值归一化到 **0-100**（最高=100，跨报告一致）。", "",
         "**各维度 100/0 含义：**"]
    L += _dim_meanings()
    L.append("")
    return L


# ---------- 每日报告 ----------
def gen_daily(agg: Agg) -> str:
    today = date.today().isoformat()
    cutoff = _cutoff_recent()
    scored = agg.scored_ids()
    recent = [pid for pid in scored if (agg.proj[pid].get("date") or "") >= cutoff]

    L = [f"# 每日报告 · {today}", "",
         f"- 数据源：{', '.join(s['label'] for s in config.SOURCES)}",
         f"- 统计口径：近 {RECENT_MONTHS} 个月（{cutoff} 起）新增项目；已评分 {len(scored)} 个", ""]
    L += _scoring_note()

    # 综合评分：近3月最新10
    newest = sorted(recent, key=lambda x: agg.proj[x].get("date") or "", reverse=True)[:DAILY_TOPN]
    month_link = f"../monthly/{today[:7]}.md"
    L += [f"## 综合评分（近3月最新 {DAILY_TOPN} 个）　[▶ 全部排名]({month_link})", ""]
    L += _overview_table(agg, newest) if newest else ["（近3月暂无已评分项目）"]
    L.append("")

    # 5 排行：近3月 Top10
    L += ["## 排行（近3月 Top10）", ""]
    for dim, title, asc in RANKINGS:
        full_link = f"../rankings/{dim}-top100.md"
        L += [f"### {title}　[▶ 全部Top100]({full_link})", ""]
        rows = _ranking_rows(agg, recent, dim, asc, DAILY_TOPN)
        if not rows:
            L += ["（近3月暂无数据）", ""]
            continue
        L += ["| # | 项目 | 一句话介绍 | " + DIM_CN[dim] + " | 综合机会分 |",
              "|---|---|---|---|---|"]
        for i, pid in enumerate(rows, 1):
            p = agg.proj[pid]
            L.append(f"| {i} | [{p['name']}]({p['url']}) | {_desc(agg, pid)} | "
                     f"{agg.dims_avg(pid)[dim]:.0f} | {agg.opp(pid):.0f} |")
        L.append("")

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    path = DAILY_DIR / f"{today}.md"
    path.write_text("\n".join(L), encoding="utf-8")
    return str(path)


# ---------- 全量 5 排行 Top100 ----------
def gen_rankings(agg: Agg) -> list[str]:
    scored = agg.scored_ids()
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for dim, title, asc in RANKINGS:
        rows = _ranking_rows(agg, scored, dim, asc, FULL_TOPN)
        order = "升序（越低越优）" if asc else "降序（越高越优）"
        L = [f"# 全量排行 · {title} · Top{FULL_TOPN}", "",
             f"- 生成时间：{datetime.now():%Y-%m-%d %H:%M} ｜ 全库已评分 {len(scored)} 个", ""]
        L += _scoring_note()
        L += [f"> 本表按「{DIM_CN[dim]}」{order}排序，取前 {FULL_TOPN}。", "",
              "| # | 项目 | 一句话介绍 | " + DIM_CN[dim] + " | 综合机会分 |",
              "|---|---|---|---|---|"]
        for i, pid in enumerate(rows, 1):
            p = agg.proj[pid]
            L.append(f"| {i} | [{p['name']}]({p['url']}) | {_desc(agg, pid)} | "
                     f"{agg.dims_avg(pid)[dim]:.0f} | {agg.opp(pid):.0f} |")
        path = RANK_DIR / f"{dim}-top100.md"
        path.write_text("\n".join(L), encoding="utf-8")
        paths.append(str(path))
    return paths


# ---------- 每月全量（增量：每月一个文件） ----------
def gen_monthly(agg: Agg) -> list[str]:
    groups: dict[str, list[str]] = {}
    for pid in agg.scored_ids():
        d = agg.proj[pid].get("date")
        if d and len(d) >= 7:
            groups.setdefault(d[:7], []).append(pid)
    MONTH_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for ym, pids in sorted(groups.items()):
        pids.sort(key=lambda x: agg.opp(x), reverse=True)
        L = [f"# 月度全量报告 · {ym}", "",
             f"- 生成时间：{datetime.now():%Y-%m-%d %H:%M} ｜ 本月已评分 {len(pids)} 个", ""]
        L += _scoring_note()
        L += ["> 下表按综合机会分降序。", ""]
        L += _overview_table(agg, pids)
        L += ["", "---", ""]
        L += _details_section(agg, pids)
        path = MONTH_DIR / f"{ym}.md"
        path.write_text("\n".join(L), encoding="utf-8")
        paths.append(str(path))
    return paths


# ---------- 主 README 顶部索引 ----------
def update_readme_index(agg: Agg, daily_path: str, rank_paths: list[str],
                        month_paths: list[str]) -> None:
    from pathlib import Path
    readme = config.ROOT / "README.md"

    def r(p):  # 绝对路径 -> 相对仓库根的 posix 路径
        return Path(p).resolve().relative_to(config.ROOT).as_posix()

    # 最新一月的已评分项目，按综合机会分降序
    def _ym(pid):
        return (agg.proj[pid].get("date") or "")[:7]
    scored = agg.scored_ids()
    months = sorted({_ym(pid) for pid in scored if _ym(pid)}, reverse=True)
    latest_ym = months[0] if months else None
    month_pids = sorted([pid for pid in scored if _ym(pid) == latest_ym],
                        key=lambda x: agg.opp(x), reverse=True)

    lines = [MARK_START, ""]
    if latest_ym and month_pids:
        lines += [f"## 📊 最新一月结果（{latest_ym}）", "",
                  f"> 生成时间：{datetime.now():%Y-%m-%d %H:%M} ｜ "
                  f"本月已评分 {len(month_pids)} 个，按综合机会分降序", ""]
        lines += _overview_table(agg, month_pids)
        lines.append("")

    lines.append("## 📁 完整报告")
    if daily_path:
        lines.append(f"- 最新每日报告：[{r(daily_path)}]({r(daily_path)}) ｜ [全部每日](reports/daily/)")
    if rank_paths:
        lines.append("- 全量排行 Top100：")
        for dim, title, _ in RANKINGS:
            p = RANK_DIR / f"{dim}-top100.md"
            lines.append(f"  - [{title}]({r(str(p))})")
    if month_paths:
        latest = r(sorted(month_paths)[-1])
        lines.append(f"- 月度全量报告：[{latest}]({latest}) ｜ [全部月度](reports/monthly/)")
    lines += ["", MARK_END]
    block = "\n".join(lines)

    if readme.exists():
        text = readme.read_text(encoding="utf-8")
    else:
        text = "# awesome-indie-products\n"
    if MARK_START in text and MARK_END in text:
        pre = text.split(MARK_START)[0]
        post = text.split(MARK_END, 1)[1]
        text = pre + block + post
    else:
        # 插到第一个标题行之后（顶端）
        parts = text.split("\n", 1)
        head = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        text = head + "\n\n" + block + "\n\n" + rest
    readme.write_text(text, encoding="utf-8")


# ---------- 编排 ----------
def generate_all() -> dict:
    conn = db.connect()
    projects, scores = db.fetch_scored(conn)
    conn.close()
    agg = Agg(projects, scores)
    daily = gen_daily(agg)
    ranks = gen_rankings(agg)
    months = gen_monthly(agg)
    update_readme_index(agg, daily, ranks, months)
    result = {"daily": daily, "rankings": ranks, "monthly": months,
              "scored": len(agg.scored_ids())}
    return result


if __name__ == "__main__":
    print(json.dumps(generate_all(), ensure_ascii=False, indent=2))
