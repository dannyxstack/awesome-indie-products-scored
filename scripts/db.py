"""SQLite 存储层：分析结果落库，报告从库中幂等生成。

- projects：采集到的项目（累积，first_seen/last_seen 记录首末次见到）
- scores  ：各平台打分（主键 project_id+platform，重跑覆盖）

opportunity_raw 入库时算好：需求×变现 / (竞争×难度)，分母下限 1。
"""
import json
import sqlite3
from datetime import datetime

import config

DB_PATH = config.DATA_DIR / "analysis.db"
DIMS = ["demand", "competition", "cost", "monetization", "execution"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id            TEXT PRIMARY KEY,
    name          TEXT,
    url           TEXT,
    repo_url      TEXT,
    desc          TEXT,
    status        TEXT,
    author        TEXT,
    author_github TEXT,
    date          TEXT,
    source_repo   TEXT,
    source_label  TEXT,
    first_seen    TEXT,
    last_seen     TEXT
);
CREATE TABLE IF NOT EXISTS scores (
    project_id      TEXT,
    platform        TEXT,
    model           TEXT,
    demand          INTEGER,
    competition     INTEGER,
    cost            INTEGER,
    monetization    INTEGER,
    execution       INTEGER,
    opportunity_raw REAL,
    reasons         TEXT,
    overall_comment TEXT,
    dry_run         INTEGER,
    scored_at       TEXT,
    PRIMARY KEY (project_id, platform)
);
CREATE TABLE IF NOT EXISTS project_vectors (
    project_id  TEXT PRIMARY KEY,
    model       TEXT,
    dim         INTEGER,
    vector      TEXT,       -- JSON float 数组
    text_hash   TEXT,       -- sha1(name+desc)，用于增量判断是否需重算
    updated_at  TEXT
);
CREATE TABLE IF NOT EXISTS similar (
    project_id  TEXT,       -- 源产品
    similar_id  TEXT,       -- 相似产品
    rank        INTEGER,    -- 1..K
    score       REAL,       -- 余弦相似度 0-1
    method      TEXT,       -- embedding / tfidf
    computed_at TEXT,
    PRIMARY KEY (project_id, similar_id)
);
"""


def connect() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def opportunity_raw(scores: dict) -> float:
    d, m = scores["demand"], scores["monetization"]
    c, e = max(1, scores["competition"]), max(1, scores["execution"])
    return d * m / (c * e)


def upsert_project(conn: sqlite3.Connection, p: dict) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT INTO projects
           (id,name,url,repo_url,desc,status,author,author_github,date,
            source_repo,source_label,first_seen,last_seen)
           VALUES (:id,:name,:url,:repo_url,:desc,:status,:author,:author_github,:date,
                   :source_repo,:source_label,:now,:now)
           ON CONFLICT(id) DO UPDATE SET
             name=excluded.name, url=excluded.url, repo_url=excluded.repo_url,
             desc=excluded.desc, status=excluded.status, author=excluded.author,
             author_github=excluded.author_github, date=excluded.date,
             source_repo=excluded.source_repo, source_label=excluded.source_label,
             last_seen=excluded.last_seen""",
        {**p, "now": now},
    )


def upsert_score(conn: sqlite3.Connection, rec: dict) -> None:
    s = rec["scores"]
    conn.execute(
        """INSERT INTO scores
           (project_id,platform,model,demand,competition,cost,monetization,execution,
            opportunity_raw,reasons,overall_comment,dry_run,scored_at)
           VALUES (:pid,:platform,:model,:demand,:competition,:cost,:monetization,:execution,
                   :opp,:reasons,:overall,:dry_run,:now)
           ON CONFLICT(project_id,platform) DO UPDATE SET
             model=excluded.model, demand=excluded.demand, competition=excluded.competition,
             cost=excluded.cost, monetization=excluded.monetization, execution=excluded.execution,
             opportunity_raw=excluded.opportunity_raw, reasons=excluded.reasons,
             overall_comment=excluded.overall_comment, dry_run=excluded.dry_run,
             scored_at=excluded.scored_at""",
        {
            "pid": rec["project_id"], "platform": rec["platform"], "model": rec["model"],
            **{k: s[k] for k in DIMS},
            "opp": opportunity_raw(s),
            "reasons": json.dumps(rec.get("reasons", {}), ensure_ascii=False),
            "overall": rec.get("overall_comment", ""),
            "dry_run": 1 if rec.get("dry_run") else 0,
            "now": datetime.now().isoformat(timespec="seconds"),
        },
    )


def has_score(conn: sqlite3.Connection, project_id: str, platform: str) -> bool:
    """是否已有该平台的真实（非 dry-run）打分。"""
    row = conn.execute(
        "SELECT 1 FROM scores WHERE project_id=? AND platform=? AND dry_run=0 LIMIT 1",
        (project_id, platform),
    ).fetchone()
    return row is not None


def fetch_scored(conn: sqlite3.Connection) -> tuple[dict, list]:
    """返回 (projects_by_id, score_rows)。仅含在 projects 表里的项目。"""
    projects = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM projects")}
    scores = [dict(r) for r in conn.execute("SELECT * FROM scores")]
    return projects, scores


# ---- 相似产品：向量缓存 + 关系表 ----
def fetch_vector_hashes(conn: sqlite3.Connection) -> dict:
    """{project_id: text_hash}，用于判断哪些项目需要（重新）向量化。"""
    return {r["project_id"]: r["text_hash"]
            for r in conn.execute("SELECT project_id, text_hash FROM project_vectors")}


def upsert_vector(conn: sqlite3.Connection, pid: str, model: str, dim: int,
                  vector_json: str, text_hash: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT INTO project_vectors (project_id,model,dim,vector,text_hash,updated_at)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(project_id) DO UPDATE SET
             model=excluded.model, dim=excluded.dim, vector=excluded.vector,
             text_hash=excluded.text_hash, updated_at=excluded.updated_at""",
        (pid, model, dim, vector_json, text_hash, now),
    )


def fetch_vectors_for(conn: sqlite3.Connection, ids: list[str]) -> tuple[list, list]:
    """取指定 id 的缓存向量，返回 (ids, vectors)，顺序对齐。"""
    out_ids, out_vecs = [], []
    id_set = set(ids)
    for r in conn.execute("SELECT project_id, vector FROM project_vectors"):
        if r["project_id"] in id_set:
            out_ids.append(r["project_id"])
            out_vecs.append(json.loads(r["vector"]))
    return out_ids, out_vecs


def replace_similar(conn: sqlite3.Connection, rows: list[tuple], method: str) -> None:
    """整体替换某 method 的相似关系。rows: (pid, sid, rank, score, method, computed_at)。"""
    conn.execute("DELETE FROM similar WHERE method=?", (method,))
    conn.executemany(
        """INSERT OR REPLACE INTO similar
           (project_id,similar_id,rank,score,method,computed_at) VALUES (?,?,?,?,?,?)""",
        rows,
    )


def fetch_similar(conn: sqlite3.Connection, pid: str, method: str | None = None) -> list[dict]:
    q = "SELECT * FROM similar WHERE project_id=?"
    args: list = [pid]
    if method:
        q += " AND method=?"
        args.append(method)
    q += " ORDER BY rank"
    return [dict(r) for r in conn.execute(q, args)]


def count_similar_sources(conn: sqlite3.Connection, method: str | None = None) -> int:
    """有多少个产品已建立相似关系。"""
    q = "SELECT COUNT(DISTINCT project_id) AS n FROM similar"
    args: list = []
    if method:
        q += " WHERE method=?"
        args.append(method)
    return conn.execute(q, args).fetchone()["n"]
