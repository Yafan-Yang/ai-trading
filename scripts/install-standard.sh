#!/usr/bin/env bash
# 安装 ai-trading skills 到 skills.sh 生态（Claude Code, Cursor, Codex 等）
# 这是推荐的标准安装方式，兼容所有支持 skills.sh 的智能体
# 用法：bash scripts/install-standard.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${AITRADING_HOME:-$HOME/.ai-trading}"

echo "🌐 AI Trading - 标准 Skills 安装程序"
echo ""
echo "🏠 工具家目录: $HOME_DIR"

# 1) 部署工具（共享）
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

# 2) 生成标准 skills 格式
echo "🔄 生成标准格式 skills..."
python3 "$ROOT/scripts/sync-skills.py"

# 3) 替换工具路径占位符（在 .agents/skills/ 中）
for skill_dir in "$ROOT"/.agents/skills/*; do
  [ -d "$skill_dir" ] || continue
  if [ -f "$skill_dir/SKILL.md" ]; then
    sed -i.bak "s#__AITRADING_HOME__#$HOME_DIR#g" "$skill_dir/SKILL.md"
    rm -f "$skill_dir/SKILL.md.bak"
  fi
done

echo ""
echo "✅ 标准格式 skills 已生成！"
echo ""
echo "📁 Skills 位置: $ROOT/.agents/skills/"
echo ""
echo "🚀 使用 skills.sh CLI 安装到任何智能体："
echo ""
echo "   # 从本地安装（推荐）"
echo "   npx skills add $ROOT"
echo ""
echo "   # 从 GitHub 安装（如果已发布）"
echo "   npx skills add <your-github-username>/ai-trading"
echo ""
echo "支持的智能体："
echo "   • Claude Code     (.claude/skills/)"
echo "   • Codex           (.codex/skills/)"
echo "   • Cursor          (.agents/skills/)"
echo "   • OpenCode        (.agents/skills/)"
echo "   • Cline           (.agents/skills/)"
echo "   • Windsurf        (.windsurf/skills/)"
echo "   • 以及 60+ 其他智能体"
echo ""
echo "💡 提示："
echo "   1. 将此项目发布到 GitHub"
echo "   2. 添加到 https://skills.sh 获得更多曝光"
echo "   3. 用户可以用 'npx skills add owner/repo' 一键安装"
echo ""
