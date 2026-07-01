# ai-trading · 多智能体选股分析 Skill

把「多智能体辩论式选股分析」做成**只装 skill 就能全局使用**的 Claude Code 命令集。
零数据库、零 API key、全免费数据源（akshare + yfinance），覆盖 **A股 / 港股 / 美股**。

> ⚠️ **免责声明**：本项目仅用于研究和教育目的，**不构成任何投资建议**。AI 预测存在不确定性，投资有风险，决策需谨慎，请咨询专业财务顾问。

## 特性

- **多智能体流水线**：五分析师并行 → 多空辩论 → 交易员提案 → 风险三方辩论 → 风险经理拍板，产出结构化研报。
- **真实数据**：akshare（A股/港股）+ yfinance（美股），stockstats 计算技术指标；带取数重试与当日缓存。
- **数字严谨**：关键估值用 `decimal.Decimal` 校验，杜绝 LLM 心算误差。
- **全局可用**：安装后在任意项目里 `/ai-trading:analyze 600519`。
- **可选 PDF**：Markdown 研报可导出中文 PDF。

## 安装（全局）

```bash
git clone <your-repo-url> ai-trading
cd ai-trading
bash install.sh
```

`install.sh` 会：
1. 把工具与依赖部署到 `~/.ai-trading/` 并创建独立 venv；
2. 把命令安装到 `~/.claude/commands/ai-trading/`，并把命令内的 `__AITRADING_HOME__` 占位符替换为工具家目录绝对路径。

可用环境变量自定义：`AITRADING_HOME`（工具家目录）、`CLAUDE_COMMANDS_DIR`（命令目录）。

**PDF 导出（可选）** 依赖系统图形库，macOS 首次需要：
```bash
brew install pango gdk-pixbuf libffi
```

## 命令一览

| 命令 | 作用 |
|---|---|
| `/ai-trading:analyze <代码>` | **一键完整流水线**，输出研报并落盘 |
| `/ai-trading:quick <代码>` | 60 秒快照（单代理，无辩论） |
| `/ai-trading:market <代码>` | 技术面分析师 |
| `/ai-trading:fundamentals <代码>` | 基本面分析师（估值/合理价位） |
| `/ai-trading:news <代码>` | 新闻面分析师 |
| `/ai-trading:sentiment <代码>` | 社交情绪分析师 |
| `/ai-trading:china <A股代码>` | A股专属视角（政策/资金/涨跌停） |
| `/ai-trading:debate <代码>` | 多空辩论 + 研究经理结论 |
| `/ai-trading:risk-panel <代码 [提案]>` | 风险三方辩论 + 风险经理拍板 |

代码格式：A股 `600519`，港股 `0700.HK` / `9988`，美股 `AAPL`。

## 数据工具（可独立运行）

```bash
PY=~/.ai-trading/.venv/bin/python
$PY ~/.ai-trading/tools/market_data.py 600519 --json        # 行情+技术指标
$PY ~/.ai-trading/tools/fundamentals.py 600519 --json       # 财务+估值(PE/PB/ROE)
$PY ~/.ai-trading/tools/news_fetch.py 600519 --macro --json # 个股+宏观新闻
$PY ~/.ai-trading/tools/verify.py pe --price 1193 --eps 66  # 数字校验(Decimal)
$PY ~/.ai-trading/tools/export_pdf.py <report.md>           # 研报导出PDF
```

环境变量：`AITRADING_NOCACHE=1` 关闭当日缓存；`AITRADING_CACHE=<dir>` 自定义缓存目录。

## 开发

```bash
bash setup.sh        # 在仓库内建 venv
bash smoke_test.sh   # 对样本股(A/港/美)跑通各工具
```

## 已知限制

- 未实现记忆/反思（原项目 ChromaDB）机制，每次分析独立。
- 社交情绪、港股新闻依赖联网搜索补充（无稳定免费 API）。
- 免费数据源有频率限制与偶发波动；估值为工具化估算，非行情终端精度。
- 定位学习研究，**不提供实盘交易指令**。

## 致谢与许可证

思想与流程源自 [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 及上游
[TradingAgents](https://github.com/TauricResearch/TradingAgents)（详见 [NOTICE](./NOTICE)）。
本项目代码独立编写，以 [Apache-2.0](./LICENSE) 许可证发布。
