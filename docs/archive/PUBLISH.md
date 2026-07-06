# 如何将 ai-trading 上架到 skills.sh

## 前提条件

- [x] 已完成多平台格式生成（运行过 `python3 scripts/sync-skills.py`）
- [x] 已创建 `package.json` 文件
- [x] 已更新 `README.md` 添加 skills.sh 徽章
- [x] 项目托管在 GitHub 上

## 步骤 1：发布到 GitHub

```bash
# 1. 初始化 git 仓库（如果还没有）
git init
git add .
git commit -m "feat: multi-platform skill support for skills.sh"

# 2. 创建 GitHub 仓库
# 访问 https://github.com/new 创建新仓库（名称：ai-trading）

# 3. 关联并推送
git remote add origin https://github.com/Yafan-Yang/ai-trading.git
git branch -M main
git push -u origin main
```

## 步骤 2：更新仓库信息

编辑以下文件，将 `Yafan-Yang` 替换为你的 GitHub 用户名：

- `package.json` 中的 `repository.url` 和 `homepage`
- `README.md` 中的徽章链接和安装命令

```bash
# 快速替换（macOS/Linux）
GITHUB_USER="你的GitHub用户名"
sed -i.bak "s/Yafan-Yang/$GITHUB_USER/g" package.json README.md INSTALL.md
rm -f *.bak

git add .
git commit -m "chore: update GitHub username"
git push
```

## 步骤 3：验证 skills 可发现性

skills.sh 会自动扫描 GitHub 仓库，确保：

1. **标准目录存在**：`.agents/skills/` 目录已生成 ✅
2. **SKILL.md 格式正确**：每个 skill 包含有效的 YAML frontmatter ✅
3. **必填字段**：每个 SKILL.md 都有 `name` 和 `description` ✅

测试发现性：
```bash
# 本地测试
npx skills add . --list

# 应该显示：
# Available skills:
#   ✓ analyze
#   ✓ quick
#   ✓ market
#   ✓ fundamentals
#   ✓ news
#   ✓ sentiment
#   ✓ china
#   ✓ debate
#   ✓ risk-panel
```

## 步骤 4：用户安装测试

推送到 GitHub 后，用户可以立即安装：

```bash
# 从 GitHub 安装
npx skills add Yafan-Yang/ai-trading

# 安装特定 skill
npx skills add Yafan-Yang/ai-trading --skill analyze

# 全局安装
npx skills add Yafan-Yang/ai-trading -g
```

## 步骤 5：提交到 skills.sh 目录（可选）

skills.sh 会自动爬取 GitHub 仓库，但你可以加速收录：

### 方式 A：等待自动收录
- skills.sh 会定期扫描 GitHub
- 确保仓库是公开的
- 添加 topics: `agent-skills`, `claude-code`, `trading`

```bash
# 在 GitHub 仓库页面添加 topics
```

### 方式 B：手动提交（推荐）

访问 [skills.sh](https://skills.sh) 并：
1. 点击右上角 "Submit Skill"（如果有此选项）
2. 或者在 GitHub 仓库中添加 `skillssh` topic

### 方式 C：通过 PR 提交

如果 skills.sh 有中心化目录：

```bash
git clone https://github.com/vercel-labs/skills.git
cd skills
# 编辑目录文件（如果有）
# 提交 PR
```

**注意**：根据 skills.sh 的最新文档，大多数情况下只需要确保：
1. 仓库公开
2. 包含有效的 skills
3. 有 `package.json` 元数据

系统会自动收录。

## 步骤 6：添加徽章到 README

徽章会显示安装量和排名：

```markdown
[![skills.sh](https://skills.sh/b/Yafan-Yang/ai-trading)](https://skills.sh/Yafan-Yang/ai-trading)
```

## 步骤 7：推广

1. **在 GitHub README 中突出显示**：
   - 在顶部添加徽章
   - 在安装部分优先推荐 skills.sh 方式

2. **社交媒体分享**：
   - Twitter/X 使用 `#AgentSkills` 标签
   - Reddit r/ClaudeAI, r/LocalLLaMA
   - HackerNews

3. **写文章/教程**：
   - 介绍多智能体选股分析的思路
   - 对比传统分析方法
   - 展示实际案例

4. **添加到其他平台**：
   - Claude Code Plugin Marketplace (如果适用)
   - Awesome Lists (awesome-ai-agents, awesome-trading)

## 验证上架成功

1. **搜索测试**：
   ```bash
   npx skills find trading
   # 应该能看到你的 ai-trading
   ```

2. **访问 skills.sh**：
   ```
   https://skills.sh/Yafan-Yang/ai-trading
   ```
   应该能看到你的项目页面

3. **查看排行榜**：
   ```
   https://skills.sh
   ```
   你的 skill 会出现在列表中（按安装量排序）

## 持续维护

### 更新 Skills

```bash
# 1. 修改 skills/*.md
# 2. 重新生成
python3 scripts/sync-skills.py
# 3. 提交
git add .
git commit -m "feat: add new skill / improve existing skill"
git push
```

用户更新：
```bash
npx skills update ai-trading
```

### 监控使用情况

- skills.sh 会显示安装量统计
- GitHub Insights 查看 clone/fork 数量
- 收集用户反馈（Issues/Discussions）

## 常见问题

### Q: 推送后多久能在 skills.sh 上看到？
A: 通常几分钟到几小时。如果超过 24 小时还没有，检查：
- 仓库是否公开
- `.agents/skills/` 目录是否存在
- SKILL.md 格式是否正确

### Q: 如何隐藏某些 internal skills？
A: 在 SKILL.md frontmatter 中添加：
```yaml
---
name: my-skill
description: ...
metadata:
  internal: true
---
```

只有设置了 `INSTALL_INTERNAL_SKILLS=1` 的用户才能看到。

### Q: 如何更新徽章上的统计数据？
A: 徽章会自动更新，无需手动操作。

### Q: 可以创建付费 skills 吗？
A: skills.sh 生态是开源的。你可以：
- 提供免费基础版 + 付费高级功能
- 在 README 中添加赞助链接
- 提供付费咨询/定制服务

## 成功指标

- ✅ 在 skills.sh 上可搜索到
- ✅ 徽章显示安装数量
- ✅ 用户可以用 `npx skills add` 安装
- ✅ 支持所有主流智能体
- ✅ GitHub Stars 增长
- ✅ Issues/Discussions 有活跃讨论

## 参考案例

查看其他成功的 skills：
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire)
- skills.sh 排行榜上的热门项目

---

🎉 **祝你的 skills 成功上架！**

如有问题，可以：
- 查看 [skills.sh 文档](https://github.com/vercel-labs/skills)
- 在 GitHub 提 Issue
- 加入相关社区讨论
