"""ai-trading 数据工具：三情景 DCF 估值模型（纯计算，不联网）。

用 decimal.Decimal 精确折现，避免浮点误差。给出乐观/基准/悲观三套现金流折现估值。

用法:
    # 基准单情景（增长率逗号分隔，逐年）
    python valuation.py --fcf 5.85e10 --growth 0.12,0.10,0.08,0.06,0.05 \
        --discount 0.083 --terminal 0.03 --shares 1.256e9

    # 三情景（乐观/基准/悲观各一组增长率）
    python valuation.py --fcf 5.85e10 --shares 1.256e9 --discount 0.083 --terminal 0.03 \
        --optimistic 0.18,0.16,0.14,0.12,0.10 \
        --base 0.12,0.10,0.08,0.06,0.05 \
        --pessimistic 0.06,0.05,0.04,0.03,0.02 --json

参数：
    --fcf        当前自由现金流（元）
    --growth     基准情景逐年增长率（如未用三情景模式）
    --discount   折现率 / WACC
    --terminal   永续增长率（须 < 折现率）
    --shares     总股本（可选，用于换算每股内在价值）

仅供研究学习，不构成投资建议。
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, getcontext

getcontext().prec = 28


def D(x) -> Decimal:
    return Decimal(str(x))


def dcf(fcf, growth_rates, discount_rate, terminal_growth) -> dict:
    """单情景 DCF。

    Args:
        fcf: 当前自由现金流
        growth_rates: 预测期逐年增长率列表
        discount_rate: 折现率
        terminal_growth: 永续增长率（须 < discount_rate）

    Returns:
        含预测期现值、终值现值、企业价值的字典
    """
    r = D(discount_rate)
    g_term = D(terminal_growth)
    if g_term >= r:
        raise ValueError(f"永续增长率({terminal_growth})必须小于折现率({discount_rate})")

    cash_flow = D(fcf)
    pv_sum = D(0)
    yearly = []

    n = len(growth_rates)
    for year, growth in enumerate(growth_rates, 1):
        cash_flow = cash_flow * (D(1) + D(growth))
        discount_factor = (D(1) + r) ** year
        pv = cash_flow / discount_factor
        pv_sum += pv
        yearly.append({
            "year": year,
            "growth": float(growth),
            "fcf": float(round(cash_flow, 2)),
            "pv": float(round(pv, 2)),
        })

    # 终值（Gordon 增长模型），并折回现值
    terminal_fcf = cash_flow * (D(1) + g_term)
    terminal_value = terminal_fcf / (r - g_term)
    terminal_pv = terminal_value / ((D(1) + r) ** n)

    enterprise_value = pv_sum + terminal_pv

    return {
        "forecast_pv": float(round(pv_sum, 2)),
        "terminal_pv": float(round(terminal_pv, 2)),
        "terminal_value": float(round(terminal_value, 2)),
        "enterprise_value": float(round(enterprise_value, 2)),
        "yearly": yearly,
    }


def three_scenarios(fcf, scenarios, discount_rate, terminal_growth, shares=None) -> dict:
    """三情景估值。

    Args:
        scenarios: {"optimistic": [...], "base": [...], "pessimistic": [...]}
        shares: 总股本（可选），提供则换算每股内在价值
    """
    results = {}
    for name, rates in scenarios.items():
        r = dcf(fcf, rates, discount_rate, terminal_growth)
        if shares:
            r["value_per_share"] = float(round(D(r["enterprise_value"]) / D(shares), 2))
        results[name] = r

    summary = {
        "inputs": {
            "fcf": float(fcf),
            "discount_rate": float(discount_rate),
            "terminal_growth": float(terminal_growth),
            "shares": float(shares) if shares else None,
        },
        "scenarios": results,
    }

    # 若有每股价值，给出区间摘要
    if shares:
        per_share = {k: v["value_per_share"] for k, v in results.items()}
        summary["value_per_share_range"] = {
            "low": min(per_share.values()),
            "high": max(per_share.values()),
            "base": per_share.get("base"),
        }
    return summary


def _parse_rates(s: str) -> list[float]:
    return [float(x) for x in s.split(",") if x.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description="三情景 DCF 估值（纯计算）")
    ap.add_argument("--fcf", type=float, required=True, help="当前自由现金流")
    ap.add_argument("--discount", type=float, required=True, help="折现率/WACC")
    ap.add_argument("--terminal", type=float, required=True, help="永续增长率")
    ap.add_argument("--shares", type=float, help="总股本（换算每股价值）")
    ap.add_argument("--growth", type=str, help="基准情景逐年增长率，逗号分隔")
    ap.add_argument("--optimistic", type=str, help="乐观情景增长率")
    ap.add_argument("--base", type=str, help="基准情景增长率")
    ap.add_argument("--pessimistic", type=str, help="悲观情景增长率")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        # 三情景模式
        if args.optimistic or args.base or args.pessimistic:
            scenarios = {}
            if args.optimistic:
                scenarios["optimistic"] = _parse_rates(args.optimistic)
            if args.base:
                scenarios["base"] = _parse_rates(args.base)
            if args.pessimistic:
                scenarios["pessimistic"] = _parse_rates(args.pessimistic)
            result = three_scenarios(args.fcf, scenarios, args.discount,
                                     args.terminal, args.shares)
        # 单情景模式
        elif args.growth:
            r = dcf(args.fcf, _parse_rates(args.growth), args.discount, args.terminal)
            if args.shares:
                r["value_per_share"] = float(round(D(r["enterprise_value"]) / D(args.shares), 2))
            result = r
        else:
            ap.error("请提供 --growth（单情景）或 --optimistic/--base/--pessimistic（三情景）")

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    except ValueError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
