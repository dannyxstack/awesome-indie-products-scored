"""AI 打分的 prompt 模板与维度定义。

各维度按"自然含义"打分（0-100 整数），方向不统一——需求/变现越高越好，
竞争/成本/难度越高越差。综合机会分用公式 需求×变现/(竞争×难度) 计算，
方向自洽。每个维度的 100/0 含义见下方定义，务必按定义打分。
"""

# 维度定义：key -> (中文名, 100分含义, 0分含义, 方向)
# direction: "up" 越高越有利于商业机会；"down" 越高越不利
DIMENSIONS = {
    "demand":        ("需求指数",       "市场需求巨大、受众广",         "几乎无人需要",              "up"),
    "competition":   ("竞争度",         "红海、巨头林立、竞争白热化",   "蓝海、几乎无竞争对手",      "down"),
    "cost":          ("成本指数",       "需要巨额资金/团队/资源",       "近乎零成本即可做出并运营",  "down"),
    "monetization":  ("变现预估",       "变现路径清晰、付费意愿强",     "极难变现、几乎无收入模型",  "up"),
    "execution":     ("执行+推广难度",  "技术极难且获客(SEO/GEO)渠道极窄", "技术与获客都很容易",     "down"),
}

SYSTEM_PROMPT = """你是一位资深的独立开发商业分析师，熟悉 SaaS、工具类产品、AI 应用的市场格局、\
获客渠道（SEO 搜索引擎优化、GEO 生成式引擎优化/在 AI 回答中被推荐）与变现模式。
你的任务是对给定的独立开发者项目，从商业机会角度做冷静、务实、可落地的评估。
要求：
- 基于产品的真实赛道现状判断，不被产品自我介绍的措辞带偏，也不无端唱衰。
- 每个维度按其下方给出的 100/0 含义打分（0-100 整数）。注意各维度方向不同：
  需求/变现越高越好；竞争/成本/难度越高代表越激烈/越贵/越难（越不利）。
- 每个维度给出一个整数分数和一句（30字以内）中文理由，理由要具体、给出依据。
- 严格只输出 JSON，不要任何额外文字或 markdown 代码块围栏。"""


def _dimension_spec() -> str:
    lines = []
    for key, (cn, hi, lo, _dir) in DIMENSIONS.items():
        lines.append(f'  - "{key}"（{cn}）：100 = {hi}；0 = {lo}')
    return "\n".join(lines)


def build_user_prompt(project: dict) -> str:
    """为单个项目构造用户消息。"""
    repo = project.get("repo_url") or "无"
    return f"""请评估以下独立开发者项目：

项目名称：{project.get('name')}
一句话介绍：{project.get('desc')}
产品链接：{project.get('url')}
代码仓库：{repo}
当前状态：{project.get('status')}

评分维度（0-100 整数，各维方向不同，请严格按每条的 100/0 含义打分）：
{_dimension_spec()}

请严格按以下 JSON 结构输出（scores 为整数，reasons 为中文短句）：
{{
  "scores": {{ "demand": 0, "competition": 0, "cost": 0, "monetization": 0, "execution": 0 }},
  "reasons": {{ "demand": "", "competition": "", "cost": "", "monetization": "", "execution": "" }},
  "overall_comment": "一句话总体判断（40字以内）"
}}"""
