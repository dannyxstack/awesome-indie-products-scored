# awesome-indie-products · 商机可行性自动分析

自动抓取 [中国独立开发者项目列表](https://github.com/1c7/chinese-independent-developer) 的 README，
用多个 AI 平台从 5 个维度对每个项目的商业机会打分，生成 Markdown 报告并提交到本仓库。

## 分析维度（0-100，越高越有利于商业机会）

| 维度 | 100 分 | 0 分 |
|---|---|---|
| 需求量 demand | 需求巨大、受众广 | 几乎无人需要 |
| 竞争宽松度 competition | 蓝海、几乎无竞争 | 红海、巨头林立 |
| 成本可控度 cost | 近乎零成本可做 | 需巨额投入 |
| 变现能力 monetization | 变现路径清晰强劲 | 极难变现 |
| 执行难易度 execution | 技术+获客(SEO/GEO)都容易 | 极难 |

各平台分数**分别列出、不跨平台融合**。

## 目录结构

```
scripts/
  config.py      数据源、POC 范围、AI 平台配置
  scraper.py     抓取 raw README
  parser.py      Markdown -> 结构化项目
  prompts.py     5 维度打分 prompt
  analyzer.py    OpenAI 兼容客户端(gpt/deepseek 共用) + dry-run
  cache.py       按(项目,平台)去重防重复付费
  renderer.py    生成 Markdown 报告
  publisher.py   本地 git 提交(不 push)
  run.py         主编排入口
data/
  projects.json      解析出的项目
  scores/<平台>.json  各平台打分(累积)
  analyzed_cache.json 已分析记录
output/report.md     最终报告
```

## 使用

> **Python 环境**：本项目统一使用 conda 环境 `awesome-indie-products`（详见 CLAUDE.md）。
> 下面命令用 `conda run -n awesome-indie-products` 显式指定；也可先 `conda activate awesome-indie-products` 再运行。

```bash
conda run -n awesome-indie-products pip install -r requirements.txt
cp .env.example .env         # 填入 DEEPSEEK_API_KEY / OPENAI_API_KEY
```

### 方式一：本地管理界面（推荐）

```bash
conda run -n awesome-indie-products streamlit run scripts/app.py
```

浏览器打开后：① 浏览/搜索/筛选项目 → ② 选范围勾选平台跑分(带进度条) →
③ 各平台并列看评分和理由 → ④ 生成报告预览并一键本地提交。

### 方式二：命令行

```bash
conda run -n awesome-indie-products python scripts/run.py --dry-run   # 模拟全链路，无需 key
conda run -n awesome-indie-products python scripts/run.py             # 增量分析 POC 范围(默认最近 30 个)并出报告
conda run -n awesome-indie-products python scripts/run.py -n 10       # 指定数量
conda run -n awesome-indie-products python scripts/run.py --refresh   # 重新抓取解析 README
conda run -n awesome-indie-products python scripts/run.py --full      # 分析全部项目(调用量巨大，谨慎)
```

- **增量**：`analyzed_cache.json` 记录已分析的 (项目, 平台)，重复运行只补缺，不重复付费。
- **提交**：`python publisher.py` 做本地 `git commit`（**不 push**，推送需手动确认）。
