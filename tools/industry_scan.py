"""ai-trading 数据工具：行业扫描（A股板块成分股初筛）。

用法:
    python industry_scan.py --list                 列出所有行业板块名称
    python industry_scan.py <板块名> [--top N] [--json]

- 仅支持 A股（东财行业板块）。数据源为 akshare 东财接口，偶发断连，已套重试+当日缓存。
- 一次调用即可拿到成分股的最新价、市盈率、市值等，无需逐只再取数。
- 初筛规则：市值 > 50亿 且 市盈率为正（粗筛，供人工进一步挑选）。
数据仅供研究学习，不构成投资建议。
"""
from __future__ import annotations

import argparse
import json
import sys

from _net import day_cache, retry


@retry(times=3)
@day_cache("industry_names")
def _board_names() -> list[str]:
    """板块名称列表。东财接口偶发不通，降级到同花顺（仅名称，较稳定）。"""
    import akshare as ak
    try:
        df = ak.stock_board_industry_name_em()
        return df["板块名称"].tolist()
    except Exception:  # noqa: BLE001  东财不通时降级
        df = ak.stock_board_industry_name_ths()
        return df["name"].tolist()


@retry(times=3)
@day_cache("industry_cons")
def _board_cons(board: str) -> list[dict]:
    import akshare as ak
    df = ak.stock_board_industry_cons_em(symbol=board)
    return df.to_dict(orient="records")


def _num(x):
    try:
        if x is None or x == "-":
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def scan(board: str, top: int) -> dict:
    """扫描单个行业板块，返回初筛后的候选清单。"""
    rows = _board_cons(board)
    candidates = []
    for r in rows:
        # 东财成分股字段：代码/名称/最新价/涨跌幅/市盈率-动态/总市值 等
        mktcap = _num(r.get("总市值"))
        pe = _num(r.get("市盈率-动态"))
        candidates.append({
            "代码": r.get("代码"),
            "名称": r.get("名称"),
            "最新价": _num(r.get("最新价")),
            "涨跌幅": _num(r.get("涨跌幅")),
            "市盈率": pe,
            "总市值": mktcap,
        })

    # 初筛：市值 > 50亿 且 PE 为正（None 值不参与筛选，保留但标记）
    def passes(c):
        mc, pe = c["总市值"], c["市盈率"]
        if mc is not None and mc < 5e9:
            return False
        if pe is not None and pe <= 0:
            return False
        return True

    filtered = [c for c in candidates if passes(c)]
    # 按市值降序取 Top N
    filtered.sort(key=lambda c: (c["总市值"] or 0), reverse=True)

    return {
        "板块": board,
        "成分股总数": len(candidates),
        "初筛通过数": len(filtered),
        "筛选规则": "总市值>50亿 且 市盈率>0",
        "候选清单": filtered[:top],
    }


def to_markdown(d: dict) -> str:
    lines = [
        f"# 行业扫描：{d['板块']}",
        "",
        f"- 成分股总数：{d['成分股总数']}",
        f"- 初筛通过：{d['初筛通过数']}（{d['筛选规则']}）",
        "",
        "| 代码 | 名称 | 最新价 | 涨跌幅% | 市盈率 | 总市值(亿) |",
        "|------|------|--------|---------|--------|-----------|",
    ]
    for c in d["候选清单"]:
        mc = f"{c['总市值']/1e8:.0f}" if c["总市值"] else "-"
        pe = f"{c['市盈率']:.1f}" if c["市盈率"] else "-"
        price = f"{c['最新价']:.2f}" if c["最新价"] else "-"
        chg = f"{c['涨跌幅']:+.2f}" if c["涨跌幅"] is not None else "-"
        lines.append(f"| {c['代码']} | {c['名称']} | {price} | {chg} | {pe} | {mc} |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="行业板块扫描（A股）")
    ap.add_argument("board", nargs="?", help="板块名称，如 白酒 / 半导体")
    ap.add_argument("--list", action="store_true", help="列出所有板块名称")
    ap.add_argument("--top", type=int, default=20, help="返回候选数量（默认20）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        if args.list:
            names = _board_names()
            if args.json:
                print(json.dumps(names, ensure_ascii=False, indent=2))
            else:
                print("可用板块（共 %d 个）：" % len(names))
                print("、".join(names))
            return 0

        if not args.board:
            ap.error("请提供板块名称，或用 --list 查看所有板块")

        result = scan(args.board, args.top)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(to_markdown(result))
        return 0

    except Exception as e:  # noqa: BLE001
        # 数据源断连时给出可读降级提示，而非堆栈
        msg = {
            "error": "取数失败",
            "detail": f"{type(e).__name__}: {str(e)[:120]}",
            "hint": "东财板块接口偶发断连，可稍后重试；或用 --list 确认板块名是否正确。",
        }
        if args.json:
            print(json.dumps(msg, ensure_ascii=False, indent=2))
        else:
            print(f"❌ {msg['error']}：{msg['detail']}\n💡 {msg['hint']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
