"""全局配置：数据源、POC 范围、AI 平台配置、文件路径。"""
from pathlib import Path

# ---- 路径 ----
ROOT = Path(__file__).resolve().parent.parent

# 自动加载项目根目录的 .env（存在 python-dotenv 时）
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass
DATA_DIR = ROOT / "data"
PROJECTS_JSON = DATA_DIR / "projects.json"
# 分析结果落库 data/analysis.db（见 db.py）；报告输出到 reports/（见 report.py）

# ---- 数据源：每个来源用 type 指定采集适配器（见 sources.REGISTRY）----
#   type=1c7_readme     : 1c7 主/子版面格式（状态机解析）
#   type=github_markdown: 同上格式的其它 GitHub markdown，直接复用
#   type=v2ex_node      : V2EX 节点（官方 API），需 node
#   type=github_md_ai   : 任意格式 markdown，交给 AI 抽取
GITHUB_UPDATE_CHECK = True   # 采集前用 commits API 检查 README 是否变化

SOURCES = [
    {
        "type": "1c7_readme",
        "repo": "1c7/chinese-independent-developer",
        "branch": "master",
        "path": "README.md",
        "label": "chinese-independent-developer",
        "raw_url": "https://raw.githubusercontent.com/1c7/chinese-independent-developer/master/README.md"
    },
    # 暂缓：AI 抽取来源会消耗 token，准备好 DEEPSEEK_API_KEY 后再取消注释启用
    # {
    #     "type": "github_md_ai", "repo": "XiaomingX/1000-chinese-independent-developer-plus",
    #     "label": "XiaomingX·plus",
    #     "raw_url": "https://raw.githubusercontent.com/XiaomingX/1000-chinese-independent-developer-plus/main/README.md"
    # },

    # 子版面（同格式，取消注释即用）：
    # {"type": "github_markdown", "repo": "1c7/chinese-independent-developer",
    #  "branch": "master", "path": "pages/README-Programmer-Edition.md", "label": "程序员版面",
    #  "raw_url": "https://raw.githubusercontent.com/1c7/chinese-independent-developer/master/pages/README-Programmer-Edition.md"},

    # V2EX 创意节点：填了 V2EX_API_TOKEN 走官方 API 2.0，可用 pages 翻页取历史（每页约 20 条，
    # 限流 600 次/小时）；没填 token 则回退 API 1.0 只取最新 10 条，pages 被忽略。
    {"type": "v2ex_node", "node": "create", "label": "V2EX·创意", "pages": 1},

    # 任意 markdown 用 AI 抽取（platform 省略则用 PHASE2_PLATFORM）：
    # {"type": "github_md_ai", "repo": "someone/awesome-xxx", "label": "某榜单",
    #  "raw_url": "https://raw.githubusercontent.com/someone/awesome-xxx/main/README.md"},
]

# ---- POC 范围 ----
# 列表是倒序（最新在前），取解析结果的前 N 个即"最近新增"的项目。
POC_LIMIT = 30

# ---- AI 平台 ----
# 两个平台都用 OpenAI 兼容协议，共用同一个客户端，仅 base_url / key 不同。
#   name         : 用于文件名和报告列头
#   model        : 实际模型 id
#   base_url     : None 表示官方 OpenAI 端点；DeepSeek 用其兼容端点
#   api_key_env  : 从哪个环境变量读取 key
AI_PLATFORMS = [
    {
        "name": "gpt",
        "model": "gpt-4o-mini",
        "base_url": None,
        "api_key_env": "OPENAI_API_KEY",
    },
    {
        "name": "deepseek",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
]

# Phase 2 单平台验证时先只用这个平台（其名字须在 AI_PLATFORMS 中）。
PHASE2_PLATFORM = "deepseek"

# 调用参数
REQUEST_TIMEOUT = 60      # 单次请求超时（秒）
MAX_RETRIES = 3           # 失败重试次数
RETRY_BACKOFF = 2.0       # 重试退避基数（秒）

# ---- 相似产品（竞品发现）----
# 用 embedding 把 name+desc 向量化，余弦相似取 Top-K 近邻。DeepSeek 无 embedding 端点，用 OpenAI。
EMBEDDING = {
    "model": "text-embedding-3-small",
    "api_key_env": "OPENAI_API_KEY",
    "base_url": None,      # None = 官方 OpenAI 端点
    "batch": 256,          # 单次请求最多向量化多少条
}
SIMILAR_TOP_K = 5          # 每个产品保存几个相似产品
SIMILAR_MIN_SCORE = 0.0    # 相似度低于此不收录（0 = 不过滤）
