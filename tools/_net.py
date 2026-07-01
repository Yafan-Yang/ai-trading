"""ai-trading 共享：取数重试 + 当日本地缓存。

- retry(): 对偶发网络错误重试若干次（akshare/yfinance 常见断连）。
- day_cache(): 以「代码+函数+当天」为键把结果缓存到 ~/.ai-trading/cache，
  同一天重复取数直接命中，降低对免费接口的压力。
"""
from __future__ import annotations

import functools
import hashlib
import json
import os
import time
from datetime import date
from pathlib import Path

CACHE_DIR = Path(os.environ.get("AITRADING_CACHE",
                                Path.home() / ".ai-trading" / "cache"))


def retry(times: int = 3, delay: float = 1.2, backoff: float = 1.8):
    """网络取数重试装饰器。"""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            wait, last = delay, None
            for i in range(times):
                try:
                    return fn(*a, **kw)
                except Exception as e:  # noqa: BLE001
                    last = e
                    if i < times - 1:
                        time.sleep(wait)
                        wait *= backoff
            raise last
        return wrapper
    return deco


def _key(namespace: str, *parts) -> Path:
    raw = "|".join([namespace, str(date.today()), *map(str, parts)])
    h = hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]  # noqa: S324
    return CACHE_DIR / f"{namespace}_{h}.json"


def day_cache(namespace: str):
    """把返回的「可 JSON 序列化」结果按天缓存。仅用于纯数据函数。"""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            if os.environ.get("AITRADING_NOCACHE"):
                return fn(*a, **kw)
            path = _key(namespace, *a, *sorted(kw.items()))
            if path.exists():
                try:
                    return json.loads(path.read_text("utf-8"))
                except Exception:  # noqa: BLE001
                    pass
            result = fn(*a, **kw)
            try:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(result, ensure_ascii=False), "utf-8")
            except Exception:  # noqa: BLE001
                pass
            return result
        return wrapper
    return deco
