"""跨来源统一的 URL 规范化与项目 ID 生成（用于去重）。"""
import hashlib
import re


def normalize_url(url: str) -> str:
    """规范化 URL 作为去重键：去协议/www、去 query 与 fragment、去尾斜杠、转小写。"""
    u = (url or "").strip()
    u = u.split("#", 1)[0]
    u = re.sub(r"\?.*$", "", u)
    u = re.sub(r"^https?://", "", u, flags=re.I)
    u = re.sub(r"^www\.", "", u, flags=re.I)
    return u.rstrip("/").lower()


def make_id(url: str, name: str = "") -> str:
    """项目唯一 ID：优先按规范化 URL（同一产品跨来源可去重）；无 URL 时退回名称。"""
    key = normalize_url(url) or (name or "").strip().lower()
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
