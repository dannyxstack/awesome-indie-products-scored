"""调用 AI 平台对项目打分。

- gpt / deepseek 共用 OpenAI 兼容客户端，仅 base_url / key 不同。
- 支持 dry-run 模拟模式（无需 key，用确定性假数据跑通管道）。
- 输出严格 JSON，带失败重试。
"""
import json
import os
import time

import config
import prompts


class AnalyzerError(Exception):
    pass


def _platform_by_name(name: str) -> dict:
    for p in config.AI_PLATFORMS:
        if p["name"] == name:
            return p
    raise AnalyzerError(f"未知平台: {name}")


def _mock_result(project: dict, platform: dict) -> dict:
    """dry-run：基于 id 生成确定性的假分数，用于验证管道。"""
    seed = int(project["id"], 16)
    scores = {k: 40 + (seed >> (i * 3)) % 60 for i, k in enumerate(prompts.DIMENSIONS)}
    return {
        "scores": scores,
        "reasons": {k: f"[mock] {cn}占位理由" for k, (cn, *_ ) in prompts.DIMENSIONS.items()},
        "overall_comment": "[mock] 模拟结果，仅用于验证管道",
    }


def _make_client(platform: dict):
    from openai import OpenAI

    api_key = os.environ.get(platform["api_key_env"])
    if not api_key:
        raise AnalyzerError(
            f"缺少环境变量 {platform['api_key_env']}（平台 {platform['name']}）"
        )
    return OpenAI(api_key=api_key, base_url=platform["base_url"],
                  timeout=config.REQUEST_TIMEOUT)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """用 embedding 模型批量向量化，返回与输入同序的向量列表。"""
    from openai import OpenAI

    emb = config.EMBEDDING
    api_key = os.environ.get(emb["api_key_env"])
    if not api_key:
        raise AnalyzerError(f"缺少环境变量 {emb['api_key_env']}（embedding 需要 OpenAI key）")
    client = OpenAI(api_key=api_key, base_url=emb["base_url"], timeout=config.REQUEST_TIMEOUT)
    batch = int(emb.get("batch", 256))
    out: list[list[float]] = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        resp = client.embeddings.create(model=emb["model"], input=chunk)
        # 按 index 排序，确保与输入顺序对齐
        out.extend(d.embedding for d in sorted(resp.data, key=lambda d: d.index))
    return out


def chat_json(platform_name: str, system: str, user: str, temperature: float = 0.2) -> str:
    """通用的"要 JSON"调用，返回模型原始文本。供打分/抽取等复用。"""
    platform = _platform_by_name(platform_name)
    client = _make_client(platform)
    resp = client.chat.completions.create(
        model=platform["model"],
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    return resp.choices[0].message.content


def _call_api(project: dict, platform: dict) -> str:
    """真实调用，返回模型的原始文本内容。"""
    client = _make_client(platform)
    resp = client.chat.completions.create(
        model=platform["model"],
        messages=[
            {"role": "system", "content": prompts.SYSTEM_PROMPT},
            {"role": "user", "content": prompts.build_user_prompt(project)},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return resp.choices[0].message.content


def _parse_and_validate(text: str) -> dict:
    """解析模型输出并校验字段完整、分数在 0-100。"""
    data = json.loads(text)
    scores = data.get("scores", {})
    reasons = data.get("reasons", {})
    clean_scores, clean_reasons = {}, {}
    for key in prompts.DIMENSIONS:
        if key not in scores:
            raise AnalyzerError(f"缺少维度分数: {key}")
        val = int(scores[key])
        clean_scores[key] = max(0, min(100, val))
        clean_reasons[key] = str(reasons.get(key, "")).strip()
    return {
        "scores": clean_scores,
        "reasons": clean_reasons,
        "overall_comment": str(data.get("overall_comment", "")).strip(),
    }


def analyze(project: dict, platform_name: str, dry_run: bool = False) -> dict:
    """对单个项目用指定平台打分，返回一条 score 记录。"""
    platform = _platform_by_name(platform_name)

    if dry_run:
        result = _mock_result(project, platform)
    else:
        last_err = None
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                result = _parse_and_validate(_call_api(project, platform))
                break
            except Exception as e:  # noqa: BLE001 — 统一重试
                last_err = e
                if attempt < config.MAX_RETRIES:
                    time.sleep(config.RETRY_BACKOFF * attempt)
        else:
            raise AnalyzerError(f"打分失败（{config.MAX_RETRIES}次）: {last_err}")

    return {
        "project_id": project["id"],
        "project_name": project["name"],
        "project_url": project["url"],
        "platform": platform_name,
        "model": platform["model"],
        "dry_run": dry_run,
        **result,
    }
