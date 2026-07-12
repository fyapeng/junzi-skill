#!/usr/bin/env python3
"""Validate the Junzi skill and its public repository with no third-party packages."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
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
    "evals/triggers.yaml",
    "evals/runs/2026-07-13-trigger-forward-test.md",
    "README.md",
    "README_EN.md",
    "GOVERNANCE.md",
    "CITATION.cff",
    "assets/junzi-seal.svg",
    "assets/readme-hero.svg",
    "assets/five-layers.svg",
    "assets/practice-loop.svg",
    "assets/portraits/intellectual-sources.webp",
    "assets/portraits/ATTRIBUTION.md",
    "website/package.json",
    "website/package-lock.json",
    "website/astro.config.mjs",
    "website/src/pages/index.astro",
    "website/src/styles/global.css",
    ".github/workflows/pages.yml",
    "LICENSE",
    "NOTICE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
]

BINARY_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
for required in REQUIRED_FILES:
    path = ROOT / required
    if path.suffix.lower() in BINARY_SUFFIXES:
        if not path.is_file():
            fail(f"missing file: {required}")
    else:
        read(required)

for relative in [
    "assets/junzi-seal.svg",
    "assets/readme-hero.svg",
    "assets/five-layers.svg",
    "assets/practice-loop.svg",
]:
    try:
        ET.parse(ROOT / relative)
    except ET.ParseError as exc:
        fail(f"invalid SVG XML: {relative}: {exc}")

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

triggers = read("evals/triggers.yaml")
trigger_count = len(re.findall(r"(?m)^  - id: JZ-T\d{2}$", triggers))
if trigger_count < 12:
    fail(f"evals/triggers.yaml must retain at least twelve trigger cases; found {trigger_count}")
for kind in ["positive", "negative", "continuity", "coexistence", "security"]:
    if f"kind: {kind}" not in triggers:
        fail(f"evals/triggers.yaml is missing trigger kind: {kind}")

governance = read("GOVERNANCE.md")
for phrase in ["个人负责", "道之所向", "外部反馈"]:
    if phrase not in governance:
        fail(f"GOVERNANCE.md is missing governance concept: {phrase}")

website = read("website/src/pages/index.astro")
for phrase in ["道法势术器", "退回最近仍成立的节点", "广用其器", "fyapeng/junzi-skill"]:
    if phrase not in website:
        fail(f"website is missing core Junzi presentation: {phrase}")

astro_config = read("website/astro.config.mjs")
for phrase in ['site: "https://fyapeng.com"', 'base: "/junzi-skill"']:
    if phrase not in astro_config:
        fail(f"Astro Pages configuration is missing: {phrase}")

pages_workflow = read(".github/workflows/pages.yml")
for phrase in ["withastro/action@v6", "actions/deploy-pages@v5", "path: website"]:
    if phrase not in pages_workflow:
        fail(f"Pages workflow is missing: {phrase}")

interface = read("agents/openai.yaml")
for phrase in ["display_name:", "short_description:", "default_prompt:", "$junzi", "allow_implicit_invocation: true"]:
    if phrase not in interface:
        fail(f"agents/openai.yaml is missing: {phrase}")

license_text = read("LICENSE")
if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
    fail("LICENSE is not recognizable as Apache License 2.0")

citation = read("CITATION.cff")
version_match = re.search(r"(?m)^version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", citation)
project_version = version_match.group(1) if version_match else ""
if not project_version:
    fail("CITATION.cff is missing a semantic project version")
if project_version and f"## [{project_version}]" not in read("CHANGELOG.md"):
    fail(f"CHANGELOG.md has no release section for {project_version}")
try:
    website_package = json.loads(read("website/package.json"))
    if website_package.get("version") != project_version:
        fail(
            "website/package.json version does not match CITATION.cff: "
            f"{website_package.get('version')} != {project_version}"
        )
except json.JSONDecodeError as exc:
    fail(f"website/package.json is invalid JSON: {exc}")
try:
    website_lock = json.loads(read("website/package-lock.json"))
    lock_root_version = website_lock.get("packages", {}).get("", {}).get("version")
    if website_lock.get("version") != project_version or lock_root_version != project_version:
        fail("website/package-lock.json root versions do not match CITATION.cff")
except json.JSONDecodeError as exc:
    fail(f"website/package-lock.json is invalid JSON: {exc}")

link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
IGNORED_PARTS = {".git", "node_modules", "dist"}
for markdown in ROOT.rglob("*.md"):
    if IGNORED_PARTS.intersection(markdown.parts):
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
    if not path.is_file() or IGNORED_PARTS.intersection(path.parts):
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
    f"{case_count} recorded evaluations, {red_team_count} red-team cases, {trigger_count} trigger cases, "
    "and repository-relative Markdown links."
)
