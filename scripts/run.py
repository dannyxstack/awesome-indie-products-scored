"""主编排入口：抓取 -> 解析 -> 多平台打分(落库) -> 幂等生成报告。

用法：
    python run.py                 # 增量：只分析 POC 范围内、库中没有的 (项目,平台)
    python run.py --dry-run       # 模拟模式，无需 key，验证全链路
    python run.py -n 10           # 覆盖 POC 数量
    python run.py --full          # 分析全部项目（谨慎：调用量巨大）
    python run.py --refresh       # 重新抓取并解析 README（否则复用 projects.json）
    python run.py --no-report     # 只打分不生成报告

分数落库 data/analysis.db；报告输出到 reports/（每日/排行/月度）。
"""
import argparse
import json

import config
import sources
import state
import analyzer
import db
import report


def _read_projects_json() -> list[dict]:
    """直接读现有 projects.json（不存在返回 []，不触发采集）。"""
    if config.PROJECTS_JSON.exists():
        return json.loads(config.PROJECTS_JSON.read_text(encoding="utf-8"))
    return []


def collect_sources(selected_labels: list[str] | None = None,
                    overrides: dict[str, dict] | None = None) -> list[dict]:
    """采集来源并写入 projects.json。

    selected_labels: 要采集的来源 label 列表；None=全部（整体重写）。
                     指定子集时按 label «合并保留»：只替换所选来源的项目，其它来源原样保留。
    overrides:       {label: {参数键: 值}}，覆盖该来源本次采集的参数（如 pages/max_items）。
    """
    overrides = overrides or {}
    srcs = config.SOURCES
    if selected_labels is not None:
        srcs = [s for s in srcs if s["label"] in selected_labels]
    srcs = [{**s, **overrides.get(s["label"], {})} for s in srcs]

    new_projects, warnings = sources.collect_all(srcs)

    if selected_labels is None:
        merged = new_projects                      # 全量：整体重写
    else:
        collected = {s["label"] for s in srcs}
        new_by = _group_by_label(new_projects)
        old_by = _group_by_label(_read_projects_json())
        ordered: list[dict] = []                   # 按 config 顺序：选中用新数据，其它用旧数据
        for s in config.SOURCES:
            lbl = s["label"]
            ordered += new_by.get(lbl, []) if lbl in collected else old_by.get(lbl, [])
        merged = _dedup_by_id(ordered)

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.PROJECTS_JSON.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if warnings:
        print(f"[run] 采集/解析警告 {len(warnings)} 条（前5）")
        for w in warnings[:5]:
            print("   ", w)
    new_ids = state.record_and_diff(merged)
    state.update_commits(srcs)
    if new_ids:
        print(f"[run] 本次新增 {len(new_ids)} 个项目")
    return merged


def _group_by_label(projects: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for p in projects:
        grouped.setdefault(p.get("source_label", ""), []).append(p)
    return grouped


def _dedup_by_id(projects: list[dict]) -> list[dict]:
    out, seen = [], set()
    for p in projects:
        if p["id"] in seen:
            continue
        seen.add(p["id"])
        out.append(p)
    return out


def refresh_projects() -> list[dict]:
    """采集全部来源，整体重写 projects.json。"""
    return collect_sources(selected_labels=None)


def load_projects() -> list[dict]:
    if config.PROJECTS_JSON.exists():
        return json.loads(config.PROJECTS_JSON.read_text(encoding="utf-8"))
    return refresh_projects()


def get_projects(force_refresh: bool) -> list[dict]:
    """决定用缓存还是重新采集：--refresh 强制；否则按 commit 检测是否有更新。"""
    if force_refresh:
        return refresh_projects()
    if not config.PROJECTS_JSON.exists():
        return refresh_projects()
    if config.GITHUB_UPDATE_CHECK and state.any_github_changed(config.SOURCES):
        print("[run] 检测到来源更新，重新采集...")
        return refresh_projects()
    print("[run] 来源无变化，使用本地缓存 projects.json")
    return load_projects()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-n", type=int, default=None, help="分析项目数量（默认 config.POC_LIMIT）")
    ap.add_argument("--full", action="store_true", help="分析全部项目")
    ap.add_argument("--refresh", action="store_true", help="重新抓取解析 README")
    ap.add_argument("--no-report", action="store_true")
    args = ap.parse_args()

    projects = get_projects(force_refresh=args.refresh)
    if not args.full:
        limit = args.n if args.n is not None else config.POC_LIMIT
        projects = projects[:limit]
    print(f"[run] 待处理项目 {len(projects)} 个，平台 {[p['name'] for p in config.AI_PLATFORMS]}，dry_run={args.dry_run}\n")

    conn = db.connect()
    for proj in projects:                 # 先把工作集项目落库
        db.upsert_project(conn, proj)
    conn.commit()

    total_calls = 0
    for platform in config.AI_PLATFORMS:
        name = platform["name"]
        done = skipped = failed = 0
        for proj in projects:
            pid = proj["id"]
            if not args.dry_run and db.has_score(conn, pid, name):
                skipped += 1
                continue
            try:
                record = analyzer.analyze(proj, name, dry_run=args.dry_run)
            except analyzer.AnalyzerError as e:
                failed += 1
                print(f"  [{name}] 失败: {proj['name']} -> {e}")
                continue
            db.upsert_score(conn, record)
            done += 1
            total_calls += 1
            if done % 5 == 0:
                print(f"  [{name}] 已完成 {done} ...")
        conn.commit()
        print(f"[run] 平台 {name}: 新打分 {done}，跳过 {skipped}，失败 {failed}")
    conn.close()

    print(f"\n[run] 本次共 {total_calls} 次分析调用")

    if not args.no_report:
        res = report.generate_all()
        print(f"[run] 报告已生成（已评分 {res['scored']} 个）：")
        print(f"      每日 {res['daily']}")
        print(f"      排行 {len(res['rankings'])} 个 · 月度 {len(res['monthly'])} 个")


if __name__ == "__main__":
    main()
