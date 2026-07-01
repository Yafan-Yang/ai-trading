#!/usr/bin/env bash
# 全局安装 ai-trading skill：
#   1) 把工具 + 依赖部署到工具家目录（默认 ~/.ai-trading），并建好 venv；
#   2) 把命令安装到 Claude Code 全局命令目录（默认 ~/.claude/commands/ai-trading），
#      并把命令里的 __AITRADING_HOME__ 占位符替换成工具家目录的绝对路径。
# 安装后可在任意项目里使用 /ai-trading:analyze <代码> 等命令。
#
# 可用环境变量覆盖：
#   AITRADING_HOME       工具家目录（默认 $HOME/.ai-trading）
#   CLAUDE_COMMANDS_DIR  Claude 命令根目录（默认 $HOME/.claude/commands）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${AITRADING_HOME:-$HOME/.ai-trading}"
CMD_DIR="${CLAUDE_COMMANDS_DIR:-$HOME/.claude/commands}/ai-trading"

echo "🏠 工具家目录: $HOME_DIR"
echo "🧩 命令目录:   $CMD_DIR"

# 1) 部署工具与依赖清单
mkdir -p "$HOME_DIR/tools"
cp "$ROOT"/tools/*.py "$HOME_DIR/tools/"
cp "$ROOT/requirements.txt" "$ROOT/setup.sh" "$HOME_DIR/"
chmod +x "$HOME_DIR/setup.sh"

# 2) 建 venv（在家目录内）
bash "$HOME_DIR/setup.sh"

# 3) 安装命令并改写占位符
mkdir -p "$CMD_DIR"
for f in "$ROOT"/skills/*.md; do
  sed "s#__AITRADING_HOME__#$HOME_DIR#g" "$f" > "$CMD_DIR/$(basename "$f")"
done

echo ""
echo "✅ 安装完成！在任意项目里可用："
echo "   /ai-trading:analyze 600519      # 完整多智能体研报"
echo "   /ai-trading:quick AAPL          # 快照"
echo "   /ai-trading:market 0700.HK      # 单角色分析师"
echo ""
echo "ℹ️  PDF 导出为可选功能，macOS 需一次性安装: brew install pango gdk-pixbuf libffi"
