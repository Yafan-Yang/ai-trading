# ai-trading 优化方案（保留备用）

> 生成时间：2026-07-02
> 
> 本文档记录了借鉴 ai-berkshire 的优化思路，待安装机制完成后再实施。

## 📊 第一阶段：强化决策质量（立即见效）

### 1. 强制明确结论 + 分层建议

修改研报模板，参考 ai-berkshire 的"镜子测试"：

```markdown
## 📋 执行摘要

### 投资建议（明确结论，不打太极）

| 策略类型 | 操作建议 | 目标价位 | 建仓比例 | 触发条件 |
|---------|---------|---------|---------|---------|
| 🚀 激进型 | 买入 | ¥180-190 | 15-20% | 立即/回调3%内 |
| 🎯 稳健型 | 观望后买入 | ¥160-170 | 5-10% | 等Q3财报确认 |
| 🛡️ 保守型 | 不建议买入 | - | 0% | 不符合10年确定性 |

**镜子测试结果**：✅ 可以用5句话说清楚商业模式 / ❌ 说不清，观望

**信息丰富度**：A级（财报+多源+行业报告）/ B级（公开数据完整）/ C级（数据稀缺，仅供参考）
```

### 2. 加入反偏见检查清单

在「风险经理拍板」前增加一道关：

```python
# tools/bias_check.py
from decimal import Decimal

class BiasChecker:
    """结构化反偏见机制"""
    
    def quick_rejection_checklist(self, stock_data):
        """8条红线一票否决（参考芒格）"""
        return {
            "财务数据异常": self.check_benford_law(stock_data),
            "商业模式难懂": self.check_business_clarity(),
            "管理层诚信问题": self.check_management_integrity(),
            "行业天花板明显": self.check_industry_ceiling(),
            "护城河不清晰": self.check_moat(),
            "估值过度乐观": self.check_valuation_sanity(),
            "与市场共识一致": self.check_consensus_risk(),
            "5句话说不清楚": self.mirror_test_failed(),
        }
    
    def check_benford_law(self, financials):
        """本福特定律检测财报数字分布"""
        # 检查收入、利润首位数字分布是否异常
        pass
    
    def inverse_analysis(self, conclusion):
        """逆向检验：如果这个股票会失败，原因是什么？"""
        return {
            "最可能失败场景": "...",
            "导致估值腰斩的因素": "...",
            "竞争对手可能的反击": "...",
        }
```

在 `analyze.md` 的阶段4后加入：

```markdown
## 阶段 4.5 · 反偏见检查（新增）
调用 `bias_check.py` 执行：
1. **快速否决清单**：8条红线检查，任何一条触发立即标注高风险
2. **逆向检验**：强制思考3个失败场景
3. **信息丰富度评级**：A/B/C，C级不建议重仓
4. **反共识检查**：如果和市场共识完全一致，需要说明为什么敢跟随

输出到研报的「风险提示」章节。
```

---

## 🏗️ 第二阶段：Skill 细化和分类（1-2周）

参考 ai-berkshire 的 18 skill 体系，按**投研流程**重新组织：

### 新目录结构
```
skills/
├── 01-screening/           # 初筛阶段（新增）
│   ├── industry-scan.md       # 行业扫描：列出新能源/半导体等板块所有股票
│   ├── funnel-filter.md       # 漏斗筛选：财务健康度批量过滤
│   └── quick-reject.md        # 快速否决：8条红线批量检测
│
├── 02-deep-research/       # 深度研究（改进现有）
│   ├── analyze.md             # 保留，加强反偏见
│   ├── moat-analysis.md       # 护城河专项：网络效应/成本优势/品牌/转换成本
│   ├── management-dive.md     # 管理层深挖：治理结构/激励/诚信历史
│   └── scenario-model.md      # 情景建模：乐观/基准/悲观三套估值
│
├── 03-single-dimension/    # 单维度分析（保留现有）
│   ├── quick.md               # 60秒快照
│   ├── market.md              # 技术面
│   ├── fundamentals.md        # 基本面
│   ├── news.md                # 新闻面
│   ├── sentiment.md           # 情绪面
│   └── china.md               # A股视角
│
├── 04-debate/              # 辩论机制（保留）
│   ├── debate.md              # 多空辩论
│   └── risk-panel.md          # 风险三方
│
└── 05-portfolio/           # 持仓管理（新增）
    ├── portfolio-check.md     # 组合诊断：持仓列表输入，检查相关性/行业集中度
    ├── alert-monitor.md       # 异动监控：股价偏离基本面>15%时深度分析原因
    └── rebalance.md           # 再平衡建议：基于市值变化调整仓位
```

