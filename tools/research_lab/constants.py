"""v2.2-lab research-lab constants."""

from __future__ import annotations

from pathlib import Path

CONTRACT_VERSION = "2.2-lab"
REPO_ROOT = Path(__file__).resolve().parents[2]
USAGE_GUIDE_PATH = REPO_ROOT / "10_提示词" / "Research_Lab_Usage_Guide.md"
SPEC_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-08-28-research-lab-maturity-design.md"
)
LEAN_ROOT = REPO_ROOT / "06_LEAN形式化"
CORRESPONDENCE_PATH = LEAN_ROOT / "correspondence.yaml"
FIDELITY_FIXTURE = (
    REPO_ROOT / "tests" / "research_lab" / "fixtures" / "fidelity" / "p001_suite.yaml"
)
PROBLEM_REGISTRY = REPO_ROOT / "tools" / "research_lab" / "problems" / "PROB-SF-001.yaml"
PROBLEMS_DIR = REPO_ROOT / "tools" / "research_lab" / "problems"
CONJECTURES_DIR = REPO_ROOT / "tools" / "research_lab" / "conjectures"
LITERATURE_DIR = REPO_ROOT / "tools" / "research_lab" / "literature"
EXPERTS_DIR = REPO_ROOT / "tools" / "research_lab" / "experts"
PAPERS_DIR = REPO_ROOT / "tools" / "research_lab" / "papers"
HOLDOUT_PATH = REPO_ROOT / "tools" / "research_lab" / "holdout.yaml"
TASK_REGISTRY = REPO_ROOT / "tools" / "research_lab" / "tasks" / "TASK-SF-001.yaml"
LOCKFILE_PATH = REPO_ROOT / "requirements.lock"
PROTOCOL_PATH = REPO_ROOT / "tools" / "research_lab" / "protocol.yaml"
FROZEN_SCHEMA_PATH = REPO_ROOT / "元数据规范.md"
PROJECT_RULES_PATH = REPO_ROOT / "项目规则.md"
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
FAILURE_JOURNAL_PATH = REPO_ROOT / "tools" / "research_lab" / "sidecars" / "failures.jsonl"
FRONTIER_PKG = REPO_ROOT / "packages" / "domain-frontier"
EXPLORATION_PKG = REPO_ROOT / "packages" / "domain-exploration"
EXPLORATION_DOCS = REPO_ROOT / "docs" / "research" / "exploration"

KEY_ROOTS: tuple[str, ...] = (
    "01_知识库",
    "02_题目库",
    "04_LATEX",
    "05_代码",
    "06_LEAN形式化",
    "07_项目",
    "08_成果输出",
    "tools",
    "tests",
    ".github/workflows",
)

SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {".git", ".lake", "__pycache__", ".venv", "node_modules", ".elan"}
)
