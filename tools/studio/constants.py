"""Studio sidecar constants. Not Frozen Schema."""

from __future__ import annotations

from pathlib import Path

CONTRACT_VERSION = "studio-0.1"
REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
VENDOR_DIR = STATIC_DIR / "vendor"
VENDOR_TYPES = {
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
}
PROBLEM_DIR = "02_题目库"
KNOWLEDGE_DIR = "01_知识库"
METHOD_DIR = "12_方法库"
PROJECT_DIR = "07_项目"
TEMPLATE_DIR = "_模板"
WORKFLOW_DIRS = ("未解决", "研究中", "已解决")
RESERVED_IDS = frozenset({"P0000", "K0000", "M0000"})
STATIC_FILES = frozenset({"index.html", "styles.css", "app.js"})
LAB_PROBLEMS_DIR = REPO_ROOT / "tools" / "research_lab" / "problems"
