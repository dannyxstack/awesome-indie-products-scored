"""用 OpenAI 兼容模型从任意格式 markdown 中抽取项目列表。

适配陌生排版的榜单/README，无需为每种格式手写解析器。
过长文本按字符切块，分块抽取后合并。
"""
import json

import analyzer
import config

SYSTEM = """你是信息抽取器。用户会给你一段 markdown 文本（可能是产品/项目榜单）。
请从中抽取所有"独立开发者产品或项目"，忽略纯工具链接、导航、说明性段落。
严格只输出 JSON：{"items": [{"name": "", "url": "", "desc": "", "author": ""}]}
- url 取该项目的主链接（官网或仓库），必须是 http(s) 开头的真实链接；无链接则跳过该项。
- desc 为一句话中文简介（若原文是英文可保留）。author 未知则留空字符串。
- 不要编造不存在的项目，不要输出 markdown 代码围栏。"""

CHUNK_CHARS = 12000


def _chunks(text: str, size: int = CHUNK_CHARS) -> list[str]:
    lines, buf, cur = text.splitlines(keepends=True), [], 0
    for ln in lines:
        if cur + len(ln) > size and buf:
            yield "".join(buf)
            buf, cur = [], 0
        buf.append(ln)
        cur += len(ln)
    if buf:
        yield "".join(buf)


def extract_projects(markdown: str, platform_name: str | None = None
                     ) -> tuple[list[dict], list[str]]:
    platform = platform_name or config.PHASE2_PLATFORM
    items, warnings = [], []
    for i, chunk in enumerate(_chunks(markdown), 1):
        try:
            raw = analyzer.chat_json(platform, SYSTEM, chunk, temperature=0.0)
            data = json.loads(raw)
            items.extend(data.get("items", []))
        except Exception as e:  # noqa: BLE001
            warnings.append(f"[ai_extract] 第 {i} 块抽取失败: {e}")
    return items, warnings
