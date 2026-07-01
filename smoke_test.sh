#!/usr/bin/env bash
# 冒烟测试：对样本股跑通各数据工具，检查退出码与输出非空。
# 用法: bash smoke_test.sh   （在仓库根目录，需先 bash setup.sh）
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || { echo "❌ 未找到 venv，请先运行 bash setup.sh"; exit 1; }

pass=0; fail=0
run() {  # run <描述> <命令...>
  local desc="$1"; shift
  local out
  if out="$("$@" 2>/dev/null)" && [ -n "$out" ]; then
    echo "✅ $desc"; pass=$((pass+1))
  else
    echo "❌ $desc"; fail=$((fail+1))
  fi
}

echo "== 市场识别 =="
run "identify 600519/0700.HK/AAPL/830799" "$PY" "$ROOT/tools/_market.py" 600519 0700.HK AAPL 830799

echo "== 行情 =="
run "A股 600519 market_data"  "$PY" "$ROOT/tools/market_data.py" 600519 --days 60
run "美股 AAPL market_data"   "$PY" "$ROOT/tools/market_data.py" AAPL --days 60
run "港股 0700.HK market_data" "$PY" "$ROOT/tools/market_data.py" 0700.HK --days 60

echo "== 基本面 =="
run "A股 600519 fundamentals" "$PY" "$ROOT/tools/fundamentals.py" 600519
run "美股 AAPL fundamentals"  "$PY" "$ROOT/tools/fundamentals.py" AAPL

echo "== 新闻 =="
run "A股 600519 news" "$PY" "$ROOT/tools/news_fetch.py" 600519 --limit 3

echo "== 校验 =="
run "verify pe" "$PY" "$ROOT/tools/verify.py" pe --price 1193 --eps 66

echo ""
echo "结果: 通过 $pass ，失败 $fail"
[ "$fail" -eq 0 ] && echo "🎉 全部通过" || { echo "⚠️ 有失败项（免费接口偶发波动，可重试）"; exit 1; }
