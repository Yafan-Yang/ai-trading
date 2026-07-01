"""ai-trading 数据工具：数字严谨性校验（防 LLM 心算错误）。

所有计算用 decimal.Decimal 精确进行。子命令:

    python verify.py calc "1193.01 / 66.04"
    python verify.py pe --price 1193.01 --eps 66.04
    python verify.py pb --price 1193.01 --bvps 216.32
    python verify.py market-cap --price 1193.01 --shares 1256197800
    python verify.py cross --a 18.06 --b 18.1 --tol 0.05   # 一致性检查

输出 JSON，供 skill 校验研报中的关键数字。仅供研究学习，不构成投资建议。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 28


def D(x) -> Decimal:
    return Decimal(str(x))


def _out(d: dict) -> int:
    print(json.dumps(d, ensure_ascii=False, indent=2))
    return 0


def cmd_calc(args) -> int:
    expr = args.expr.strip()
    if not re.fullmatch(r"[0-9eE_.+\-*/() %]+", expr):
        return _out({"error": "表达式仅允许数字与 + - * / ( ) 运算符", "expr": expr})
    try:
        # 用 Decimal 求值：将数字字面量包成 Decimal
        safe = re.sub(r"(?<![\w.])(\d+\.?\d*(?:[eE][+\-]?\d+)?)", r"Decimal('\1')", expr)
        val = eval(safe, {"__builtins__": {}}, {"Decimal": Decimal})  # noqa: S307
        return _out({"expr": expr, "result": float(val), "exact": str(val)})
    except (InvalidOperation, ZeroDivisionError, SyntaxError, Exception) as e:  # noqa: BLE001
        return _out({"error": str(e), "expr": expr})


def cmd_pe(args) -> int:
    if args.eps == 0:
        return _out({"error": "EPS 为 0，PE 无意义"})
    pe = D(args.price) / D(args.eps)
    return _out({"metric": "PE", "price": args.price, "eps": args.eps,
                 "PE": float(round(pe, 2))})


def cmd_pb(args) -> int:
    if args.bvps == 0:
        return _out({"error": "每股净资产为 0，PB 无意义"})
    pb = D(args.price) / D(args.bvps)
    return _out({"metric": "PB", "price": args.price, "bvps": args.bvps,
                 "PB": float(round(pb, 2))})


def cmd_market_cap(args) -> int:
    cap = D(args.price) * D(args.shares)
    return _out({"metric": "market_cap", "price": args.price, "shares": args.shares,
                 "market_cap": float(cap),
                 "market_cap_亿": float(round(cap / D(1e8), 2))})


def cmd_cross(args) -> int:
    a, b = D(args.a), D(args.b)
    base = abs(a) if a != 0 else D(1)
    diff = abs(a - b) / base
    ok = diff <= D(args.tol)
    return _out({"a": args.a, "b": args.b, "rel_diff": float(round(diff, 4)),
                 "tolerance": args.tol, "consistent": ok,
                 "verdict": "一致" if ok else "⚠️ 不一致，请核对数据来源"})


def main() -> int:
    ap = argparse.ArgumentParser(description="数字严谨性校验")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("calc"); p.add_argument("expr"); p.set_defaults(fn=cmd_calc)
    p = sub.add_parser("pe"); p.add_argument("--price", type=float, required=True)
    p.add_argument("--eps", type=float, required=True); p.set_defaults(fn=cmd_pe)
    p = sub.add_parser("pb"); p.add_argument("--price", type=float, required=True)
    p.add_argument("--bvps", type=float, required=True); p.set_defaults(fn=cmd_pb)
    p = sub.add_parser("market-cap"); p.add_argument("--price", type=float, required=True)
    p.add_argument("--shares", type=float, required=True); p.set_defaults(fn=cmd_market_cap)
    p = sub.add_parser("cross"); p.add_argument("--a", type=float, required=True)
    p.add_argument("--b", type=float, required=True)
    p.add_argument("--tol", type=float, default=0.05); p.set_defaults(fn=cmd_cross)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
