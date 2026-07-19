"""相似产品（竞品发现）：把 name+desc 向量化，取 Top-K 近邻落库。

- 向量缓存在 project_vectors，只对新增/文案变动的项目重新调用 embedding（省钱）。
- 近邻在「当前工作集」内计算：归一化后余弦相似度取每个产品最相近的 K 个。
- 结果整体替换写入 similar 表（method=embedding）。

用法：
    python similar.py            # 对 projects.json 全量建立相似关系
"""
import hashlib
import json
from datetime import datetime

import config
import db
import analyzer

METHOD = "embedding"


def _text(p: dict) -> str:
    return f"{p.get('name', '')}。{p.get('desc', '') or ''}".strip()


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def _ensure_vectors(conn, projects: list[dict], log=print) -> int:
    """对新增/文案变动的项目补算向量并缓存，返回本次向量化的数量。"""
    have = db.fetch_vector_hashes(conn)
    todo = [p for p in projects if have.get(p["id"]) != _hash(_text(p))]
    if not todo:
        log(f"向量全部命中缓存（{len(projects)} 个），无需调用 API。")
        return 0
    log(f"向量化 {len(todo)} 个（缓存命中 {len(projects) - len(todo)} 个）...")
    vecs = analyzer.embed_texts([_text(p) for p in todo])
    model = config.EMBEDDING["model"]
    for p, v in zip(todo, vecs):
        db.upsert_vector(conn, p["id"], model, len(v), json.dumps(v), _hash(_text(p)))
    conn.commit()
    return len(todo)


def rebuild(projects: list[dict], top_k: int | None = None,
            min_score: float | None = None, log=print) -> dict:
    """为传入的项目集合建立相似关系并落库。返回统计信息。"""
    import numpy as np

    top_k = top_k or config.SIMILAR_TOP_K
    min_score = config.SIMILAR_MIN_SCORE if min_score is None else min_score

    conn = db.connect()
    n_new = _ensure_vectors(conn, projects, log)

    ids = [p["id"] for p in projects]
    ids, vecs = db.fetch_vectors_for(conn, ids)
    if len(ids) < 2:
        conn.close()
        return {"vectorized": n_new, "total": len(ids), "pairs": 0, "top_k": top_k}

    mat = np.asarray(vecs, dtype="float32")
    norm = np.linalg.norm(mat, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    mat = mat / norm
    sims = mat @ mat.T                      # NxN 余弦相似度

    now = datetime.now().isoformat(timespec="seconds")
    rows: list[tuple] = []
    for i, pid in enumerate(ids):
        order = np.argsort(-sims[i])        # 相似度降序
        rank = 0
        for j in order:
            if j == i:
                continue
            s = float(sims[i, j])
            if s < min_score:
                break
            rank += 1
            rows.append((pid, ids[j], rank, round(s, 4), METHOD, now))
            if rank >= top_k:
                break

    db.replace_similar(conn, rows, METHOD)
    conn.commit()
    conn.close()
    log(f"完成：{len(ids)} 个产品，写入 {len(rows)} 条相似关系（Top-{top_k}）。")
    return {"vectorized": n_new, "total": len(ids), "pairs": len(rows), "top_k": top_k}


def main() -> None:
    projects = json.loads(config.PROJECTS_JSON.read_text(encoding="utf-8"))
    print(f"[similar] 对 {len(projects)} 个项目建立相似关系...")
    res = rebuild(projects)
    print(f"[similar] {res}")


if __name__ == "__main__":
    main()
