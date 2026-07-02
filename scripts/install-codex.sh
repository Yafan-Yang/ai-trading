#!/usr/bin/env bash
# 安装 ai-trading skills 到 Codex
# 用法：bash scripts/install-codex.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${AITRADING_HOME:-$HOME/.ai-trading}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

echo "🏠 工具家目录: $HOME_DIR"
echo "🧩 Codex 技能目录: $CODEX_DIR"

# 1) 先部署工具（与 Claude 共享）
mkdir -p "$HOME_DIR/tools"
cp "$ROOT"/tools/*.py "$HOME_DIR/tools/"
cp "$ROOT/requirements.txt" "$ROOT/setup.sh" "$HOME_DIR/"
chmod +x "$HOME_DIR/setup.sh"

if [ ! -d "$HOME_DIR/.venv" ]; then
    echo "📦 创建虚拟环境..."
    bash "$HOME_DIR/setup.sh"
else
    echo "✓ 虚拟环境已存在"
fi

# 2) 生成 Codex skills
echo "🔄 生成 Codex 格式..."
python3 "$ROOT/scripts/sync-skills.py"

# 3) 复制到 Codex 目录
mkdir -p "$CODEX_DIR"
for skill_dir in "$ROOT"/codex-skills/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  rm -rf "$CODEX_DIR/ai-trading-$name"
  cp -R "$skill_dir" "$CODEX_DIR/ai-trading-$name"

  # 替换工具路径占位符
  if [ -f "$CODEX_DIR/ai-trading-$name/SKILL.md" ]; then
    sed -i.bak "s#__AITRADING_HOME__#$HOME_DIR#g" "$CODEX_DIR/ai-trading-$name/SKILL.md"
    rm -f "$CODEX_DIR/ai-trading-$name/SKILL.md.bak"
  fi
done

echo ""
echo "✅ Codex 安装完成！"
echo ""
echo "📚 Skills 已安装到: $CODEX_DIR"
echo "   ai-trading-analyze"
echo "   ai-trading-quick"
echo "   ai-trading-market"
echo "   ... 等 9 个 skills"
echo ""
echo "🔄 请重启 Codex 以加载新 skills"
echo ""