### 优先实现3个新 skill

#### 1. 行业扫描
```markdown
# skills/01-screening/industry-scan.md
---
description: 扫描指定行业的所有上市公司，产出候选清单
argument-hint: <行业关键词，如：新能源汽车 / 半导体 / 医疗器械>
---

流程：
1. 通过 akshare 获取行业成分股列表
2. 批量拉取市值、PE、ROE基础数据
3. 按「市值>50亿 + ROE>15% + PE合理」初筛
4. 输出 Top 20 候选清单，带简要标签
5. 询问用户对哪几只进行深度分析（调用 /ai-trading:analyze）
```

#### 2. 护城河专项分析
```markdown
# skills/02-deep-research/moat-analysis.md
---
description: 专项评估公司护城河的宽度与可持续性
argument-hint: <股票代码>
---

评估四种护城河类型：
1. **网络效应**（0-10分）：用户数→价值→更多用户的飞轮
2. **成本优势**（0-10分）：规模经济、独特资产、流程优势
3. **转换成本**（0-10分）：客户迁移成本、生态锁定
4. **品牌**（0-10分）：定价权、客户忠诚度

必须调用基本面工具验证：
- 毛利率趋势（真实成本优势的证据）
- 客户集中度（转换成本的佐证）
- 研发/营销费用率（品牌投入）

输出护城河得分卡 + 与竞品对比 + 5年内被攻破的概率评估
```

#### 3. 持仓异动监控
```markdown
# skills/05-portfolio/alert-monitor.md
---
description: 监控持仓股票价格异动，分析背离原因
argument-hint: <股票代码 [当前价格] [你的成本价]>
---

流程：
1. 拉取近30天价格、成交量、新闻
2. 计算偏离度：(当前价 - 合理估值) / 合理估值
3. 如果 |偏离度| > 15%，触发深度分析：
   - 基本面是否变化（财务数据、行业地位）
   - 市场情绪是否过度反应
   - 是否出现黑天鹅事件
4. 给出操作建议：加仓 / 持有 / 减仓 / 止损

输出格式：
| 偏离度 | 原因归因 | 是否基本面恶化 | 建议操作 |
```

---

## 🔧 第三阶段：工具层增强（长期）

### 1. 多源交叉验证

```python
# tools/cross_verify.py
from decimal import Decimal

class CrossVerifier:
    """关键数据至少2个来源验证"""
    
    def verify_market_cap(self, symbol):
        """市值手算验证"""
        # 来源1：akshare 报告数据
        reported = self.get_akshare_market_cap(symbol)
        
        # 来源2：股价 × 总股本 手算
        price = self.get_latest_price(symbol)
        shares = self.get_total_shares(symbol)
        calculated = Decimal(str(price)) * Decimal(str(shares))
        
        deviation = abs(calculated - reported) / reported
        if deviation > 0.02:  # 偏差>2%
            return {"status": "WARNING", "deviation": deviation}
        return {"status": "OK", "deviation": deviation}
    
    def verify_pe_calculation(self, symbol):
        """PE = 股价 / EPS 交叉验证"""
        reported_pe = self.get_reported_pe(symbol)
        price = self.get_latest_price(symbol)
        eps = self.get_eps(symbol)
        
        calculated_pe = Decimal(str(price)) / Decimal(str(eps))
        deviation = abs(calculated_pe - Decimal(str(reported_pe))) / Decimal(str(reported_pe))
        
        return {
            "status": "OK" if deviation < 0.05 else "WARNING",
            "reported": float(reported_pe),
            "calculated": float(calculated_pe),
            "deviation": float(deviation)
        }
    
    def benford_law_check(self, numbers):
        """本福特定律检测：首位数字分布检测财务造假"""
        from collections import Counter
        import math
        
        first_digits = [int(str(abs(n)).lstrip('0')[0]) for n in numbers if n != 0]
        observed = Counter(first_digits)
        
        # 本福特定律期望分布
        expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}
        
        # 卡方检验
        chi_square = sum(
            (observed.get(d, 0) - len(first_digits) * expected[d])**2 / 
            (len(first_digits) * expected[d])
            for d in range(1, 10)
        )
        
        # 自由度=8，显著性水平0.05，临界值≈15.51
        suspicious = chi_square > 15.51
        
        return {
            "chi_square": chi_square,
            "suspicious": suspicious,
            "warning": "财务数据首位数字分布异常，可能存在人为修饰" if suspicious else "通过"
        }
```

