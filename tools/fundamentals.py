"""ai-trading 数据工具：基本面（财务三表关键项 + 估值比率）。

用法:
    python fundamentals.py <代码> [--json]

- A股/港股 走 akshare，美股走 yfinance。
- 输出：公司概况、估值(PE/PB/PS)、盈利能力(ROE/毛利/净利)、规模(市值/营收/净利)。
数据仅供研究学习，不构成投资建议。
"""
from __future__ import annotations

import argparse
import json
import sys

from _market import MarketInfo, identify_market, yf_symbol
from _net import day_cache, retry


def _num(x):
    try:
        if x is None:
            return None
        return round(float(x), 4)
    except (TypeError, ValueError):
        return None


def _a_name(code: str) -> str | None:
    """A股名称查询（stock_individual_info_em 在新版 akshare 已损坏，改用代码-名称表）。"""
    import akshare as ak
    try:
        nm = ak.stock_info_a_code_name()
        hit = nm[nm["code"] == code]
        if not hit.empty:
            return str(hit.iloc[0]["name"])
    except Exception:  # noqa: BLE001
        pass
    return None


def _a_price(code: str) -> float | None:
    """A股最新价（用于估值反算）。"""
    import akshare as ak
    try:
        d = ak.stock_bid_ask_em(symbol=code)
        kv = dict(zip(d["item"], d["value"]))
        return _num(kv.get("最新"))
    except Exception:  # noqa: BLE001
        return None


@retry()
def _fetch_a(info: MarketInfo) -> dict:
    import akshare as ak
    out = {"name": _a_name(info.code), "profile": {}, "valuation": {},
           "profitability": {}, "solvency": {}, "growth": {}, "scale": {}}

    abs_df = ak.stock_financial_abstract(symbol=info.code)
    if abs_df is None or abs_df.empty:
        raise RuntimeError("stock_financial_abstract 无数据")
    periods = [c for c in abs_df.columns if c not in ("选项", "指标")]  # 最新在前
    idx = abs_df.set_index("指标")
    latest = periods[0]
    out["_report_period"] = latest

    def series(name):
        """取某指标的整行（去重取第一条）。"""
        try:
            r = idx.loc[name]
            if getattr(r, "ndim", 1) > 1:
                r = r.iloc[0]
            return {p: r[p] for p in periods}
        except Exception:  # noqa: BLE001
            return {}

    def latest_of(name):
        return _num(series(name).get(latest))

    # 盈利能力
    out["profitability"]["ROE净资产收益率(%)"] = latest_of("净资产收益率(ROE)")
    out["profitability"]["ROA总资产报酬率(%)"] = latest_of("总资产报酬率(ROA)") or latest_of("总资产报酬率")
    out["profitability"]["毛利率(%)"] = latest_of("毛利率")
    out["profitability"]["销售净利率(%)"] = latest_of("销售净利率")
    # 偿债
    out["solvency"]["资产负债率(%)"] = latest_of("资产负债率")
    out["solvency"]["流动比率"] = latest_of("流动比率")
    # 成长
    out["growth"]["营收增长率(%)"] = latest_of("营业总收入增长率")
    out["growth"]["归母净利增长率(%)"] = latest_of("归属母公司净利润增长率")
    # 规模（元）
    out["scale"]["营业总收入"] = latest_of("营业总收入")
    out["scale"]["归母净利润"] = latest_of("归母净利润")
    out["scale"]["净资产"] = latest_of("股东权益合计(净资产)")

    # 估值：PE(TTM) 与 PB，用最新价反算
    price = _a_price(info.code)
    eps = series("基本每股收益")
    bvps = latest_of("每股净资产")
    if price:
        out["valuation"]["最新价"] = price
        if bvps:
            out["valuation"]["PB"] = round(price / bvps, 2)
        # TTM EPS = 最新累计 + (上年年报 - 上年同期累计)，中国财报为年内累计
        py_end = str(int(latest[:4]) - 1) + "1231"
        py_same = str(int(latest[:4]) - 1) + latest[4:]
        try:
            if latest.endswith("1231"):
                ttm_eps = eps[latest]
            else:
                ttm_eps = eps[latest] + (eps[py_end] - eps[py_same])
            if ttm_eps and ttm_eps > 0:
                out["valuation"]["PE(TTM,估算)"] = round(price / ttm_eps, 2)
                out["valuation"]["每股收益TTM(估算)"] = round(float(ttm_eps), 3)
        except Exception:  # noqa: BLE001
            pass
        out["valuation"]["每股净资产"] = bvps
    return out


