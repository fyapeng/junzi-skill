#!/usr/bin/env python3
"""Validate the Junzi skill and its public repository with no third-party packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing file: {relative}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"not valid UTF-8: {relative}: {exc}")
        return ""


REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/CHARTER.md",
    "references/PRACTICE_PROTOCOL.md",
    "references/SOURCE_MAP.md",
    "references/EVALUATION.md",
    "evals/cases.yaml",
    "README.md",
    "README_EN.md",
    "GOVERNANCE.md",
    "CITATION.cff",
    "assets/junzi-seal.svg",
    "LICENSE",
    "NOTICE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
]

for required in REQUIRED_FILES:
    read(required)

skill = read("SKILL.md")
frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", skill, re.DOTALL)
if not frontmatter:
    fail("SKILL.md must begin with YAML frontmatter")
else:
    fields = []
    for line in frontmatter.group(1).splitlines():
        if line and not line[0].isspace() and ":" in line:
            fields.append(line.split(":", 1)[0].strip())
    if fields != ["name", "description"]:
        fail(f"SKILL.md frontmatter fields must be name, description; found {fields}")
    if not re.search(r"(?m)^name:\s*junzi\s*$", frontmatter.group(1)):
        fail("SKILL.md name must be junzi")
    description = re.search(r"(?m)^description:\s*(.+)$", frontmatter.group(1))
    if not description or len(description.group(1).strip()) < 80:
        fail("SKILL.md description must explain capability and triggering context")

if len(skill.splitlines()) >= 500:
    fail("SKILL.md must stay below 500 lines")

required_references = [
    "references/CHARTER.md",
    "references/PRACTICE_PROTOCOL.md",
    "references/SOURCE_MAP.md",
    "references/EVALUATION.md",
]
for reference in required_references:
    if f"`{reference}`" not in skill:
        fail(f"SKILL.md does not route to {reference}")

charter = read("references/CHARTER.md")
layers = ["道——", "法——", "势——", "术——", "器——"]
positions = [charter.find(layer) for layer in layers]
if any(position < 0 for position in positions) or positions != sorted(positions):
    fail("CHARTER.md must present 道、法、势、术、器 in hierarchical order")
for phrase in ["自强不息", "厚德载物", "道有恒而不僵", "君子自勉"]:
    if phrase not in charter:
        fail(f"CHARTER.md is missing core phrase: {phrase}")

protocol = read("references/PRACTICE_PROTOCOL.md")
for phrase in ["最小主线", "开放求知", "独立伙伴关系", "创造解决路径", "验省与层级诊断"]:
    if phrase not in protocol:
        fail(f"PRACTICE_PROTOCOL.md is missing section: {phrase}")

sources = read("references/SOURCE_MAP.md")
source_urls = set(re.findall(r"https://[^)\s]+", sources))
if len(source_urls) < 15:
    fail(f"SOURCE_MAP.md needs broad direct-source coverage; found {len(source_urls)} URLs")
for phrase in ["原典文本", "解释判断", "行为转化", "适用边界", "传统之间的张力"]:
    if phrase not in sources:
        fail(f"SOURCE_MAP.md is missing source-integrity concept: {phrase}")

evaluation = read("references/EVALUATION.md")
case_count = len(re.findall(r"(?m)^### JZ-E\d{2}", evaluation))
if case_count < 6:
    fail(f"EVALUATION.md must retain at least six recorded cases; found {case_count}")
for phrase in ["本轮不能证明", "后续非回归测试", "不为通过测试"]:
    if phrase not in evaluation:
        fail(f"EVALUATION.md is missing conservative validation language: {phrase}")

red_team = read("evals/cases.yaml")
red_team_count = len(re.findall(r"(?m)^  - id: JZ-R\d{2}$", red_team))
if red_team_count < 10:
    fail(f"evals/cases.yaml must retain at least ten red-team cases; found {red_team_count}")
for phrase in [
    "legitimate-goal-replacement",
    "evidence-defeats-authority",
    "tool-failure-honesty",
    "blocked-branch-backtracking",
    "tool-chain-capture-and-exit",
]:
    if phrase not in red_team:
        fail(f"evals/cases.yaml is missing core scenario: {phrase}")

governance = read("GOVERNANCE.md")
for phrase in ["个人负责", "道之所向", "外部反馈"]:
    if phrase not in governance:
        fail(f"GOVERNANCE.md is missing governance concept: {phrase}")

interface = read("agents/openai.yaml")
for phrase in ["display_name:", "short_description:", "default_prompt:", "$junzi"]:
    if phrase not in interface:
        fail(f"agents/openai.yaml is missing: {phrase}")

license_text = read("LICENSE")
if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
    fail("LICENSE is not recognizable as Apache License 2.0")

link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for markdown in ROOT.rglob("*.md"):
    if ".git" in markdown.parts:
        continue
    text = markdown.read_text(encoding="utf-8")
    for target in link_pattern.findall(text):
        target = target.strip().strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if relative and not (markdown.parent / relative).resolve().exists():
            fail(f"broken relative link: {markdown.relative_to(ROOT)} -> {target}")

marker_pattern = re.compile(r"\[TODO|TODO:|待完成")
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    if path.suffix.lower() not in {".md", ".yaml", ".yml"}:
        continue
    if marker_pattern.search(path.read_text(encoding="utf-8")):
        fail(f"unresolved placeholder in {path.relative_to(ROOT)}")

if ERRORS:
    print("Junzi validation failed:")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)

print(
    "Junzi validation passed: "
    f"{len(REQUIRED_FILES)} required files, {len(source_urls)} source links, "
    f"{case_count} recorded evaluations, {red_team_count} red-team cases, "
    "and repository-relative Markdown links."
)
