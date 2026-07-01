"""ai-trading 共享工具：市场识别、代码规范化、货币单位。

对标原项目 tradingagents/utils/stock_utils.py 的市场判定逻辑。
支持 A股 / 港股 / 美股。
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MarketInfo:
    market: str          # 'a' | 'hk' | 'us'
    market_name: str     # 中文市场名
    currency: str        # 货币代码 CNY / HKD / USD
    currency_symbol: str # ¥ / HK$ / $
    code: str            # 规范化后的代码（用于取数）
    raw: str             # 原始输入


def identify_market(ticker: str) -> MarketInfo:
    """根据代码格式判定市场。

    - A股:  6 位数字            600519 / 000001 / 300750 / 688981
    - 港股: 数字含 .HK 或 4-5 位纯数字  0700.HK / 00700 / 9988
    - 美股: 1-5 位字母           AAPL / TSLA / BRK.B
    """
    raw = (ticker or "").strip()
    t = raw.upper()

    # 港股：显式 .HK 后缀
    if t.endswith(".HK"):
        digits = t[:-3]
        return MarketInfo("hk", "港股", "HKD", "HK$", digits.zfill(5), raw)

    # A股：6 位纯数字
    if re.fullmatch(r"\d{6}", t):
        return MarketInfo("a", "中国A股", "CNY", "¥", t, raw)

    # 港股：4-5 位纯数字（补齐到 5 位）
    if re.fullmatch(r"\d{4,5}", t):
        return MarketInfo("hk", "港股", "HKD", "HK$", t.zfill(5), raw)

    # 美股：字母（允许 BRK.B 这类）
    if re.fullmatch(r"[A-Z]{1,5}(\.[A-Z])?", t):
        return MarketInfo("us", "美股", "USD", "$", t, raw)

    # 兜底：含字母按美股，否则按 A股
    if any(c.isalpha() for c in t):
        return MarketInfo("us", "美股", "USD", "$", t, raw)
    return MarketInfo("a", "中国A股", "CNY", "¥", t, raw)


def yf_symbol(info: MarketInfo) -> str:
    """转换成 yfinance 可识别的代码。"""
    if info.market == "us":
        return info.code
    if info.market == "hk":
        # yfinance 港股：4 位数字 + .HK（如 0700.HK）
        return f"{info.code.lstrip('0').zfill(4)}.HK"
    # A股 yfinance：6 位 + .SS(沪) / .SZ(深) / .BJ(北交所)
    if info.code[:2] in ("83", "87", "88", "43", "92"):
        return f"{info.code}.BJ"  # 北交所
    suffix = ".SS" if info.code[0] in "69" else ".SZ"
    return f"{info.code}{suffix}"


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["600519", "0700.HK", "9988", "AAPL"]:
        m = identify_market(arg)
        print(f"{arg:>10} -> {m.market_name}({m.market}) code={m.code} "
              f"{m.currency_symbol}{m.currency} yf={yf_symbol(m)}")
