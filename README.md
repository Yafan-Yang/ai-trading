# ai-trading

> "The stock market is a device for transferring money from the impatient to the patient." — Warren Buffett

多智能体选股分析框架。用 AI 重新定义投资研究的深度与效率。

**一个人 + Claude Code / Codex = 一个投研团队**

## 为什么不能直接问 ChatGPT？

大语言模型在投资分析中的三个致命缺陷：

### 1. 数字幻觉

LLM 用浮点数心算财务指标，误差累积：

```python
# ❌ 典型 AI 回答
"茅台 PE 约 30 倍，合理估值 1800-2000 元"
# 实际：PE = 股价 1193 / 每股收益 66 ≠ 30

# ✅ ai-trading 强制验证
decimal.Decimal('1193') / Decimal('66')  # 18.08
# 结果：估值被高估 60%，避免误判
```

### 2. 确认偏差

单一视角容易陷入一致性陷阱。ai-trading 采用**五分析师并行 + 多空对抗**机制：

```
技术派："突破上升通道，RSI 未超买" 
    vs
价值派："PE 28 高于历史中位数 25"
    vs  
新闻派："反腐政策影响消费"
    vs
情绪派："雪球看涨情绪 85%，过热信号"
```

四个独立视角产生真实矛盾，逼出盲区。

### 3. 无法复现

同样的问题，ChatGPT 每次给出不同答案。ai-trading 用结构化流水线确保：

- 同样输入 → 同样深度的分析
- 7 家公司横向对比，评分标准一致
- 半年后重新分析，可直接对比变化

## 工作流程

```
输入股票代码
    ↓
[阶段 1] 五分析师并行（4倍信息量）
  技术面 + 基本面 + 新闻面 + 情绪面 + A股视角
    ↓
[阶段 2] 多空辩论
  🐂 看涨 vs 🐻 看跌 → 🧑‍⚖️ 研究经理综合
    ↓
[阶段 3] 交易员提案
  买入/持有/卖出 + 目标价 + 置信度
    ↓
[阶段 4] 风险三方辩论
  🔥 激进 vs 🛡️ 保守 vs ⚖️ 中性
    ↓
[阶段 5] 风险经理拍板
  最终决策 + 目标价区间 + 仓位建议
    ↓
[阶段 6] 生成结构化研报
  Markdown + 可选 PDF 导出
```

## 强制决策输出

不允许"两面讨好"。每份研报必须给出明确建议：

| 策略类型 | 操作建议 | 目标价位 | 建仓比例 |
|---------|---------|---------|---------|
| 🚀 激进型 | 买入 | ¥180-190 | 15-20% |
| 🎯 稳健型 | 观望后买入 | ¥160-170 | 5-10% |
| 🛡️ 保守型 | 不建议 | - | 0% |

**核心原则**：5 句话说不完整的公司 = 不买，没有例外。

## 数据严谨性保障

### 精确计算

所有估值计算使用 `decimal.Decimal`，避免浮点误差：

```python
# 真实案例：腾讯市值验算
price = Decimal('320.4')          # 港股股价
shares = Decimal('9.58e9')        # 总股本
calculated = price * shares        # 3.07万亿港币
reported = Decimal('3.06e12')     # 报告数据
deviation = abs(calculated - reported) / reported
# 结果：偏差 0.3%，通过验证 ✅
```

### 多源交叉验证

关键数据至少 2 个独立来源：

- **市值**：akshare 报告数据 vs 股价×总股本手算
- **PE**：报告 PE vs 股价÷每股收益倒推
- **ROE**：利润表 vs 资产负债表交叉计算

### 本福特定律检测

财报首位数字分布检测造假：

```python
# 正常财报：首位数字符合对数分布
revenues = [1.2亿, 2.3亿, 3.1亿, 1.8亿...]
benford_check(revenues)  # ✅ χ² = 8.2 < 15.51

# 人为修饰：首位数字异常集中
revenues = [9.8亿, 9.7亿, 9.9亿, 9.6亿...]  
benford_check(revenues)  # ❌ χ² = 42.1 > 15.51 可疑
```

