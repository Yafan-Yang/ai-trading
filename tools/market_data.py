"""ai-trading 数据工具：行情 OHLCV + 技术指标。

用法:
    python market_data.py <代码> [--days 365] [--json]

- A股/港股 走 akshare，美股走 yfinance（失败时互相回退）。
- 技术指标用 stockstats 计算：MA / EMA / MACD / RSI / BOLL / ATR / MFI / VWMA。
- 默认输出人类可读的 Markdown 摘要；加 --json 输出结构化 JSON（含最近若干日指标）。

数据仅供研究学习，不构成投资建议。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta

import pandas as pd

from _market import MarketInfo, identify_market, yf_symbol
from _net import retry


@retry()
def _fetch_a(info: MarketInfo, days: int) -> pd.DataFrame:
    import akshare as ak
    end = datetime.now()
    start = end - timedelta(days=days + 60)  # 多取一点用于指标预热
    df = ak.stock_zh_a_hist(
        symbol=info.code, period="daily",
        start_date=start.strftime("%Y%m%d"), end_date=end.strftime("%Y%m%d"),
        adjust="qfq",
    )
    df = df.rename(columns={
        "日期": "date", "开盘": "open", "最高": "high", "最低": "low",
        "收盘": "close", "成交量": "volume", "成交额": "amount",
    })
    return df[["date", "open", "high", "low", "close", "volume"]]


@retry()
def _fetch_hk(info: MarketInfo, days: int) -> pd.DataFrame:
    import akshare as ak
    df = ak.stock_hk_daily(symbol=info.code.zfill(5), adjust="qfq")
    df = df.rename(columns={"date": "date", "open": "open", "high": "high",
                            "low": "low", "close": "close", "volume": "volume"})
    df = df[["date", "open", "high", "low", "close", "volume"]].tail(days + 60)
    return df


@retry()
def _fetch_yf(info: MarketInfo, days: int) -> pd.DataFrame:
    import yfinance as yf
    sym = yf_symbol(info)
    end = datetime.now()
    start = end - timedelta(days=days + 60)
    hist = yf.Ticker(sym).history(start=start.strftime("%Y-%m-%d"),
                                  end=end.strftime("%Y-%m-%d"))
    if hist.empty:
        raise RuntimeError(f"yfinance 无数据: {sym}")
    hist = hist.reset_index().rename(columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Volume": "volume",
    })
    return hist[["date", "open", "high", "low", "close", "volume"]]


def fetch_ohlcv(info: MarketInfo, days: int) -> pd.DataFrame:
    """按市场取行情，带回退。"""
    errors = []
    order = {
        "a": [_fetch_a, _fetch_yf],
        "hk": [_fetch_hk, _fetch_yf],
        "us": [_fetch_yf],
    }[info.market]
    for fn in order:
        try:
            df = fn(info, days)
            if df is not None and not df.empty:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
                for c in ["open", "high", "low", "close", "volume"]:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
                return df.dropna(subset=["close"]).reset_index(drop=True)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{fn.__name__}: {e}")
    raise RuntimeError("行情获取失败:\n" + "\n".join(errors))


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """用 stockstats 计算技术指标（与原项目一致的一组）。"""
    from stockstats import wrap
    s = wrap(df.copy())
    cols = {
        "close_50_sma": "MA50", "close_200_sma": "MA200", "close_10_ema": "EMA10",
        "macd": "MACD", "macds": "MACD_signal", "macdh": "MACD_hist",
        "rsi_14": "RSI14", "boll": "BOLL_mid", "boll_ub": "BOLL_up",
        "boll_lb": "BOLL_low", "atr_14": "ATR14", "vwma": "VWMA", "mfi": "MFI",
    }
    out = df.copy()
    for raw, name in cols.items():
        try:
            out[name] = pd.to_numeric(s[raw], errors="coerce").values
        except Exception:  # noqa: BLE001
            out[name] = None
    # stockstats 的 MFI 返回 0-1 比值，转换为通用的 0-100 区间
    if "MFI" in out and out["MFI"] is not None:
        try:
            out["MFI"] = (pd.to_numeric(out["MFI"], errors="coerce") * 100).round(3)
        except Exception:  # noqa: BLE001
            pass
    return out


def build_report(info: MarketInfo, df: pd.DataFrame, days: int) -> dict:
    view = df.tail(days).reset_index(drop=True)
    last = view.iloc[-1]
    first = view.iloc[0]
    sym = f"{info.currency_symbol}"

    def g(k):
        v = last.get(k)
        return None if v is None or pd.isna(v) else round(float(v), 4)

    chg_pct = round((last["close"] - first["close"]) / first["close"] * 100, 2)
    hi = round(float(view["high"].max()), 4)
    lo = round(float(view["low"].min()), 4)

    return {
        "ticker": info.code, "market": info.market_name, "currency": info.currency,
        "as_of": last["date"], "window_days": days,
        "price": {
            "close": round(float(last["close"]), 4),
            "period_change_pct": chg_pct,
            "period_high": hi, "period_low": lo,
        },
        "indicators": {k: g(k) for k in [
            "MA50", "MA200", "EMA10", "MACD", "MACD_signal", "MACD_hist",
            "RSI14", "BOLL_mid", "BOLL_up", "BOLL_low", "ATR14", "VWMA", "MFI"]},
        "recent": view.tail(10)[["date", "open", "high", "low", "close", "volume"]]
                     .round(4).to_dict("records"),
        "_currency_symbol": sym,
    }


def to_markdown(r: dict) -> str:
    sym = r["_currency_symbol"]
    ind = r["indicators"]
    p = r["price"]
    lines = [
        f"### 行情与技术指标 · {r['ticker']}（{r['market']}，截至 {r['as_of']}）",
        "",
        f"- 最新收盘: **{sym}{p['close']}** ｜ 近{r['window_days']}日涨跌: **{p['period_change_pct']}%**",
        f"- 区间高/低: {sym}{p['period_high']} / {sym}{p['period_low']}",
        "",
        "| 指标 | 值 | 指标 | 值 |",
        "|---|---|---|---|",
        f"| MA50 | {ind['MA50']} | MA200 | {ind['MA200']} |",
        f"| EMA10 | {ind['EMA10']} | RSI14 | {ind['RSI14']} |",
        f"| MACD | {ind['MACD']} | MACD信号 | {ind['MACD_signal']} |",
        f"| BOLL上轨 | {ind['BOLL_up']} | BOLL下轨 | {ind['BOLL_low']} |",
        f"| ATR14 | {ind['ATR14']} | MFI | {ind['MFI']} |",
        "",
        "> 数据来源: akshare/yfinance ｜ 指标: stockstats ｜ 仅供研究学习，不构成投资建议。",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="行情+技术指标取数")
    ap.add_argument("ticker")
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    info = identify_market(args.ticker)
    try:
        df = fetch_ohlcv(info, args.days)
        df = add_indicators(df)
    except Exception as e:  # noqa: BLE001
        err = {"error": str(e), "ticker": args.ticker}
        print(json.dumps(err, ensure_ascii=False) if args.json else f"❌ {e}")
        return 1

    report = build_report(info, df, args.days)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
