# AI Trading Skills 安装指南

## 三种安装方式

### 1. 使用 skills.sh CLI（推荐）

**优点**：
- 一键安装到 70+ 智能体
- 自动管理更新
- 支持项目级和全局安装
- 最佳兼容性

**安装步骤**：

```bash
# 从 GitHub 安装（需要先发布）
npx skills add Yafan-Yang/ai-trading

# 从本地路径安装（开发/测试）
npx skills add /path/to/ai-trading

# 安装特定 skill
npx skills add Yafan-Yang/ai-trading --skill analyze

# 安装到特定智能体
npx skills add Yafan-Yang/ai-trading -a claude-code -a cursor

# 全局安装（所有项目可用）
npx skills add Yafan-Yang/ai-trading -g
```

**支持的智能体**：
- Claude Code
- Codex
- Cursor
- OpenCode
- Cline
- Windsurf
- Goose
- Continue
- GitHub Copilot
- ... 以及其他 60+ 智能体

### 2. 统一安装脚本（自动检测）

```bash
git clone <your-repo-url> ai-trading
cd ai-trading
bash install.sh
```

脚本会：
1. 自动检测已安装的智能体
2. 询问你想安装到哪些平台
3. 自动部署工具和依赖
4. 生成对应格式的 skills

### 3. 手动指定平台

```bash
# 仅安装到 Claude Code
bash scripts/install-claude.sh

# 仅安装到 Codex
bash scripts/install-codex.sh

# 安装标准格式（兼容多平台）
bash scripts/install-standard.sh
```

## 安装后的目录结构

### Claude Code
```
~/.claude/commands/ai-trading/
├── analyze.md
├── quick.md
├── market.md
└── ...
```

### Codex
```
~/.codex/skills/
├── ai-trading-analyze/
│   └── SKILL.md
├── ai-trading-quick/
│   └── SKILL.md
└── ...
```

### skills.sh 标准格式（Cursor, OpenCode, 等）
```
~/.agents/skills/          # 全局安装
或
.agents/skills/            # 项目安装

├── analyze/
│   └── SKILL.md
├── quick/
│   └── SKILL.md
└── ...
```

## 共享的工具目录

所有平台共享同一套 Python 工具：

```
~/.ai-trading/
├── .venv/                 # Python 虚拟环境
├── tools/
│   ├── market_data.py
│   ├── fundamentals.py
│   ├── news_fetch.py
│   ├── verify.py
│   └── export_pdf.py
├── requirements.txt
└── setup.sh
```

## 验证安装

### Claude Code
```bash
# 在任意目录运行
claude
# 然后输入
/ai-trading:analyze 600519
```

### Codex
```bash
codex
# 在对话中输入
使用 ai-trading analyze 分析腾讯
```

### Cursor / 其他
直接在编辑器的 AI 对话中提及：
```
用 ai-trading 分析一下这只股票：AAPL
```

## 卸载

### 使用 skills.sh
```bash
npx skills remove ai-trading
```

### 手动卸载
```bash
# Claude Code
rm -rf ~/.claude/commands/ai-trading/

# Codex
rm -rf ~/.codex/skills/ai-trading-*

# 标准格式
rm -rf ~/.agents/skills/analyze
rm -rf ~/.agents/skills/quick
# ... 其他 skills

# 共享工具（可选）
rm -rf ~/.ai-trading/
```

## 常见问题

### Q: 如何更新 skills？
```bash
# 使用 skills.sh
npx skills update ai-trading

# 手动
cd /path/to/ai-trading
git pull
bash install.sh
```

### Q: 如何查看已安装的 skills？
```bash
npx skills list
```

### Q: 为什么我的智能体没有检测到？
确保智能体的配置目录存在（如 `~/.claude/`, `~/.codex/`）。有些智能体需要先运行一次才会创建配置目录。

### Q: 可以同时安装到多个智能体吗？
可以！使用 `bash install.sh` 选择选项 1，或者用 skills.sh CLI：
```bash
npx skills add . -a claude-code -a codex -a cursor
```

### Q: PDF 导出失败怎么办？
PDF 功能是可选的。macOS 需要安装图形库：
```bash
brew install pango gdk-pixbuf libffi
```

其他系统参考 WeasyPrint 文档。

## 开发者：修改 skills 后重新生成

```bash
# 1. 修改 skills/*.md 文件

# 2. 重新生成多平台格式
python3 scripts/sync-skills.py

# 3. 重新安装
bash install.sh
```

## 高级配置

### 自定义工具目录
```bash
export AITRADING_HOME=/custom/path
bash install.sh
```

### 自定义命令目录（Claude Code）
```bash
export CLAUDE_COMMANDS_DIR=/custom/path/.claude/commands
bash scripts/install-claude.sh
```

### 关闭数据缓存
```bash
export AITRADING_NOCACHE=1
```

### 自定义缓存目录
```bash
export AITRADING_CACHE=/custom/cache/dir
```
