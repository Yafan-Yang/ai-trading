# 从旧安装方式迁移到新的多平台安装

如果你之前使用了旧的 `install.sh`（仅支持 Claude Code），现在可以迁移到支持多平台的新安装方式。

## 变化概览

### 旧版本（仅 Claude Code）
```
~/.claude/commands/ai-trading/
├── analyze.md
├── quick.md
└── ...
```

### 新版本（多平台）
```
# 标准格式（70+ 智能体，包括 Codex）
.agents/skills/
├── analyze/SKILL.md
├── quick/SKILL.md
└── ...

# Claude Code（保持兼容）
~/.claude/commands/ai-trading/
├── analyze.md
└── ...
```

## 迁移步骤

### 1. 拉取最新代码

```bash
cd ai-trading
git pull origin main
```

### 2. 生成新格式

```bash
python3 scripts/sync-skills.py
```

这会生成：
- `.agents/skills/` - skills.sh 标准格式（兼容所有智能体包括 Codex）

### 3. 选择安装方式

#### 选项 A：使用 skills.sh CLI（推荐）

```bash
# 全局安装到所有检测到的智能体
npx skills add .

# 或指定特定智能体
npx skills add . -a claude-code -a cursor -a codex
```

**优点**：
- 自动支持所有智能体
- 统一管理和更新
- 最佳兼容性

#### 选项 B：手动安装脚本

```bash
# 交互式选择
bash install.sh

# 或单独安装
bash scripts/install-claude.sh    # Claude Code
bash scripts/install-standard.sh  # 标准格式（推荐，兼容所有智能体）
```

### 4. 验证安装

#### Claude Code
```bash
# 原有命令继续工作
/ai-trading:analyze 600519
```

#### Codex / Cursor / 其他
直接在对话中提及：
```
用 analyze 分析 AAPL
```

## 清理旧安装（可选）

如果你只想保留新的标准格式安装：

```bash
# 备份（推荐）
cp -r ~/.claude/commands/ai-trading ~/.claude/commands/ai-trading.backup

# 删除旧安装
rm -rf ~/.claude/commands/ai-trading

# 使用新方式重新安装
npx skills add . -a claude-code
```

## 保持两种格式共存

**可以同时保留**旧的 Claude Code 命令和新的标准格式：

- 旧命令：`/ai-trading:analyze`（继续工作）
- 新格式：通过 skills.sh 安装的版本

它们共享同一个工具目录（`~/.ai-trading/`），互不干扰。

## 更新工作流变化

### 旧方式
```bash
# 修改 skills/*.md
# 手动重新运行 install.sh
```

### 新方式
```bash
# 1. 修改 skills/*.md
# 2. 自动同步（GitHub Actions）或手动同步
python3 scripts/sync-skills.py
# 3. 推送到 GitHub
git add . && git commit -m "update skills" && git push
# 4. 用户更新
npx skills update ai-trading
```

## 开发者注意事项

### 单一来源原则

`skills/*.md` 是唯一的源文件（Single Source of Truth）：

```
skills/*.md
    ↓ (sync-skills.py)
    └→ .agents/skills/    (标准格式，兼容所有智能体)
```

**永远只修改 `skills/*.md`**，然后运行 `sync-skills.py` 重新生成。

## 常见问题

### Q: 旧的 `/ai-trading:analyze` 还能用吗？
A: 可以！如果你保留了 `~/.claude/commands/ai-trading/`，旧命令继续工作。

### Q: 需要卸载旧版本吗？
A: 不需要。新旧版本可以共存，它们共享工具目录。

### Q: 如何在项目中使用而不是全局安装？
```bash
cd my-project
npx skills add Yafan-Yang/ai-trading
# skills 安装到 my-project/.agents/skills/
```

### Q: GitHub Actions 自动同步是什么？
A: 当你推送 `skills/*.md` 更改时，GitHub Actions 会自动运行 `sync-skills.py` 并提交生成的文件。

查看 `.github/workflows/sync-skills.yml`
