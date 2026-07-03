#!/usr/bin/env bash
# 安装 ai-trading skills 到 Codex（使用符号链接）
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

# 2) 生成标准格式 skills（存储到工具目录）
echo "🔄 生成标准格式..."
python3 "$ROOT/scripts/sync-skills.py"

# 将生成的 skills 复制到工具目录（单一来源）
mkdir -p "$HOME_DIR/skills"
for skill_dir in "$ROOT"/.agents/skills/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  rm -rf "$HOME_DIR/skills/$name"
  cp -R "$skill_dir" "$HOME_DIR/skills/$name"

  # 替换工具路径占位符
  if [ -f "$HOME_DIR/skills/$name/SKILL.md" ]; then
    sed -i.bak "s#__AITRADING_HOME__#$HOME_DIR#g" "$HOME_DIR/skills/$name/SKILL.md"
    rm -f "$HOME_DIR/skills/$name/SKILL.md.bak"
  fi
done

# 3) 创建符号链接到 Codex 目录
mkdir -p "$CODEX_DIR"
for skill_dir in "$HOME_DIR"/skills/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  target_link="$CODEX_DIR/ai-trading-$name"

  # 删除旧的（文件或链接）
  rm -rf "$target_link"

  # 创建符号链接
  ln -s "$skill_dir" "$target_link"
done

echo ""
echo "✅ Codex 安装完成（使用符号链接）！"
echo ""
echo "📚 源文件位置: $HOME_DIR/skills/"
echo "🔗 符号链接位置: $CODEX_DIR/ai-trading-*"
echo ""
echo "💡 优点："
echo "   • 只存储一份文件，节省空间"
echo "   • 修改源文件后自动同步"
echo "   • 更新时只需重新运行 sync-skills.py"
echo ""
echo "🔄 请重启 Codex 以加载新 skills"
echo ""
