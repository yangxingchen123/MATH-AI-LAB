"""Register papers under 03_参考资料. Does not parse PDF into Knowledge."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = REPO_ROOT / "03_参考资料"
IDENTITY_TEMPLATE = REFERENCE_ROOT / "_模板" / "文献条目_v1.md"
TAXONOMY_DIRS: tuple[str, ...] = ("教材", "论文", "竞赛", "讲义")
CONTRACT_VERSION = "0.1"
