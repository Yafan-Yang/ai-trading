# ai-trading · 多智能体选股分析 Skill

[![skills.sh](https://skills.sh/b/Yafan-Yang/ai-trading)](https://skills.sh/Yafan-Yang/ai-trading)

把「多智能体辩论式选股分析」做成**只装 skill 就能全局使用**的 Claude Code 命令集。
零数据库、零 API key、全免费数据源（akshare + yfinance），覆盖 **A股 / 港股 / 美股**。

> ⚠️ **免责声明**：本项目仅用于研究和教育目的，**不构成任何投资建议**。AI 预测存在不确定性，投资有风险，决策需谨慎，请咨询专业财务顾问。

## ✨ 特性

- **多智能体流水线**：五分析师并行 → 多空辩论 → 交易员提案 → 风险三方辩论 → 风险经理拍板，产出结构化研报。
- **真实数据**：akshare（A股/港股）+ yfinance（美股），stockstats 计算技术指标；带取数重试与当日缓存。
- **数字严谨**：关键估值用 `decimal.Decimal` 校验，杜绝 LLM 心算误差。
- **多平台支持**：兼容 Claude Code、Codex、Cursor、OpenCode、Windsurf 等 70+ 智能体。
- **全局可用**：安装后在任意项目里使用。
- **可选 PDF**：Markdown 研报可导出中文 PDF。

## 📦 安装

### 方式 1：使用 skills.sh CLI（推荐）

支持 70+ 智能体，一键安装到所有兼容平台：

```bash
# 从 GitHub 安装（需要先发布到 GitHub）
npx skills add Yafan-Yang/ai-trading

# 从本地安装（开发/测试）
git clone <your-repo-url> ai-trading
cd ai-trading
npx skills add .
```

支持的智能体包括：
- **Claude Code** (`.claude/skills/`)
- **Codex** (`.codex/skills/`)
- **Cursor** (`.agents/skills/`)
- **OpenCode** (`.agents/skills/`)
- **Cline** (`.agents/skills/`)
- **Windsurf** (`.windsurf/skills/`)
- 以及其他 60+ 智能体 → [完整列表](https://github.com/vercel-labs/skills#supported-agents)

### 方式 2：手动安装

如果不想使用 skills.sh CLI，可以手动安装到特定平台：

```bash
git clone <your-repo-url> ai-trading
cd ai-trading

# 自动检测并安装到所有可用平台
bash install.sh

# 或者指定安装到特定平台：
bash scripts/install-claude.sh      # 仅 Claude Code
bash scripts/install-codex.sh       # 仅 Codex
bash scripts/install-standard.sh    # 标准格式（兼容多平台）
```

**PDF 导出（可选）** 依赖系统图形库，macOS 首次需要：
```bash
brew install pango gdk-pixbuf libffi
```

## 🚀 使用方法

### 在 Claude Code 中

```bash
/ai-trading:analyze 600519         # 完整分析流水线
/ai-trading:quick AAPL             # 60秒快照
/ai-trading:market 0700.HK         # 技术面分析
```

### 在 Codex / Cursor / 其他智能体中

安装后，skills 会自动加载。你可以直接请求：

```
使用 ai-trading analyze 分析腾讯控股 (0700.HK)
```

或者在对话中自然地提及：
```
帮我用 ai-trading 的多智能体框架分析一下贵州茅台
```

## 📋 命令一览

| 命令 | 作用 |
|---|---|
| `analyze` | **一键完整流水线**，输出研报并落盘 |
| `quick` | 60 秒快照（单代理，无辩论） |
| `market` | 技术面分析师 |
| `fundamentals` | 基本面分析师（估值/合理价位） |
| `news` | 新闻面分析师 |
| `sentiment` | 社交情绪分析师 |
| `china` | A股专属视角（政策/资金/涨跌停） |
| `debate` | 多空辩论 + 研究经理结论 |
| `risk-panel` | 风险三方辩论 + 风险经理拍板 |

代码格式：A股 `600519`，港股 `0700.HK` / `9988`，美股 `AAPL`。

## 🛠️ 数据工具（可独立运行）

```bash
PY=~/.ai-trading/.venv/bin/python
$PY ~/.ai-trading/tools/market_data.py 600519 --json        # 行情+技术指标
$PY ~/.ai-trading/tools/fundamentals.py 600519 --json       # 财务+估值(PE/PB/ROE)
$PY ~/.ai-trading/tools/news_fetch.py 600519 --macro --json # 个股+宏观新闻
$PY ~/.ai-trading/tools/verify.py pe --price 1193 --eps 66  # 数字校验(Decimal)
$PY ~/.ai-trading/tools/export_pdf.py <report.md>           # 研报导出PDF
```

环境变量：`AITRADING_NOCACHE=1` 关闭当日缓存；`AITRADING_CACHE=<dir>` 自定义缓存目录。

## 🏗️ 项目结构

```
ai-trading/
├── .agents/skills/          # skills.sh 标准格式（兼容 70+ 智能体）
│   ├── analyze/
│   │   └── SKILL.md
│   ├── quick/
│   └── ...
│
├── codex-skills/            # Codex 专用格式
│   ├── analyze/
│   │   └── SKILL.md
│   └── ...
│
├── skills/                  # Claude Code 原生命令（源文件）
│   ├── analyze.md
│   ├── quick.md
│   └── ...
│
├── tools/                   # Python 数据工具
│   ├── market_data.py
│   ├── fundamentals.py
│   ├── news_fetch.py
│   ├── verify.py
│   └── export_pdf.py
│
├── scripts/                 # 安装与同步脚本
│   ├── sync-skills.py       # 从 skills/ 生成多平台格式
│   ├── install-claude.sh
│   ├── install-codex.sh
│   └── install-standard.sh
│
├── install.sh               # 统一安装入口
├── package.json             # skills.sh 元数据
├── requirements.txt         # Python 依赖
└── setup.sh                 # 虚拟环境设置
```

## 🔧 开发

```bash
# 在仓库内建 venv 并测试
bash setup.sh

# 对样本股(A/港/美)跑通各工具
bash smoke_test.sh

# 修改 skills/ 后重新生成多平台格式
python3 scripts/sync-skills.py
```

## 📤 发布到 skills.sh

1. **将项目推送到 GitHub**：
   ```bash
   git remote add origin https://github.com/Yafan-Yang/ai-trading.git
   git push -u origin main
   ```

2. **更新 package.json**：
   - 修改 `repository.url` 为你的仓库地址
   - 修改 `homepage` 为你的 GitHub 主页

3. **用户可以直接安装**：
   ```bash
   npx skills add Yafan-Yang/ai-trading
   ```

4. **（可选）提交到 skills.sh 目录**：
   - 访问 [skills.sh](https://skills.sh)
   - 项目会通过 GitHub 爬虫自动收录
   - 或者手动提交 PR 到 [vercel-labs/skills](https://github.com/vercel-labs/skills)

5. **添加徽章到 README**：
   ```markdown
   [![skills.sh](https://skills.sh/b/Yafan-Yang/ai-trading)](https://skills.sh/Yafan-Yang/ai-trading)
   ```

## 🌟 与 ai-berkshire 的差异化

| 维度 | ai-berkshire | ai-trading |
|------|-------------|------------|
| **投资流派** | 价值投资（巴菲特/芒格/段永平/李录） | 全方位投研（技术+基本+新闻+情绪） |
| **数据源** | 需配置多个付费源 | 100%免费数据（akshare+yfinance） |
| **市场覆盖** | 美股为主 | A股/港股/美股三市场 |
| **决策风格** | 10年确定性、镜子测试 | 多空辩论、风险三方、分层建议 |
| **技术特色** | 四大师对抗、强制决策 | 五分析师并行、流水线式辩论 |

## ⚠️ 已知限制

- 未实现记忆/反思（原项目 ChromaDB）机制，每次分析独立。
- 社交情绪、港股新闻依赖联网搜索补充（无稳定免费 API）。
- 免费数据源有频率限制与偶发波动；估值为工具化估算，非行情终端精度。
- 定位学习研究，**不提供实盘交易指令**。

## 📚 致谢与许可证

思想与流程源自 [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 及上游
[TradingAgents](https://github.com/TauricResearch/TradingAgents)（详见 [NOTICE](./NOTICE)）。
本项目代码独立编写，以 [Apache-2.0](./LICENSE) 许可证发布。

---

**优化路线图** → 查看 [OPTIMIZATION_PLAN.md](./OPTIMIZATION_PLAN.md) 了解未来改进方向（反偏见机制、护城河分析、持仓管理等）。
