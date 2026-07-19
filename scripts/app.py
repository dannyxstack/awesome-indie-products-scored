"""本地管理工作流界面（Streamlit）。

运行：streamlit run scripts/app.py
数据源为 SQLite（data/analysis.db），报告由 report.py 幂等生成。
"""
import json

import pandas as pd
import streamlit as st

import config
import sources
import prompts
import analyzer
import db
import similar
import report
import publisher
import run as pipeline

STATUS_CN = {"online": "已上线", "in_dev": "开发中", "closed": "已关闭",
             "idea": "点子", "unknown": "未知"}


# ---------- 从 DB 读取（每次 rerun 直接读，数据量小） ----------
def load_projects() -> list[dict]:
    return pipeline.load_projects()


def load_db():
    """返回 (scores_by_plat, analyzed_map)。
    scores_by_plat: {平台: {pid: {scores, model, reasons, overall_comment}}}
    analyzed_map:   {pid: [平台...]}
    """
    conn = db.connect()
    _, rows = db.fetch_scored(conn)
    conn.close()
    scores_by_plat: dict[str, dict] = {}
    analyzed_map: dict[str, list] = {}
    for r in rows:
        rec = {
            "scores": {k: r[k] for k in db.DIMS},
            "model": r["model"],
            "reasons": json.loads(r["reasons"] or "{}"),
            "overall_comment": r["overall_comment"] or "",
        }
        scores_by_plat.setdefault(r["platform"], {})[r["project_id"]] = rec
        analyzed_map.setdefault(r["project_id"], []).append(r["platform"])
    return scores_by_plat, analyzed_map


# ---------- 侧边栏 ----------
def sidebar() -> dict:
    st.sidebar.header("控制面板")
    st.sidebar.caption("数据源采集")
    labels = [s["label"] for s in config.SOURCES]
    selected = st.sidebar.multiselect("选择要采集的来源", labels, default=labels)

    # 为每个所选来源渲染其可调参数（参数声明见 sources.TYPE_PARAMS）
    overrides: dict[str, dict] = {}
    for s in config.SOURCES:
        if s["label"] not in selected:
            continue
        for key, cn, default, lo, hi in sources.params_for(s):
            val = st.sidebar.number_input(
                f"{s['label']} · {cn}", int(lo), int(hi), int(s.get(key, default)),
                key=f"param_{s['label']}_{key}")
            overrides.setdefault(s["label"], {})[key] = int(val)

    if st.sidebar.button("🔄 采集所选来源", disabled=not selected):
        with st.spinner("采集中..."):
            all_selected = len(selected) == len(labels)
            projects = pipeline.collect_sources(
                None if all_selected else selected, overrides)
        st.sidebar.success(f"已采集：共 {len(projects)} 个项目（本次来源 {len(selected)} 个）")

    st.sidebar.divider()
    all_names = [p["name"] for p in config.AI_PLATFORMS]
    platforms = st.sidebar.multiselect("分析平台", all_names, default=all_names)
    dry_run = st.sidebar.toggle("dry-run 模拟模式（不调真实 API）", value=False)
    if dry_run:
        st.sidebar.info("模拟模式：用确定性假数据验证管道，不消耗额度。")
    return {"platforms": platforms, "dry_run": dry_run}