def _pct(x):
    """yfinance 的比率是小数（0.47），转成百分数（47.0）。"""
    v = _num(x)
    return None if v is None else round(v * 100, 2)


@retry()
def _fetch_us_hk(info: MarketInfo) -> dict:
    import yfinance as yf
    t = yf.Ticker(yf_symbol(info))
    fi = t.info or {}
    out = {
        "name": fi.get("longName") or fi.get("shortName"),
        "profile": {
            "行业": fi.get("industry"), "板块": fi.get("sector"),
            "国家": fi.get("country"), "网站": fi.get("website"),
        },
        "valuation": {
            "PE(TTM)": _num(fi.get("trailingPE")),
            "预期PE": _num(fi.get("forwardPE")),
            "PB": _num(fi.get("priceToBook")),
            "PS": _num(fi.get("priceToSalesTrailing12Months")),
        },
        "profitability": {
            "ROE(%)": _pct(fi.get("returnOnEquity")),
            "毛利率(%)": _pct(fi.get("grossMargins")),
            "净利率(%)": _pct(fi.get("profitMargins")),
        },
        "scale": {
            "市值": _num(fi.get("marketCap")),
            "营收(TTM)": _num(fi.get("totalRevenue")),
            "净利润": _num(fi.get("netIncomeToCommon")),
            "52周高": _num(fi.get("fiftyTwoWeekHigh")),
            "52周低": _num(fi.get("fiftyTwoWeekLow")),
        },
        "analyst": {
            "推荐": fi.get("recommendationKey"),
            "目标均价": _num(fi.get("targetMeanPrice")),
        },
    }
    return out


@day_cache("fundamentals")
def fetch(info: MarketInfo) -> dict:
    if info.market == "a":
        return _fetch_a(info)
    return _fetch_us_hk(info)


def to_markdown(info: MarketInfo, d: dict) -> str:
    sym = info.currency_symbol
    lines = [f"### 基本面 · {d.get('name') or info.code}（{info.market_name}）", ""]
    if d.get("_report_period"):
        lines.append(f"报告期: {d['_report_period']}")
        lines.append("")
    for section, title in [("profile", "公司概况"), ("valuation", "估值"),
                           ("profitability", "盈利能力"), ("solvency", "偿债能力"),
                           ("growth", "成长性"), ("scale", "规模"),
                           ("analyst", "分析师")]:
        block = d.get(section) or {}
        block = {k: v for k, v in block.items() if not k.startswith("_") and v is not None}
        if not block:
            continue
        lines.append(f"**{title}**")
        for k, v in block.items():
            lines.append(f"- {k}: {v}")
        lines.append("")
    lines.append(f"> 计价货币: {info.currency}({sym}) ｜ 数据来源: akshare/yfinance ｜ 仅供研究学习，不构成投资建议。")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="基本面取数")
    ap.add_argument("ticker")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    info = identify_market(args.ticker)
    try:
        data = fetch(info)
    except Exception as e:  # noqa: BLE001
        err = {"error": str(e), "ticker": args.ticker}
        print(json.dumps(err, ensure_ascii=False) if args.json else f"❌ {e}")
        return 1

    if args.json:
        data["_meta"] = {"ticker": info.code, "market": info.market_name,
                         "currency": info.currency}
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(info, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
