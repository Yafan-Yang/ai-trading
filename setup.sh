#!/usr/bin/env bash
# 在脚本所在目录创建 venv 并安装依赖（全免费数据源，无需 API key）。
# 既可在仓库内直接用于开发，也会被 install.sh 复制到工具家目录后调用。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"

PY=""
for c in python3.12 python3.11 python3.10; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "❌ 未找到 python3.10+，请先安装（macOS: brew install python@3.11）" >&2
  exit 1
fi
echo "✅ 使用 $PY ($($PY --version 2>&1))"

[ -d "$VENV" ] || { echo "📦 创建 venv: $VENV"; "$PY" -m venv "$VENV"; }
"$VENV/bin/python" -m pip install --quiet --upgrade pip
echo "📥 安装依赖（首次较慢）..."
"$VENV/bin/python" -m pip install --quiet -r "$ROOT/requirements.txt"

echo "✅ 完成。工具解释器: $VENV/bin/python"
"$VENV/bin/python" -c "import akshare, yfinance, stockstats, pandas; \
print('akshare', akshare.__version__, '| yfinance', yfinance.__version__, '| pandas', pandas.__version__)"