## 覆盖范围

| 市场 | 数据源 | 支持功能 |
|------|--------|---------|
| **A股** | akshare | 行情/财务/新闻/政策/涨跌停 |
| **港股** | akshare | 行情/财务/新闻 |
| **美股** | yfinance | 行情/财务/新闻 |

**零成本**：100% 免费数据源，无需 API key，无频率限制（带缓存与重试）。

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

### skills.sh

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

| Skill | 功能 | 时长 |
|-------|------|------|
| `analyze` | 完整多智能体分析流水线 | ~5分钟 |
| `quick` | 60秒快照（单代理） | ~1分钟 |
| `market` | 技术面分析（趋势、指标） | ~2分钟 |
| `fundamentals` | 基本面分析（财务、估值） | ~2分钟 |
| `news` | 新闻面分析 | ~2分钟 |
| `sentiment` | 情绪面分析（社交媒体） | ~2分钟 |
| `china` | A股专属视角（政策/资金/涨跌停） | ~2分钟 |
| `debate` | 多空辩论 | ~3分钟 |
| `risk-panel` | 风险三方辩论 | ~3分钟 |

## 代码格式

- **A股**：`600519`（茅台）、`000001`（平安）
- **港股**：`0700.HK`（腾讯）、`9988.HK`（阿里）
- **美股**：`AAPL`、`TSLA`、`NVDA`

## 示例输出

```markdown
# 贵州茅台（600519）投研报告

## 📋 执行摘要
| 投资建议 | 置信度 | 风险评分 | 目标价位 |
|---------|--------|---------|---------|
| 买入 | 78% | 0.35 | ¥1850-1950 |

**核心逻辑**：
1. 品牌护城河极深，定价权强（提价 8 次无需求下滑）
2. ROE 常年 >20%，自由现金流充沛（FCF/净利润 >0.9）
3. 估值回调至 PE 28（vs 历史中位数 30，合理区间）
4. **风险**：消费降级、反腐政策、库存周期

## 📈 技术面分析
- **趋势**：60 日均线上方，上升通道完整
- **RSI**: 58（中性区间，未超买）
- **MACD**: 金叉第 3 周，动能持续
- **支撑/压力**：¥1750（20日线）/ ¥1900（前高）

## 💰 基本面分析
- **估值**：PE 28.5（行业平均 32），PB 8.2，处合理低位
- **盈利能力**：ROE 22.3%（连续 10 年 >20%），毛利率 91%
- **现金流**：经营现金流 / 净利润 = 1.15（优秀）
- **合理价位**：DCF 估值 ¥1850-2000，安全边际 5-10%

## 🛡️ 风险经理最终决策

**建议**：买入  
**目标价**：¥1850-1950  
**仓位**：10-15%（单一标的上限）  
**止损**：跌破 ¥1700（技术+估值双重支撑）

**触发条件**：
- ✅ 立即买入：回调至 ¥1780 以下
- ⏸️ 暂缓：突破 ¥1900 后等回踩
- ❌ 止损：政策黑天鹅（限价/禁售）

研报自动保存至 `reports/ai-trading/600519_analysis_20260702_143025.md`
```

## 数据工具（独立运行）

```bash
PY=~/.ai-trading/.venv/bin/python

# 行情 + 技术指标
$PY ~/.ai-trading/tools/market_data.py 600519 --json

# 财务 + 估值
$PY ~/.ai-trading/tools/fundamentals.py 600519 --json

# 新闻（含宏观）
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

## 免责声明

本项目仅用于研究和教育目的，**不构成任何投资建议**。AI 模型的预测存在不确定性，投资有风险，决策需谨慎。请咨询专业财务顾问。

## 许可证

[Apache-2.0](./LICENSE)。思想与流程源自 [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 及上游 [TradingAgents](https://github.com/TauricResearch/TradingAgents)（详见 [NOTICE](./NOTICE)）。
