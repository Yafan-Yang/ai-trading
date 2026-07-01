"""ai-trading 数据工具：个股新闻。

用法:
    python news_fetch.py <代码> [--limit 10] [--macro] [--json]

- A股: akshare stock_news_em（东方财富个股新闻）；--macro 追加央视财经宏观新闻。
- 美股: yfinance 的新闻列表。
- 港股: akshare 覆盖有限，返回空并提示由 skill 用联网搜索补充。

数据仅供研究学习，不构成投资建议。
"""
from __future__ import annotations

import argparse
import json
import sys

from _market import MarketInfo, identify_market, yf_symbol
from _net import retry


@retry(times=2)
def _news_a(info: MarketInfo, limit: int) -> list[dict]:
    import akshare as ak
    df = ak.stock_news_em(symbol=info.code)
    items = []
    for _, r in df.head(limit).iterrows():
        content = str(r.get("新闻内容", "") or "")
        items.append({
            "title": str(r.get("新闻标题", "")).strip(),
            "time": str(r.get("发布时间", "")).strip(),
            "source": str(r.get("文章来源", "")).strip(),
            "summary": content[:180].strip(),
            "url": str(r.get("新闻链接", "")).strip(),
        })
    return items


@retry(times=2)
def _news_us(info: MarketInfo, limit: int) -> list[dict]:
    import yfinance as yf
    raw = getattr(yf.Ticker(yf_symbol(info)), "news", None) or []
    items = []
    for n in raw[:limit]:
        c = n.get("content", n) if isinstance(n, dict) else {}
        title = c.get("title") or n.get("title", "")
        items.append({
            "title": str(title).strip(),
            "time": str(c.get("pubDate", n.get("providerPublishTime", ""))),
            "source": str((c.get("provider") or {}).get("displayName", "") if isinstance(c.get("provider"), dict) else n.get("publisher", "")),
            "summary": str(c.get("summary", "")).strip()[:180],
            "url": str((c.get("canonicalUrl") or {}).get("url", "") if isinstance(c.get("canonicalUrl"), dict) else n.get("link", "")),
        })
    return items


def _macro_cctv(limit: int = 5) -> list[dict]:
    import akshare as ak
    df = ak.news_cctv()
    items = []
    for _, r in df.tail(limit).iterrows():
        items.append({
            "title": str(r.get("title", "")).strip(),
            "time": str(r.get("date", "")).strip(),
            "source": "央视财经",
            "summary": str(r.get("content", "")).strip()[:180],
            "url": "",
        })
    return items


def fetch(info: MarketInfo, limit: int, macro: bool) -> dict:
    out = {"ticker": info.code, "market": info.market_name, "items": [],
           "macro": [], "note": ""}
    try:
        if info.market == "a":
            out["items"] = _news_a(info, limit)
        elif info.market == "us":
            out["items"] = _news_us(info, limit)
        else:  # hk
            out["note"] = "港股新闻 akshare 覆盖有限，建议由 skill 用联网搜索补充。"
    except Exception as e:  # noqa: BLE001
        out["note"] = f"新闻获取失败: {e}；建议由 skill 用联网搜索补充。"
    if macro:
        try:
            out["macro"] = _macro_cctv()
        except Exception as e:  # noqa: BLE001
            out["macro_error"] = str(e)
    return out


def to_markdown(d: dict) -> str:
    lines = [f"### 新闻 · {d['ticker']}（{d['market']}）", ""]
    if not d["items"]:
        lines.append(f"_未获取到个股新闻。{d.get('note', '')}_")
    for i, n in enumerate(d["items"], 1):
        lines.append(f"{i}. **{n['title']}** ({n['time']} · {n['source']})")
        if n["summary"]:
            lines.append(f"   {n['summary']}")
    if d.get("macro"):
        lines += ["", "**宏观（央视财经）**"]
        for n in d["macro"]:
            lines.append(f"- {n['title']}（{n['time']}）")
    lines += ["", "> 数据来源: akshare/yfinance ｜ 仅供研究学习，不构成投资建议。"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="个股新闻取数")
    ap.add_argument("ticker")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--macro", action="store_true", help="追加央视财经宏观新闻")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    info = identify_market(args.ticker)
    data = fetch(info, args.limit, args.macro)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
