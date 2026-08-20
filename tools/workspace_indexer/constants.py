"""Constants for Workspace Indexer v1."""

from __future__ import annotations

INDEXER_VERSION = "1.5"
INDEX_DIR_RELATIVE = "09_长期记忆/自动索引"
GENERATED_HEADER = """\
<!--
GENERATED FILE — DO NOT EDIT MANUALLY
Generator: tools.workspace_indexer
Source of truth: validated repository objects and filesystem
Regenerate with:
python -m tools.workspace_indexer rebuild
python -m tools.workspace_indexer sync
-->
"""

MANAGED_FILES: tuple[str, ...] = (
    "项目统计.md",
    "知识索引.md",
    "题目索引.md",
    "成果索引.md",
    "证据索引.md",
    "方法索引.md",
    "学习证据状态.md",
    "知识关联证据.md",
    "知识关系.md",
)

OUTCOME_VALUES: tuple[str, ...] = (
    "correct",
    "incorrect",
    "partial",
    "unsolved",
    "abandoned",
    "unassessed",
)

ASSISTANCE_OMITTED_LABEL = "not reliably recorded"

PROBLEM_DIR = "02_题目库"
OUTPUT_DIR = "08_成果输出"
LATEX_DIR = "04_LATEX"
WORKFLOW_DIRS: frozenset[str] = frozenset({"未解决", "研究中", "已解决"})

IMAGE_EXTENSIONS: frozenset[str] = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"})
