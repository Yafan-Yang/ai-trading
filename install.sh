#!/usr/bin/env bash
# AI Trading 统一安装脚本
# 自动检测并安装到所有可用的智能体平台

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     AI Trading - 多智能体选股分析 Skill 安装程序       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 检测可用的智能体
DETECTED_AGENTS=()

if [ -d "$HOME/.claude" ]; then
    DETECTED_AGENTS+=("claude-code")
fi

if [ -d "$HOME/.codex" ]; then
    DETECTED_AGENTS+=("codex")
fi

if [ -d "$HOME/.cursor" ]; then
    DETECTED_AGENTS+=("cursor")
fi

if [ -d "$HOME/.agents" ]; then
    DETECTED_AGENTS+=("standard-agents")
fi

if [ ${#DETECTED_AGENTS[@]} -eq 0 ]; then
    echo "⚠️  未检测到已安装的智能体"
    echo ""
    echo "推荐使用 skills.sh CLI 安装（支持 70+ 智能体）："
    echo "   bash scripts/install-standard.sh"
    echo ""
    exit 0
fi

echo "🔍 检测到以下智能体："
for agent in "${DETECTED_AGENTS[@]}"; do
    echo "   ✓ $agent"
done
echo ""

# 询问用户想要安装到哪些平台
echo "请选择安装方式："
echo ""
echo "  1) 安装到所有检测到的智能体"
echo "  2) 仅安装到 Claude Code"
echo "  3) 仅安装到 Codex"
echo "  4) 使用 skills.sh 标准格式（推荐，兼容性最好）"
echo "  5) 退出"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📦 安装到所有检测到的智能体..."
        echo ""

        for agent in "${DETECTED_AGENTS[@]}"; do
            case $agent in
                claude-code)
                    bash "$ROOT/scripts/install-claude.sh"
                    ;;
                codex)
                    bash "$ROOT/scripts/install-codex.sh"
                    ;;
                *)
                    ;;
            esac
        done

        bash "$ROOT/scripts/install-standard.sh"
        ;;
    2)
        bash "$ROOT/scripts/install-claude.sh"
        ;;
    3)
        bash "$ROOT/scripts/install-codex.sh"
        ;;
    4)
        bash "$ROOT/scripts/install-standard.sh"
        ;;
    5)
        echo "❌ 安装已取消"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║               🎉 安装完成！                           ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
