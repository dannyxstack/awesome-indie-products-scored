# 技术方案说明 · awesome-indie-products

> 本项目的架构、模块、报告体系与使用方式说明。面向使用者的简介与最新结果见 [README.md](README.md)。

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
  config.py      数据源(按 type 配适配器)、POC 范围、AI 平台配置
  scraper.py     底层抓取(raw markdown / API)
  ids.py         URL 规范化 + 项目 ID(跨来源去重)
  sources.py     多来源采集适配器注册表(1c7 / v2ex / AI抽取)
  parser.py      1c7 版面格式解析
  extractor.py   AI 从任意 markdown 抽取项目
  state.py       更新检测(commit) + source_state
  prompts.py     5 维度打分 prompt
  analyzer.py    OpenAI 兼容客户端(gpt/deepseek 共用) + dry-run
  db.py          SQLite 存储层(projects + scores)，增量查库
  report.py      从 DB 幂等生成报告(每日/排行/月度) + README 索引
  publisher.py   本地 git 提交(不 push)
  run.py         主编排入口
data/
  analysis.db        SQLite：projects + scores（分析结果的唯一数据源）
  projects.json      最近一次采集解析出的项目
  source_state.json  已知项目ID + 各来源 commit(更新检测)
reports/
  daily/YYYY-MM-DD.md          每日报告(近3月最新10总览 + 5维度近3月Top10)
  rankings/<维度>-top100.md     5 个全量维度 Top100
  monthly/YYYY-MM.md           每月全量(增量)
.github/workflows/analyze.yml  定时自动分析并提交
```

## 报告体系（数据落库 + 幂等生成）

分析结果全部写入 SQLite（`data/analysis.db`），报告由 `report.py` 纯查询库生成——
**幂等**：同样的库跑出同样的 md，可反复重跑。每次 `run.py` 结束自动重生成：

- **每日报告** `reports/daily/YYYY-MM-DD.md`（按日归档）：近 3 个月最新 10 个项目综合评分总览
  + 5 个维度各取近 3 月 Top10，每块旁附「全量排名」链接。
- **全量排行** `reports/rankings/<维度>-top100.md` ×5：需求最高 / 竞争度最低 / 成本最低 /
  变现最强 / 难度最低，各 Top100。
- **月度全量** `reports/monthly/YYYY-MM.md`：按项目添加月份分组，每月一个文件，增量更新。
- 主 README 顶部「📊 分析报告」区自动维护到这些文件的链接。

## 多来源与自动更新

- **更新检测**：默认每次运行先用 GitHub commits API 检查 README 是否变化，无变化则用本地缓存；
  有变化才重新采集，并按项目 ID diff 出「本次新增」；结合库中已有打分（`db.has_score`）只分析新增。
- **多来源**：`config.SOURCES` 每项用 `type` 指定适配器——
  `1c7_readme`/`github_markdown`(同格式直接复用)、`v2ex_node`(V2EX 官方 API)、
  `github_md_ai`(任意格式 markdown 交给 AI 抽取)。跨来源按规范化 URL 去重。
- **定时自动化**：`.github/workflows/analyze.yml` 每天定时跑，检测更新→分析新增→生成报告→自动 commit。
  需在仓库 Settings → Secrets 配 `DEEPSEEK_API_KEY` / `OPENAI_API_KEY`。

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
# 注：conda run 在 Windows 中文控制台捕获输出会报编码错，故加 --no-capture-output 直接透传日志
conda run -n awesome-indie-products --no-capture-output python scripts/run.py --dry-run   # 模拟全链路，无需 key
conda run -n awesome-indie-products --no-capture-output python scripts/run.py             # 增量分析 POC 范围(默认最近 30 个)并出报告
conda run -n awesome-indie-products --no-capture-output python scripts/run.py -n 10       # 指定数量
conda run -n awesome-indie-products --no-capture-output python scripts/run.py --refresh   # 重新抓取解析 README
conda run -n awesome-indie-products --no-capture-output python scripts/run.py --full      # 分析全部项目(调用量巨大，谨慎)
```

- **增量**：库中已有真实打分的 (项目, 平台) 自动跳过，重复运行只补缺，不重复付费。
- **报告**：每次运行自动幂等生成到 `reports/`；也可单独 `python scripts/report.py` 只重生成报告。
- **提交**：`python scripts/publisher.py` 做本地 `git commit`（**不 push**，推送需手动确认）。
