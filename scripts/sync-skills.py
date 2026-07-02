#!/usr/bin/env python3
"""
将 Claude Code 命令文件转换为多平台格式：
1. Codex Skills (.codex/skills/*/)
2. skills.sh 兼容格式 (skills/*)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / "skills"
CODEX_SKILLS = ROOT / "codex-skills"
STANDARD_SKILLS = ROOT / ".agents" / "skills"  # skills.sh 标准位置


def split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """分离 YAML frontmatter 和正文"""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text

    frontmatter_text = text[4:end]
    body = text[end + 5:].lstrip("\n")

    # 解析 frontmatter
    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def first_heading(text: str, fallback: str) -> str:
    """提取第一个一级标题"""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def yaml_quote(value: str) -> str:
    """YAML 字符串转义"""
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'


def generate_skill_metadata(name: str, source_name: str, source_text: str, skill_type: str = "standard") -> str:
    """
    生成 SKILL.md 的 frontmatter

    Args:
        name: skill 名称
        source_name: 源文件名
        source_text: 源文件内容
        skill_type: "standard" (skills.sh) 或 "codex"
    """
    existing, body = split_frontmatter(source_text)

    # 基础信息
    description = ""
    argument_hint = ""

    if existing:
        description = existing.get("description", "")
        argument_hint = existing.get("argument-hint", "")

    if not description:
        # 从标题生成描述
        title = first_heading(body, name)
        description = f"AI Trading skill: {title}"

    # skills.sh 标准格式
    if skill_type == "standard":
        metadata = "---\n"
        metadata += f"name: {name}\n"
        metadata += f"description: {yaml_quote(description)}\n"
        if argument_hint:
            metadata += f"metadata:\n"
            metadata += f"  argument-hint: {yaml_quote(argument_hint)}\n"
        metadata += "---\n\n"
        return metadata

    # Codex 格式（保留更多信息）
    else:
        metadata = "---\n"
        metadata += f"name: {name}\n"
        metadata += f"description: {yaml_quote(description)}\n"
        if argument_hint:
            metadata += f"argument-hint: {yaml_quote(argument_hint)}\n"
        metadata += f"source: skills/{source_name}\n"
        metadata += "---\n\n"
        return metadata


def generate_skill_body(name: str, source_name: str, source_text: str, skill_type: str = "standard") -> str:
    """
    生成 SKILL.md 的正文

    Args:
        skill_type: "standard" (skills.sh) 或 "codex"
    """
    _, body = split_frontmatter(source_text)

    if skill_type == "codex":
        # Codex 需要适配说明
        note = (
            "## Codex Adapter Note\n\n"
            f"This skill is generated from `skills/{source_name}` for Codex compatibility.\n\n"
            "- Treat `$ARGUMENTS` as the user's request in the current conversation.\n"
            "- When the source mentions Claude-specific features (Task, Agent, WebSearch), "
            "use the closest Codex equivalent.\n"
            "- Tool paths like `__AITRADING_HOME__` should be resolved to your installation path.\n\n"
        )
        return note + body.rstrip() + "\n"

    # skills.sh 标准格式：直接使用正文，但要清理 Claude 特定的占位符
    cleaned_body = body.replace("__AITRADING_HOME__", "$HOME/.ai-trading")
    cleaned_body = re.sub(
        r"你是 \*\*ai-trading (.*?)\*\*",
        r"You are the **ai-trading \1**",
        cleaned_body
    )

    return cleaned_body.rstrip() + "\n"


def convert_skill(source_path: Path, skill_type: str = "standard") -> tuple[str, str]:
    """
    转换单个 skill

    Returns:
        (metadata, body) 元组
    """
    name = source_path.stem
    source_name = source_path.name
    source_text = source_path.read_text(encoding="utf-8")

    metadata = generate_skill_metadata(name, source_name, source_text, skill_type)
    body = generate_skill_body(name, source_name, source_text, skill_type)

    return metadata, body


def sync_codex_skills():
    """同步到 Codex 格式（codex-skills/）"""
    print("📦 Syncing Codex skills...")
    CODEX_SKILLS.mkdir(exist_ok=True)

    count = 0
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        skill_dir = CODEX_SKILLS / name
        skill_dir.mkdir(exist_ok=True)

        metadata, body = convert_skill(source, skill_type="codex")
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(metadata + body, encoding="utf-8")

        count += 1
        print(f"  ✓ {name}")

    print(f"✅ Synced {count} Codex skills to {CODEX_SKILLS}/\n")


def sync_standard_skills():
    """同步到 skills.sh 标准格式（.agents/skills/）"""
    print("🌐 Syncing skills.sh standard format...")
    STANDARD_SKILLS.mkdir(parents=True, exist_ok=True)

    count = 0
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        skill_dir = STANDARD_SKILLS / name
        skill_dir.mkdir(exist_ok=True)

        metadata, body = convert_skill(source, skill_type="standard")
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(metadata + body, encoding="utf-8")

        count += 1
        print(f"  ✓ {name}")

    print(f"✅ Synced {count} standard skills to {STANDARD_SKILLS}/\n")


def main():
    """主函数"""
    if "--check" in sys.argv[1:]:
        print("🔍 Check mode: verifying skill conversion...")
        # 这里可以添加验证逻辑
        return

    print("🔄 AI Trading Skills Sync\n")
    print(f"📁 Source: {CLAUDE_SKILLS}/")
    print(f"📁 Codex: {CODEX_SKILLS}/")
    print(f"📁 Standard: {STANDARD_SKILLS}/\n")

    if not CLAUDE_SKILLS.exists():
        print(f"❌ Error: {CLAUDE_SKILLS} not found")
        sys.exit(1)

    skills = list(CLAUDE_SKILLS.glob("*.md"))
    if not skills:
        print(f"❌ Error: No .md files found in {CLAUDE_SKILLS}")
        sys.exit(1)

    print(f"Found {len(skills)} skills to sync\n")

    # 执行同步
    sync_codex_skills()
    sync_standard_skills()

    print("🎉 All skills synced successfully!")


if __name__ == "__main__":
    main()