### 2. 估值计算器增强

```python
# tools/valuation.py
from decimal import Decimal, getcontext

getcontext().prec = 10

class ValuationCalculator:
    """三情景估值模型"""
    
    def dcf_three_scenarios(self, fcf, growth_rates, discount_rate, terminal_growth):
        """
        自由现金流折现（三情景）
        
        Args:
            fcf: 当前自由现金流
            growth_rates: {"optimistic": [0.20, 0.18, ...], "base": [...], "pessimistic": [...]}
            discount_rate: 折现率（通常 WACC）
            terminal_growth: 永续增长率
        """
        scenarios = {}
        
        for scenario, rates in growth_rates.items():
            pv_sum = Decimal(0)
            cash_flow = Decimal(str(fcf))
            
            # 预测期现金流折现
            for year, growth in enumerate(rates, 1):
                cash_flow *= (Decimal(1) + Decimal(str(growth)))
                pv = cash_flow / (Decimal(1) + Decimal(str(discount_rate))) ** year
                pv_sum += pv
            
            # 终值
            terminal_fcf = cash_flow * (Decimal(1) + Decimal(str(terminal_growth)))
            terminal_value = terminal_fcf / (Decimal(str(discount_rate)) - Decimal(str(terminal_growth)))
            terminal_pv = terminal_value / (Decimal(1) + Decimal(str(discount_rate))) ** len(rates)
            
            scenarios[scenario] = {
                "forecast_pv": float(pv_sum),
                "terminal_pv": float(terminal_pv),
                "total_value": float(pv_sum + terminal_pv)
            }
        
        return scenarios
```

---

## 📋 实施优先级

### P0（本周）
1. ✅ 优化安装机制（支持 Claude/Codex/skills.sh）
2. 修改 `analyze.md` 研报模板，加入分层建议和信息丰富度评级

### P1（2周内）
1. 实现 `bias_check.py`（快速否决清单 + 逆向检验）
2. 集成到 `analyze.md` 流程中

### P2（1个月）
1. 新增 3 个 skill：行业扫描、护城河分析、持仓异动监控
2. 重新组织目录结构

### P3（长期）
1. 实现 `cross_verify.py` 多源交叉验证
2. 扩展 `valuation.py` 三情景估值模型
3. 完整的 18 skill 体系

---

## 🎯 与 ai-berkshire 的差异化定位

| 维度 | ai-berkshire | ai-trading |
|------|-------------|------------|
| **投资流派** | 价值投资（巴菲特/芒格/段永平/李录） | 全方位投研（技术+基本+新闻+情绪） |
| **数据源** | 需配置多个付费源 | 100%免费数据（akshare+yfinance） |
| **市场覆盖** | 美股为主 | A股/港股/美股三市场 |
| **决策风格** | 10年确定性、镜子测试 | 多空辩论、风险三方、分层建议 |
| **技术特色** | 四大师对抗、强制决策 | 五分析师并行、流水线式辩论 |

**ai-trading 的核心优势**：
- ✅ 零成本启动（免费数据源）
- ✅ 覆盖中国市场（A股+港股深度支持）
- ✅ 技术面+基本面融合（不局限价值投资）
- ✅ 可扩展的辩论框架（易于加入新视角）

**可以借鉴的精华**：
- ✅ 强制决策输出（不打太极）
- ✅ 反偏见机制（快速否决清单）
- ✅ 信息丰富度评级（防止过度自信）
- ✅ 护城河评估框架（深度分析维度）

---

## 📚 参考资料

- [ai-berkshire](https://github.com/xbtlin/ai-berkshire) - 价值投资 AI 研究框架
- [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) - 多智能体选股原型
- 芒格《穷查理宝典》 - 逆向思维、快速否决清单
- 段永平投资问答 - 护城河评估、商业模式简洁性
