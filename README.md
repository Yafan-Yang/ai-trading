# ai-trading

多智能体选股分析 skill 包。五分析师并行 → 多空辩论 → 交易员提案 → 风险三方辩论 → 风险经理拍板，产出结构化研报。

覆盖 **A股 / 港股 / 美股**，零数据库、零 API key、全免费数据源（akshare + yfinance）。

> ⚠️ **免责声明**：本项目仅用于研究和教育目的，**不构成任何投资建议**。AI 预测存在不确定性，投资有风险，决策需谨慎。

## 安装

### Claude Code

```bash
git clone https://github.com/Yafan-Yang/ai-trading.git
cd ai-trading
bash scripts/install-claude.sh
```

使用：`/ai-trading:analyze 600519`

### Codex

```bash
git clone https://github.com/Yafan-Yang/ai-trading.git
cd ai-trading
bash scripts/install-codex.sh
```

重启 Codex 后生效。使用：自然语言调用，例如 "使用 ai-trading analyze 分析腾讯"

### skills.sh（推荐）

支持 Claude Code、Codex、Cursor、OpenCode、Cline、Windsurf 等 70+ 智能体。

```bash
npx skills add Yafan-Yang/ai-trading
```

#### 选项

```bash
# 安装特定 skill
npx skills add Yafan-Yang/ai-trading --skill analyze

# 全局安装
npx skills add Yafan-Yang/ai-trading -g

# 安装到特定智能体
npx skills add Yafan-Yang/ai-trading -a claude-code -a cursor
```

## Skills 列表

| Skill | 功能 |
|-------|------|
| `analyze` | 完整多智能体分析流水线（~5分钟） |
| `quick` | 60秒快照（单代理） |
| `market` | 技术面分析（趋势、指标） |
| `fundamentals` | 基本面分析（财务、估值） |
| `news` | 新闻面分析 |
| `sentiment` | 情绪面分析（社交媒体） |
| `china` | A股专属视角 |
| `debate` | 多空辩论 |
| `risk-panel` | 风险三方辩论 |

## 代码格式

- **A股**：`600519`（茅台）、`000001`（平安）
- **港股**：`0700.HK`（腾讯）、`9988.HK`（阿里）
- **美股**：`AAPL`、`TSLA`、`NVDA`

## 工作流程

```
输入股票代码
    ↓
[五分析师并行]
技术面 + 基本面 + 新闻面 + 情绪面 + A股视角
    ↓
[多空辩论]
🐂 看涨 vs 🐻 看跌 → 🧑‍⚖️ 研究经理综合
    ↓
[交易员提案]
买入 / 持有 / 卖出 + 目标价 + 置信度
    ↓
[风险三方辩论]
🔥 激进 vs 🛡️ 保守 vs ⚖️ 中性
    ↓
[风险经理拍板]
最终决策 + 目标价区间 + 风险评分
    ↓
生成 Markdown 研报 → reports/ai-trading/
```

## 示例输出

```markdown
# 贵州茅台（600519）投研报告

## 📋 执行摘要
| 投资建议 | 置信度 | 风险评分 | 目标价位 |
|---------|--------|---------|---------|
| 买入 | 78% | 0.35 | ¥1850-1950 |

## 📈 技术面分析
- 趋势：上升通道
- RSI: 58（中性）
- MACD: 金叉
- 支撑/压力：¥1750 / ¥1900

## 💰 基本面分析
- PE: 28.5 (行业平均 32)
- ROE: 22.3%
- 合理价位：¥1850-2000
```

## 数据工具

```bash
PY=~/.ai-trading/.venv/bin/python

# 行情 + 技术指标
$PY ~/.ai-trading/tools/market_data.py 600519 --json

# 财务 + 估值
$PY ~/.ai-trading/tools/fundamentals.py 600519 --json

# 新闻
$PY ~/.ai-trading/tools/news_fetch.py 600519 --macro --json

# 数字校验（Decimal）
$PY ~/.ai-trading/tools/verify.py pe --price 1193 --eps 66

# 导出 PDF
$PY ~/.ai-trading/tools/export_pdf.py reports/ai-trading/report.md
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `AITRADING_NOCACHE=1` | 关闭当日缓存 |
| `AITRADING_CACHE=<dir>` | 自定义缓存目录 |
| `AITRADING_HOME=<dir>` | 自定义工具安装目录 |

## 特性

- **真实数据**：实时拉取行情、财务、新闻数据，带重试与缓存
- **数字严谨**：关键估值使用 `decimal.Decimal` 校验，杜绝 LLM 心算误差
- **多智能体流水线**：五分析师并行 → 辩论 → 最终决策
- **多平台支持**：Claude Code、Codex、Cursor 等 70+ 智能体
- **零成本**：100% 免费数据源，无需 API key

## 与 ai-berkshire 的差异化

| 维度 | ai-berkshire | ai-trading |
|------|-------------|------------|
| **投资流派** | 价值投资（巴菲特/芒格/段永平/李录） | 全方位投研（技术+基本+新闻+情绪） |
| **数据源** | 需配置多个付费源 | 100%免费（akshare+yfinance） |
| **市场覆盖** | 美股为主 | A股/港股/美股三市场 |
| **决策风格** | 10年确定性、镜子测试 | 多空辩论、风险三方、分层建议 |
| **技术特色** | 四大师对抗、强制决策 | 五分析师并行、流水线式辩论 |

## 已知限制

- 每次分析独立，未实现记忆/反思机制
- 社交情绪、港股新闻依赖联网搜索补充
- 免费数据源有频率限制与偶发波动
- 估值为工具化估算，非行情终端精度

## PDF 导出（可选）

macOS：
```bash
brew install pango gdk-pixbuf libffi
```

其他系统参考 [WeasyPrint 文档](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)。

## 开发

```bash
# 在仓库内建 venv
bash setup.sh

# 测试工具
bash smoke_test.sh

# 修改 skills 后重新生成多平台格式
python3 scripts/sync-skills.py
```

## 许可证

[Apache-2.0](./LICENSE)。思想与流程源自 [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 及上游 [TradingAgents](https://github.com/TauricResearch/TradingAgents)（详见 [NOTICE](./NOTICE)）。
