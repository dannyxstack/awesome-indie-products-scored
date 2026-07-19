# awesome-indie-products · 独立开发者商机分析

自动采集独立开发者的产品/程序员副业/一人公司 OPC 项目，用 AI 从 5 个维度评估每个项目的商业机会并打分，
生成可复现的 Markdown 报告。下方为**最新一月的结果**；完整架构与使用方式见
**[技术方案说明](PROJECT.md)**。

## 数据来源

- **GitHub 独立开发者榜单**：如 [1c7/chinese-independent-developer](https://github.com/1c7/chinese-independent-developer) 等 README 项目列表。
- **V2EX 创意节点**：通过 V2EX 官方 API 采集「创意」节点的产品自荐主题。
- **任意 markdown 榜单**：交给 AI 抽取，适配陌生排版（可扩展新增来源）。

多来源按规范化 URL **跨来源去重**，同一产品只保留一份。

## 工作原理

```
多来源采集 → AI 5 维度打分(0-100) → 落库 SQLite → 幂等生成报告
```

- **5 个维度**：需求、竞争、成本、变现、执行难度；综合机会分由 5 维计算并归一化到 0-100（全库统一基准，跨报告一致）。
- **增量 & 幂等**：已打分的「项目×平台」自动跳过、不重复付费；报告纯查库生成，同库同结果、可反复重跑。

<!-- REPORTS:START -->

## 📊 最新一月结果（2026-07）

> 生成时间：2026-07-19 22:06 ｜ 本月已评分 126 个，按综合机会分降序

| 项目 | 一句话介绍 | 需求指数 | 竞争度 | 成本指数 | 变现预估 | 执行+推广难度 | 综合机会分 |
|---|---|---|---|---|---|---|---|
| [大字白板](https://big-font-hero.pages.dev/) | 跟听障老人交流的小程序，将输入文字放大展示方便老人阅读，支持横竖屏、语音输入和交流历… | 40 | 10 | 20 | 20 | 30 | 80 |
| [Listlift](https://listlift.dev) | 面向 Etsy 卖家的内容引擎，将自有商品 Listing 转成符合卖家口吻、可审核… | 60 | 30 | 20 | 50 | 40 | 75 |
| [Loomet](https://loomet.app/) | 网页端串珠图案制作工具，支持图片导入、精准珠子用量统计、真实珠子预览、手机端 Bui… | 40 | 20 | 30 | 50 | 40 | 75 |
| [SeatView](https://seat.genchi.top) | 日本及部分海外演唱会场馆的真实座位视角图集，在坐席图上点击标注即可查看该位置的实拍视… | 60 | 20 | 30 | 40 | 50 | 72 |
| [KinMate](https://kinmate.elolin.com) | 本地优先的家庭健康档案库，把全家人（含宠物）的化验单、病历、体检报告集中安全地存在自… | 70 | 30 | 40 | 50 | 60 | 58 |
| [SignalTo](https://signalto.io/) | TradingView webhook 提醒转发工具，将策略警报自动发送到 Tele… | 70 | 60 | 30 | 75 | 50 | 52 |
| [咖啡奶茶喝什么](https://nckfhsm.com/) | 收录国内主流连锁咖啡奶茶品牌饮品和门店数据，小程序版可打卡记录评分 | 70 | 60 | 20 | 40 | 30 | 47 |
| [Stub Lab](https://stub-lab.terenzzzz.cn/) | 浏览器里运行的票根生成工具，上传照片配上标题、日期和编号即可做出可导出的纪念票根 | 30 | 20 | 10 | 20 | 20 | 45 |
| [SolDrop Tracker](https://soldrop-tracker.vercel.app) | Solana 空投追踪工具，链上钱包分析，自动检测协议交互记录并判断空投资格，无需注… | 60 | 40 | 30 | 50 | 50 | 45 |
| [Image to Editable Diagram](https://imagetoeditable.com/) | 将图表截图、白板照片转换为可编辑的 Draw.io、Mermaid 或 Excali… | 60 | 40 | 30 | 50 | 50 | 45 |
| [BiliLike-Counter](https://github.com/xxdz-Official/BiliLike-Counter) | 浏览器油猴脚本，一键统计 B 站账号各种点赞数据，直观展示账号获赞总量 | 30 | 10 | 10 | 10 | 20 | 45 |
| [GeoMock](https://geomock.com/zh) | 全球地址生成器，覆盖美国免税州等 40+ 国家，生成地址、姓名、电话和邮箱，支持复制… | 30 | 20 | 10 | 20 | 20 | 45 |
| [IELTS Writing Checker](https://ieltswritingchecker.org/) | 雅思作文批改和辅导 | 80 | 70 | 40 | 75 | 60 | 43 |
| [EasyLaunch](https://easylaunch.aimos.cloud/) | 能力产品化平台，把专家方法论和 AI Skill 一键上线成带登录、收款与数据统计的… | 70 | 60 | 40 | 60 | 50 | 42 |
| [ieltssh](https://ieltssh.com/) | 基于 AI 的雅思口语素材库，定制个人专属素材 | 70 | 60 | 30 | 60 | 50 | 42 |
| [upload](https://upload.one) | 跨 AI 的长期记忆层，让 ChatGPT、Claude、Codex、Hermes、… | 75 | 60 | 40 | 70 | 65 | 40 |
| [SkillTry](https://skilltry.aimos.cloud/) | 电商 AI Skill 服务市场，按次调用视频、选品、Listing、广告诊断等薄服… | 70 | 60 | 40 | 65 | 60 | 38 |
| [SaaSCity](https://saascity.io) | 免费提交 SaaS 产品，每个产品会变成等距城市地图上的一栋建筑，24 小时内人工审… | 30 | 20 | 20 | 40 | 50 | 36 |
| [卡网大全 · CardNav](https://cardnav.xyz) | 一站式 AI 大模型账号购买导航，聚合中转站、卡网、官方订阅比价、模型排行、使用指南… | 70 | 60 | 30 | 50 | 50 | 35 |
| [OkkMax](https://www.okkmax.com/) | AI API 中转站评测与监测工具，聚合模型纯度、在线率、延迟、价格、用户点评和福利… | 75 | 60 | 30 | 50 | 55 | 34 |
| [薪跳 PayDance](https://paydance.vercel.app/) | “实时工资”小软件，轻量优雅，可基于用户的薪资和上下班时间动态计算每一秒的收入增长，… | 30 | 20 | 10 | 15 | 20 | 34 |
| [澄镜塔罗](https://chengjingtarot.xyz/) | 沉浸式在线塔罗占卜网站，按问题类型进入 Silver、Flower、Cathedra… | 60 | 70 | 30 | 50 | 40 | 32 |
| [记账tracker](https://claw.investtracker.ai) | 投资记账与持仓复盘工具，分开呈现持仓浮盈亏和已实现盈亏，支持组合视图、微信小程序、开… | 60 | 70 | 30 | 50 | 40 | 32 |
| [AudienceCue](https://audiencecue.com/zh/tools/youtube-comment-downloader) | YouTube 公开视频评论下载和受众分析工具，粘贴视频或 Shorts 链接即可导… | 60 | 70 | 20 | 50 | 40 | 32 |
| [BGChanger - AI 视频背景移除与换脸](https://bgchanger.video) | 在浏览器中一键替换或移除视频背景，支持高精度 AI 换脸与基础视频剪辑，无需安装客户… | 85 | 80 | 60 | 70 | 70 | 32 |
| [一字成名](https://www.congta.com/app/naming) | 给宝宝起名的微信小程序，集成国学起名、诗词取名、AI 取名，支持候选集功能和家人投票 | 70 | 80 | 20 | 60 | 50 | 32 |
| [Passport Size Photo](https://passportsizephoto.net) | 在线证件照制作工具，上传照片后选择国家/证件预设，预览尺寸、背景和人脸裁剪，下载数字… | 80 | 90 | 20 | 70 | 60 | 31 |
| [BigBanana-AI-Director](https://github.com/shuyu-labs/BigBanana-AI-Director) | AI 短剧 / AI 漫剧 / AI 导演平台，工业级一站式生产工具，面向创作者；采… | 75 | 60 | 80 | 70 | 85 | 31 |
| [AgentCeres](https://agentceres.com) | 给独立开发者和出海产品的 AI 增长团队，自动做竞品研究、起草 SEO 文章与社媒帖… | 65 | 70 | 40 | 60 | 55 | 30 |
| [Haven](https://havenai.cn/) | vibe coding 部署平台，上传 ZIP 或连接 GitHub/Gitee，A… | 70 | 60 | 40 | 65 | 75 | 30 |
| [RetroWin](https://retrowin-site.pages.dev/) | 在 Mac 上还原 Windows 98/XP/7/8.1/10 经典任务栏 | 20 | 10 | 20 | 15 | 30 | 30 |
| [野果子](https://www.yeguozi.com) | 电影家居美学灵感库，从精选剧照提取墙面软装配色参考，支持按色彩浏览和配色长图分享，覆… | 40 | 30 | 20 | 30 | 40 | 30 |
| [AI 小说作家 / AI Novel Writer](https://github.com/EthanYoQ/AI-Novel-Writer) | 中文小说与网文写作桌面工作台，支持大纲、角色、章节蓝图、审稿修稿和知识库管理；内置完… | 70 | 60 | 40 | 50 | 60 | 29 |
| [轻语输入 / Whisper Input](https://github.com/EthanYoQ/whisper-input/releases/latest) | Windows 开源 AI 语音输入 App，按全局快捷键说话即可把中文整理成去口头… | 70 | 60 | 40 | 50 | 60 | 29 |
| [璞奇](https://www.zendong.com.cn) | 将书本、B 站、得到等学习内容生成练习，帮助掌握新知，支持 App、Chrome 插… | 70 | 60 | 40 | 50 | 60 | 29 |
| [Atomi](https://atomi.chat) | AI 工具与数字服务的验证交易市场——沙箱执行，回执为凭，验后放款 | 40 | 30 | 60 | 50 | 70 | 29 |
| [MeshRefinery](https://meshrefinery.com/) | 在浏览器中修复、转换和优化 3D 文件，免费使用，文件不离开本地设备 | 70 | 60 | 30 | 40 | 50 | 28 |
| [TranAI](https://tranai.app/) | 聚合海外主流应用的多开翻译器，支持沉浸式翻译、有道/百度/Google/DeepL/… | 70 | 80 | 40 | 60 | 60 | 26 |
| [GPTGeminiGrok.AI](https://trygrokai.asia/list/#/home) | Grok / SuperGrok 为主的 AI 模型服务入口，同时提供 GPTPlu… | 70 | 80 | 30 | 60 | 60 | 26 |
| [WebCode](https://github.com/shuyu-labs/WebCode) | AI 编程平台，基于浏览器运行，支持远程运行 Claude Code 和 Codex… | 75 | 80 | 40 | 60 | 70 | 24 |
| [秒折立方](https://foldcube.cn/) | 专治行测/公考图形推理里的立体空间题，平面展开图点一下就折成正方体，相对面、相邻面自… | 40 | 20 | 30 | 20 | 50 | 24 |
| [Dramily](https://dramily.com) | 一站式真人短剧生成工厂 | 70 | 60 | 80 | 50 | 75 | 23 |
| [Seedance 2.5](https://seedance25ai.im) | 字节跳动推出的 AI 视频生成器，输入提示词生成原生 4K 画质、时长达 30 秒的… | 95 | 90 | 95 | 70 | 95 | 23 |
| [ghost-proxifier-pro](https://ghostproxifier.com) | 专为 Windows 打造的免费进程级透明代理引擎，拖拽进程快捷方式即可完成注入，支… | 30 | 20 | 20 | 20 | 40 | 22 |
| [玻璃涂鸦](https://glaspen2.liuluopeng.site) | 全屏标记软件，屏蔽数位笔默认鼠标行为，实现在显示器前加了一面玻璃做笔记 | 30 | 20 | 30 | 20 | 40 | 22 |
| [claude-i18n](https://chromewebstore.google.com/detail/claude-i18n/fkfmbjccelbeolkoekeaegajhhdndajj) | [Claude.ai](https://claude.ai) 网页端简体中文 / 繁… | 30 | 20 | 10 | 10 | 20 | 22 |
| [Beancount-Trans](https://trans.dhr2333.cn/) | 上传账单，自动转换为可审计的 Beancount 复式记账数据，并在几分钟内查看财务… | 30 | 20 | 30 | 20 | 40 | 22 |
| [Vivify 实时视频换脸](https://vivify.video/zh/realtime-face-swap) | AI 实时视频换脸，支持一键换脸、变装和风格重绘 | 70 | 80 | 60 | 60 | 70 | 22 |
| [Image Clipboard](https://www.imageclipboard.xyz/) | 免费网页工具，搜索、保存和复制 Discord emoji / sticker 图片… | 30 | 20 | 10 | 10 | 20 | 22 |
| [oh-my-ppt](https://www.ohmyppt.cc/) | 描述你的需求（演示、课程或故事），AI 为你生成简洁美观的 HTML 幻灯片，本地优… | 70 | 80 | 30 | 50 | 60 | 22 |
| [AI 信息差](https://news.maynorai.asia/) | AI 产品解读站，聚焦模型横测、AI 图片生成 SaaS、提示词工作流和深度评测 | 70 | 80 | 30 | 50 | 60 | 22 |
| [MythPen](https://github.com/niyongsheng/mythpen) | 桌面端 AI 辅助小说创作工具，管理角色、世界观、章节、伏笔和时间线等写作要素 - … | 60 | 70 | 40 | 50 | 60 | 21 |
| [PicText - 图片文字编辑器](https://imagetexteditor.net/) | AI 驱动的图片文本编辑器，检测并替换照片、截图和产品图中的文本，同时保留原始布局和… | 60 | 70 | 40 | 50 | 60 | 21 |
| [ImgToSTL](https://imgtostl.com/) | 面向 3D 打印的 AI 图片转 STL 转换器 | 60 | 70 | 40 | 50 | 60 | 21 |
| [MusicAura AI](https://musicaura.ai) | AI 音乐生成器，把情绪、场景、歌词或文字提示变成原创歌曲和背景音乐，支持试听和下载 | 70 | 85 | 60 | 65 | 75 | 21 |
| [独立淘金地图](https://berich.aichi.food) | 面向小白的赚钱路子汇总，整合一个人也能做的独立创收机会 | 70 | 80 | 30 | 40 | 50 | 21 |
| [CraftMusic AI](https://craftmusic.ai/) | AI 音乐和歌词生成器，从提示词、歌词想法或项目需求生成歌曲与纯音乐，支持风格控制、… | 70 | 80 | 60 | 60 | 75 | 21 |
| [猿音（Primuse）](https://apps.apple.com/cn/app/%E7%8C%BF%E9%9F%B3/id6761675450) | 面向自建音乐库的 Apple 多端音乐播放器，把 NAS、云盘、本地文件和自托管媒体… | 60 | 70 | 30 | 40 | 50 | 21 |
| [InvoiceFlowAI](https://github.com/EthanYoQ/Invoice-Downloader/releases/tag/v2026.07.12.1) | Windows 发票归档 App，连接 QQ / 163 邮箱批量下载 PDF、OF… | 60 | 70 | 30 | 40 | 50 | 21 |
| [Chaty](https://chaty.ca) | 本地 AI 助手桌面应用（Windows / macOS），大模型在自己电脑上运行，… | 70 | 60 | 50 | 40 | 70 | 20 |
| [嘶好冷](http://8.134.62.33:8000/) | 每日一则冷笑话，附 Android 客户端 - [更多介绍](https://git… | 20 | 10 | 10 | 5 | 15 | 20 |
| [耳虫日记](https://github.com/WatanabeChika/EarwormDiary/releases) | 记录每日脑海中循环的“耳虫”旋律，支持单日多首记录、可视化专辑封面日历和本地离线无账… | 20 | 10 | 20 | 10 | 30 | 20 |
| [ShangBackground](https://github.com/xxdz-Official/ShangBackground) | Windows 桌面右键壁纸管理工具，实现"上一个桌面背景"的右键菜单，并且有多种壁… | 20 | 10 | 20 | 10 | 30 | 20 |
| [小米设备价格天梯 & 代号速查](https://beihai10078.github.io/xiaomi-price-tier/) | Xiaomi / Redmi / POCO 设备价格天梯与代号速查工具，覆盖 245… | 20 | 10 | 10 | 5 | 15 | 20 |
| [iOS 截图装饰](https://app-shots.aibit.im/) | 免费在线 iOS 截图美化生成器，在浏览器中把应用截图变成规范的 App Store… | 60 | 70 | 20 | 30 | 40 | 19 |
| [Aural](https://aural-ai.com) | 开源 AI 面试平台，支持语音、聊天和视频面试，提供自适应追问、结构化评分、面试练习… | 70 | 80 | 60 | 50 | 70 | 19 |
| [小野AI](https://xiaoye.io/) | 开源多模态 AI 内容创作平台，支持 Gemini、Seedream、Seedanc… | 70 | 80 | 60 | 50 | 70 | 19 |
| [GrokTask](https://trygroktask.asia/) | 基于 Grok AI 的智能任务自动化平台，支持定时任务、AI 自动执行、信息收集与… | 60 | 70 | 50 | 50 | 70 | 18 |
| [历史人物传记](https://www.congta.com/biog) | 可视化网站，基于中国历史人物传记数据库（CBDB）构建，包括历史人物信息、人际关系图… | 30 | 20 | 40 | 20 | 50 | 18 |
| [归灯](https://guideng.vercel.app) | 家庭位置共享 App，支持 Android、iOS 和自托管服务器 | 30 | 20 | 30 | 20 | 50 | 18 |
| [IPTV Player](https://iptv.aibit.im/zh) | 收看世界各地新闻、体育和娱乐节目（超过一万个频道），无需注册、下载或订阅 | 70 | 80 | 30 | 40 | 60 | 18 |
| [Orkas](https://orkas.ai?source=github) | AI 团队桌面 App，开源、本地优先，通过对话下达目标，由指挥官协调专业 Agen… | 70 | 80 | 60 | 50 | 75 | 18 |
| [CloudSSH](https://ssh.newbietan.cn) | 打开浏览器即可连接和管理自己的所有服务器，连接信息云端同步，内置 SFTP 文件管理… | 70 | 80 | 30 | 40 | 60 | 18 |
| [seedance 2.0 mini](https://seedancemini.online) | 浏览器直出 AI 视频，文字/图片/音频多模态输入，30 秒内生成 HD 短片，无需… | 70 | 80 | 60 | 50 | 75 | 18 |
| [Image Prompt Generator](https://image-prompt-generator.com/) | 免费 AI 图像提示词生成器和提示词库，支持多模型筛选和提示词生成 - [更多介绍]… | 70 | 80 | 30 | 40 | 60 | 18 |
| [SmartRSS](https://vinsonguo.github.io/introducing-smartrss) | 全平台 RSS 阅读器，无缝集成 FreshRSS 等服务，AI 自定义指令帮你高效… | 60 | 70 | 30 | 40 | 60 | 17 |
| [email signature generator](https://email-signature-generator.online/) | 免费的专业邮件签名在线生成器 | 60 | 80 | 20 | 30 | 40 | 17 |
| [MkImage](https://mkimage.ai) | AI 生图工具站，内置 1000+ 优质提示词，支持 GPT Image 和 Nan… | 70 | 85 | 60 | 50 | 75 | 16 |
| [Musefy - AI 音乐制作](https://music-generator.net) | 将提示词转化为 AI 歌曲、歌词和背景音乐 | 70 | 85 | 60 | 50 | 75 | 16 |
| [Gptimage2](https://gptimage2.asia/) | AI 图片生成工具 | 70 | 85 | 60 | 50 | 75 | 16 |
| [历史图轴](https://www.congta.com/maptime) | 历史时间轴与地图的结合，把通史/断代史/历史人物、时间、地图联动起来，有网页版和微信… | 40 | 30 | 30 | 20 | 50 | 16 |
| [上海City不City](https://shanghaicitycity-web.havenai.online/) | 上海城市玩法发现站，按地点和主题搜索路线，也可用 AI 规划约会、亲子、夜景等 Ci… | 40 | 30 | 30 | 20 | 50 | 16 |
| [Sillage](https://github.com/ZingLix/Sillage/blob/main/README.zh-CN.md) | 把足迹、火车、飞机、酒店放在一起记录的旅行 App，可按时间轴与照片一起回放探索过程… | 40 | 30 | 30 | 20 | 50 | 16 |
| [Text Tray](https://github.com/Jingyuan-Zheng/TextTray) | 原生 macOS 临时文本托盘，无需打开完整文本编辑器即可快速查看、编辑、清理、统计… | 40 | 30 | 20 | 20 | 50 | 16 |
| [AI YouTube Transcript](https://aiyoutubetranscript.com/) | 无需注册的 YouTube 转录工具，可搜索 transcript、跳转时间戳，并导… | 70 | 80 | 20 | 30 | 50 | 16 |
| [otpbox](https://github.com/adra2n/otpbox) | Android 两步验证认证器，注重隐私与安全，支持端到端加密同步 - [更多介绍]… | 60 | 70 | 30 | 30 | 50 | 15 |
| [AniShelf](https://apps.apple.com/us/app/anishelf/id6759359144) | 免费 iOS 追番管理工具，集中管理番剧和动画电影，记录观看状态、日期与感想，查看剧… | 60 | 70 | 20 | 30 | 50 | 15 |
| [Fork & Pour](https://fork-and-pour.terenzzzz.cn/) | 把鸡尾酒配方当作代码协作的开源项目，用 JSON 管理配方、用 PR 贡献内容、前端… | 20 | 10 | 20 | 10 | 40 | 15 |
| [xxdz-Itoc](https://github.com/xxdz-Official/xxdz-Itoc) | 可视化 Crazy Error 真程序制作软件，全球首款，基础部分无需编程，导入 M… | 20 | 10 | 30 | 15 | 60 | 15 |
| [biliJiyin](https://github.com/xxdz-Official/biliJiyin) | 浏览器油猴脚本，改造 B 站收藏夹播放列表页，调整为音乐列表播放器，且做了性能优化、… | 30 | 20 | 10 | 10 | 30 | 15 |
| [回音堂](https://anachron.qizhen.xyz/) | 借助 AI，用对话的方式讲述历史故事 - [更多介绍](https://github… | 30 | 20 | 40 | 20 | 60 | 15 |
| [Agent Island](https://agent-island.dev/) | Claude Code 与 Codex 的开源状态伴侣，在 macOS 和 Wind… | 30 | 20 | 20 | 10 | 30 | 15 |
| [MarkIt](https://chromewebstore.google.com/detail/markit-%E7%BD%91%E9%A1%B5%E6%A0%87%E6%B3%A8%E4%B8%8E%E5%8F%8D%E9%A6%88%EF%BC%8C%E8%AE%A9-ai-%E5%B0%91%E7%8C%9C%E4%B8%80%E7%82%B9/dndiinkkhpmdipaffabjkaagoogjlome) | 在网页上圈选元素、截图并写需求，生成含页面位置、元素信息和验收标准的结构化反馈 | 40 | 60 | 20 | 30 | 40 | 15 |
| [TestHive](https://testhive.elolin.com) | 面向开发者的众测/内测市场，发布测试活动即可招募真实用户帮你试用挑 bug；测试者完… | 60 | 70 | 50 | 40 | 70 | 15 |
| [WillowTab](https://chromewebstore.google.com/detail/willowtab/gfigaeaddejhmnlkeppgccklahgepapm) | 极简浏览器新标签页扩展，支持多搜索引擎切换、本地壁纸、深浅色主题和外观自定义，无需账… | 50 | 70 | 20 | 20 | 30 | 14 |
| [轻屿课表](https://mutx.ccwu.cc) | Android 校园课表 App，深度对接 HyperOS 超级岛与焦点通知，支持 … | 70 | 60 | 30 | 20 | 50 | 14 |
| [ToolGarden](https://toolgarden.xyz) | 全能工具箱，免费在线，包含 JSON、PDF、图片、二维码、信息编解码、字幕制作等常… | 70 | 90 | 20 | 30 | 50 | 14 |
| [Mindwtr](https://mindwtr.app) | 本地优先的 GTD 待办 App，几秒收集脑中的任务和想法，再通过整理、执行和每周回… | 60 | 80 | 20 | 30 | 50 | 14 |
| [HN 每日精选](https://pageslabs.com/zh) | 每日更新 Hacker News 热门话题和讨论，支持多语言 | 40 | 60 | 20 | 20 | 30 | 13 |
| [Tono](https://tonote.app/) | 极简 Android 待办与笔记 App，打开即记，想法和任务一处捕捉、永不丢失 | 70 | 80 | 20 | 30 | 60 | 13 |
| [Moler](https://github.com/niyongsheng/moler) | Mac 磁盘清理工具，NASA-Punk 风格，支持重复文件扫描、大文件检测、应用卸… | 60 | 80 | 30 | 40 | 70 | 13 |
| [玉兔远程控制](https://github.com/KangLin/RabbitRemoteControl/releases/latest) | 开源跨平台远程管理 App，支持远程桌面、文件传输、SSH、TELNET、RDP 和… | 70 | 85 | 40 | 30 | 60 | 12 |
| [AFTERSHOT](https://aftershot.terenzzzz.cn/) | 在浏览器中复盘照片的技术与审美表现，含直方图、EXIF、美学评分、视觉显著性与 HD… | 40 | 60 | 30 | 30 | 50 | 12 |
| [拼图编辑器 Puzzle Builder](https://github.com/jaychouchannel/Front-Pattern) | 纯前端零依赖的可视化拼图低代码编辑器，在画布上拖拽矩形即可创建文本/图片/视频/按钮… | 40 | 60 | 20 | 30 | 50 | 12 |
| [Google Trends Explorer](https://keywords.aibit.im/zh/) | Google 趋势关键词词根探索器，从 38 个行业 800+ 精选关键词中挑选短词… | 40 | 60 | 20 | 30 | 50 | 12 |
| [TrendingAI](https://trendingai.cn/app/) | 海外技术热点中文情报站，AI 每日从 GitHub Trending、Hacker … | 40 | 60 | 30 | 30 | 50 | 12 |
| [AppRank](https://apprank.aibit.im) | 查看 App Store 各国 App 排行榜，汲取爆款 App 思路，支持搜索任意… | 40 | 60 | 20 | 30 | 50 | 12 |
| [Onin](https://github.com/b-yp/Onin) | macOS 应用启动器，支持应用启动、文件搜索和命令执行，全程无需离开键盘 - [更… | 60 | 80 | 20 | 30 | 60 | 11 |
| [Nimclip](https://hukdoesn.github.io/Nimclip/) | macOS 剪贴板历史工具，免费开源、本地优先，支持文本、链接、代码、图片和富文本历… | 60 | 80 | 20 | 20 | 40 | 11 |
| [黄油单词](https://waiyuka.cc) | 在线背单词工具，免费，每张单词卡配有 AI 插图、单词发音和例句朗读，支持西班牙语、… | 60 | 80 | 30 | 30 | 60 | 11 |
| [Agnes 视频生成器](https://video.lichuanyang.top/zh/demo) | AI 视频生成工作流，完全免费，基于 agnes 视频模型，无需本地 GPU，可网页… | 70 | 80 | 60 | 30 | 75 | 10 |
| [MediaInsight](https://www.mediainsight360.com/) | 在线媒体格式解析工具，支持 MP4、MKV、AVI 等格式和 H264、H265、A… | 40 | 70 | 30 | 30 | 50 | 10 |
| [AI Buddy](https://chromewebstore.google.com/detail/eigpaeoigklelmfgnkljhbjjbpohenpn) | Chrome 侧边栏 AI 助手，选中文本或截图直接提问，自定义快捷键和提示词，支持… | 70 | 85 | 20 | 20 | 50 | 10 |
| [谷物OJ](http://guwu.camluni.cn:3001) | 在线评测平台，支持多语言自动评测和竞赛功能 | 60 | 80 | 40 | 30 | 70 | 10 |
| [Markra](https://editor.markra.app/) | 所见即所得 Markdown 编辑器，本地优先、开源，支持 Web、macOS、Wi… | 50 | 80 | 30 | 30 | 60 | 9 |
| [Synthesizer Flow](https://synthesizer-flow.misakif.uk/) | 浏览器端模块化合成器，通过可视化节点和连线搭建音频工作流，支持实时声音合成、MIDI… | 40 | 70 | 30 | 30 | 60 | 9 |
| [BrowSync](https://browsync.ct106.com) | macOS 跨浏览器书签、标签页与浏览状态实时同步工具 | 40 | 60 | 30 | 30 | 70 | 9 |
| [微信 PGP 加密助手](https://github.com/619dev/weixin_e2ee_crypt/releases/latest) | 在微信等即时通讯 App 中通过悬浮窗加密和解密 PGP 消息，密钥与加解密操作保留… | 10 | 5 | 20 | 5 | 40 | 8 |
| [123pan](https://github.com/123panNextGen/123pan/releases/latest) | 开源第三方 123 云盘桌面客户端，支持 Windows 和 Linux，提供文件管… | 40 | 70 | 30 | 20 | 50 | 7 |
| [ExcaliRec](https://excalirec.com/) | 浏览器白板录屏工具，面向 Excalidraw 风格讲解视频，支持自动聚焦缩放和本地… | 30 | 60 | 20 | 20 | 50 | 6 |
| [FocuSD Island](https://github.com/zzliu93-debug/FocuSD/releases/latest) | Windows 桌面悬浮灵动岛效率工具，把待办、每日笔记、剪贴板历史、媒体控制和 C… | 30 | 60 | 20 | 20 | 50 | 6 |
| [PaperPhonePlus](https://paperphone.app) | 支持端到端加密、前向保密和音视频通话的即时通讯 App，可使用官方网页端或自托管 | 40 | 70 | 30 | 20 | 60 | 6 |
| [F-Curator](https://xizon.github.io/F-Curator-Official-Website/) | 跨平台网络收藏夹管理 App，支持 Mac 和 Windows，永久保存数据，可在 … | 30 | 70 | 20 | 20 | 60 | 4 |
| [AiSiteLink](https://www.aisitelink.com/) | 传统网址导航与 AI 网址导航结合，注册后可自定义个人导航网站 | 30 | 70 | 20 | 20 | 60 | 4 |
| [问墨](https://github.com/619dev/wenmo-android/releases/latest) | 完全离线的 Android 中文输入法，不申请网络或录音权限，APK 约 1.3 M… | 30 | 60 | 20 | 10 | 40 | 4 |
| [抛骰子](https://wheelpage.com/dice-roller/) | 3D 抛骰子网站，支持多种类型骰子 | 20 | 80 | 10 | 10 | 30 | 2 |

## 📁 完整报告
- 最新每日报告：[reports/daily/2026-07-19.md](reports/daily/2026-07-19.md) ｜ [全部每日](reports/daily/)
- 全量排行 Top100：
  - [需求指数最高](reports/rankings/demand-top100.md)
  - [竞争度最低（最蓝海）](reports/rankings/competition-top100.md)
  - [成本指数最低（最省钱）](reports/rankings/cost-top100.md)
  - [变现预估最强](reports/rankings/monetization-top100.md)
  - [执行+推广难度最低（推广最友好）](reports/rankings/execution-top100.md)
- 月度全量报告：[reports/monthly/2026-07.md](reports/monthly/2026-07.md) ｜ [全部月度](reports/monthly/)

<!-- REPORTS:END -->

---

> 架构总览、模块职责、多来源适配、定时自动化与命令行用法，详见 **[技术方案说明](PROJECT.md)**。