# ---------- Tab 1：项目浏览 ----------
def tab_browse(projects: list[dict], analyzed_map: dict):
    st.subheader("项目浏览")
    col1, col2, col3 = st.columns([3, 1, 1])
    kw = col1.text_input("搜索（名称/简介）", "").strip().lower()
    status_opt = col2.selectbox("状态", ["全部"] + list(dict.fromkeys(STATUS_CN.values())))
    sources = list(dict.fromkeys(p.get("source_label") or "" for p in projects))
    source_opt = col3.selectbox("来源", ["全部"] + [s for s in sources if s])

    rows = []
    for p in projects:
        if kw and kw not in (p["name"] + p["desc"]).lower():
            continue
        scn = STATUS_CN.get(p["status"], p["status"])
        if status_opt != "全部" and scn != status_opt:
            continue
        if source_opt != "全部" and (p.get("source_label") or "") != source_opt:
            continue
        done = analyzed_map.get(p["id"], [])
        rows.append({
            "名称": p["name"], "来源": p.get("source_label") or "",
            "状态": scn, "日期": p["date"] or "",
            "作者": p["author"] or "", "已分析平台": ", ".join(done),
            "简介": p["desc"][:60], "链接": p["url"],
        })
    st.caption(f"筛选结果：{len(rows)} / {len(projects)} 个项目")

    # 分页（默认 100 条/页）
    page_size = 100
    total_pages = max(1, (len(rows) + page_size - 1) // page_size)
    pc1, pc2 = st.columns([1, 4])
    page = pc1.number_input("页码", 1, total_pages, 1, step=1)
    start = (int(page) - 1) * page_size
    page_rows = rows[start:start + page_size]
    pc2.caption(f"第 {int(page)} / {total_pages} 页，本页 {len(page_rows)} 条")

    st.dataframe(
        pd.DataFrame(page_rows), use_container_width=True, hide_index=True,
        column_config={"链接": st.column_config.LinkColumn("链接", width="small")},
    )


# ---------- Tab 2：运行分析 ----------
def tab_run(projects: list[dict], cfg: dict):
    st.subheader("运行分析")

    if "last_run" in st.session_state:
        lr = st.session_state.pop("last_run")
        st.success(f"分析完成：成功 {lr['ok']} 次，失败 {len(lr['failed'])} 次。"
                   "结果已入库，可在「③ 评分结果」查看，或到「④ 报告」生成报告。")
        if lr["failed"]:
            st.warning("失败项：\n\n" + "\n\n".join(f"- {x}" for x in lr["failed"]))

    if not cfg["platforms"]:
        st.warning("请在侧边栏至少选择一个分析平台。")
        return

    mode = st.radio("分析范围", ["最近 N 个", "手动选择项目"], horizontal=True)
    if mode == "最近 N 个":
        n = st.number_input("N", 1, len(projects), min(config.POC_LIMIT, len(projects)))
        targets = projects[: int(n)]
    else:
        names = st.multiselect("选择项目", [p["name"] for p in projects])
        targets = [p for p in projects if p["name"] in names]

    incremental = st.checkbox("增量：跳过已分析的 (项目, 平台)", value=True)

    conn = db.connect()
    pending = 0
    for p in targets:
        for plat in cfg["platforms"]:
            if not (incremental and not cfg["dry_run"] and db.has_score(conn, p["id"], plat)):
                pending += 1
    st.info(f"待分析项目 {len(targets)} 个 × 平台 {len(cfg['platforms'])} 个 = 预计 **{pending}** 次调用"
            + ("（dry-run 不计费）" if cfg["dry_run"] else ""))

    if st.button("▶ 开始分析", type="primary", disabled=pending == 0):
        for p in targets:
            db.upsert_project(conn, p)
        conn.commit()
        prog = st.progress(0.0)
        logbox = st.container(height=240)
        done = ok = 0
        failed: list[str] = []
        for p in targets:
            for plat in cfg["platforms"]:
                if incremental and not cfg["dry_run"] and db.has_score(conn, p["id"], plat):
                    continue
                try:
                    rec = analyzer.analyze(p, plat, dry_run=cfg["dry_run"])
                    db.upsert_score(conn, rec)
                    ok += 1
                    logbox.write(f"✅ [{plat}] {p['name']}")
                except analyzer.AnalyzerError as e:
                    failed.append(f"[{plat}] {p['name']} — {e}")
                    logbox.write(f"❌ [{plat}] {p['name']} — {e}")
                done += 1
                prog.progress(done / pending)
        conn.commit()
        conn.close()
        st.session_state["last_run"] = {"ok": ok, "failed": failed}
        st.rerun()
    else:
        conn.close()


# ---------- Tab 3：评分结果 ----------
def tab_results(projects: list[dict], scores_by_plat: dict[str, dict]):
    st.subheader("评分结果")
    proj_by_id = {p["id"]: p for p in projects}
    scored_ids = {pid for t in scores_by_plat.values() for pid in t}
    if not scored_ids:
        st.info("还没有评分数据，去「运行分析」跑一批。")
        return

    dims = list(prompts.DIMENSIONS.items())
    all_raw = [db.opportunity_raw(rec["scores"])
               for t in scores_by_plat.values() for rec in t.values()]
    gmax = max(all_raw) if all_raw else 1.0

    rows = []
    for pid in scored_ids:
        p = proj_by_id.get(pid)
        if not p:
            continue
        row = {"名称": p["name"]}
        for plat, table in scores_by_plat.items():
            rec = table.get(pid)
            if not rec:
                continue
            for key, (cn, *_) in dims:
                row[f"{cn}·{plat}"] = rec["scores"][key]
            row[f"机会分·{plat}"] = round(min(100, db.opportunity_raw(rec["scores"]) / gmax * 100))
        rows.append(row)
    df = pd.DataFrame(rows)
    overall_cols = [c for c in df.columns if c.startswith("机会分·")]
    if overall_cols:
        df = df.sort_values(overall_cols[0], ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.caption("打分理由详情")
    sel = st.selectbox("选择项目查看理由",
                       [proj_by_id[i]["name"] for i in scored_ids if i in proj_by_id])
    sel_id = next((i for i in scored_ids if proj_by_id.get(i) and proj_by_id[i]["name"] == sel), None)
    for plat, table in scores_by_plat.items():
        rec = table.get(sel_id)
        if not rec:
            continue
        with st.expander(f"{plat}（{rec['model']}）：{rec.get('overall_comment', '')}", expanded=True):
            for key, (cn, *_) in dims:
                st.write(f"- **{cn}** `{rec['scores'][key]}` — {rec['reasons'].get(key, '')}")


# ---------- Tab 5：相似产品（竞品发现） ----------
def tab_similar(projects: list[dict]):
    st.subheader("相似产品（竞品发现）")
    st.caption(f"用 {config.EMBEDDING['model']} 向量化 name+desc，余弦相似取 Top-{config.SIMILAR_TOP_K}。"
               "向量带缓存，仅对新增/改动的项目重新计算。")

    conn = db.connect()
    built = db.count_similar_sources(conn, similar.METHOD)
    conn.close()
    st.info(f"当前已建立相似关系的产品：**{built}** 个。")

    if st.button("🔗 计算 / 更新相似关系", type="primary"):
        logbox = st.container(height=180)
        try:
            with st.spinner("向量化 + 计算近邻中..."):
                res = similar.rebuild(projects, log=lambda m: logbox.write(m))
            st.success(f"完成：本次向量化 {res['vectorized']} 个，覆盖 {res['total']} 个产品，"
                       f"写入 {res['pairs']} 条关系。")
        except analyzer.AnalyzerError as e:
            st.error(f"失败：{e}")
        except Exception as e:  # noqa: BLE001
            st.error(f"失败：{e}")

    st.divider()
    proj_by_id = {p["id"]: p for p in projects}
    if not projects:
        st.info("还没有项目，先在侧边栏采集来源。")
        return
    sel = st.selectbox("选择产品查看相似（竞品）", [p["name"] for p in projects])
    sel_p = next((p for p in projects if p["name"] == sel), None)
    if not sel_p:
        return
    conn = db.connect()
    sims = db.fetch_similar(conn, sel_p["id"], similar.METHOD)
    conn.close()
    if not sims:
        st.warning("该产品还没有相似关系，点上方按钮计算一次。")
        return
    rows = []
    for s in sims:
        sp = proj_by_id.get(s["similar_id"])
        if not sp:
            continue
        rows.append({
            "相似度": round(s["score"], 3),
            "名称": sp["name"],
            "来源": sp.get("source_label") or "",
            "简介": (sp.get("desc") or "")[:60],
            "链接": sp["url"],
            "疑似同款": "⚠" if s["score"] >= 0.98 else "",
        })
    st.dataframe(
        pd.DataFrame(rows), use_container_width=True, hide_index=True,
        column_config={"链接": st.column_config.LinkColumn("链接", width="small")},
    )


# ---------- Tab 4：报告 & 提交 ----------
def tab_report():
    st.subheader("报告 & 提交")
    st.caption("从数据库幂等生成：每日报告 / 5 个全量排行 / 每月全量，并更新 README 索引。")
    if st.button("📄 生成全部报告"):
        with st.spinner("生成中..."):
            res = report.generate_all()
        st.session_state["report_res"] = res

    res = st.session_state.get("report_res")
    if res:
        st.success(f"已生成（已评分 {res['scored']} 个）：每日 1 · 排行 {len(res['rankings'])} · 月度 {len(res['monthly'])}")
        daily = report.DAILY_DIR / f"{__import__('datetime').date.today().isoformat()}.md"
        if daily.exists():
            text = daily.read_text(encoding="utf-8")
            st.download_button("⬇ 下载今日报告", text, file_name=daily.name)
            with st.expander("📄 今日每日报告预览", expanded=True):
                st.markdown(text)
        st.divider()
        st.caption("提交到本仓库（本地 commit，不会 push）")
        if st.button("✅ 本地提交报告"):
            st.success(publisher.commit_reports())


# ---------- 主入口 ----------
def main():
    st.set_page_config(page_title="独立开发项目 · 商机分析", layout="wide")
    st.title("独立开发者项目 · 商机可行性分析")

    cfg = sidebar()
    projects = load_projects()
    scores_by_plat, analyzed_map = load_db()

    t1, t2, t3, t4, t5 = st.tabs(
        ["① 项目浏览", "② 运行分析", "③ 评分结果", "④ 报告 & 提交", "⑤ 相似产品"])
    with t1:
        tab_browse(projects, analyzed_map)
    with t2:
        tab_run(projects, cfg)
    with t3:
        tab_results(projects, scores_by_plat)
    with t4:
        tab_report()
    with t5:
        tab_similar(projects)


if __name__ == "__main__":
    main()
