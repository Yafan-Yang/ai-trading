#!/usr/bin/env bash
# 安装 ai-trading skills 到 Claude Code（使用符号链接）
# 用法：bash scripts/install-claude.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${AITRADING_HOME:-$HOME/.ai-trading}"
CMD_DIR="${CLAUDE_COMMANDS_DIR:-$HOME/.claude/commands}/ai-trading"

echo "🏠 工具家目录: $HOME_DIR"
echo "🧩 Claude 命令目录: $CMD_DIR"

# 1) 部署工具与依赖清单
mkdir -p "$HOME_DIR/tools"
cp "$ROOT"/tools/*.py "$HOME_DIR/tools/"
cp "$ROOT/requirements.txt" "$ROOT/setup.sh" "$HOME_DIR/"
chmod +x "$HOME_DIR/setup.sh"

# 2) 建 venv（在家目录内）
if [ ! -d "$HOME_DIR/.venv" ]; then
    echo "📦 创建虚拟环境..."
    bash "$HOME_DIR/setup.sh"
else
    echo "✓ 虚拟环境已存在"
fi

# 3) 将 skills 复制到工具目录（单一来源）
mkdir -p "$HOME_DIR/claude-commands"
for f in "$ROOT"/skills/*.md; do
  name="$(basename "$f")"
  sed "s#__AITRADING_HOME__#$HOME_DIR#g" "$f" > "$HOME_DIR/claude-commands/$name"
done

# 4) 创建符号链接到 Claude 命令目录
mkdir -p "$CMD_DIR"
for f in "$HOME_DIR"/claude-commands/*.md; do
  name="$(basename "$f")"
  target_link="$CMD_DIR/$name"

  # 删除旧的（文件或链接）
  rm -f "$target_link"

  # 创建符号链接
  ln -s "$f" "$target_link"
done

echo ""
echo "✅ Claude Code 安装完成（使用符号链接）！"
echo ""
echo "📚 源文件位置: $HOME_DIR/claude-commands/"
echo "🔗 符号链接位置: $CMD_DIR/"
echo ""
echo "📚 可用命令："
echo "   /ai-trading:analyze 600519      # 完整多智能体研报"
echo "   /ai-trading:quick AAPL          # 60秒快照"
echo "   /ai-trading:market 0700.HK      # 单维度分析"
echo ""
echo "💡 优点："
echo "   • 只存储一份文件，节省空间"
echo "   • 修改源文件后自动同步"
echo "   • 更新时只需重新生成命令文件"
echo ""
