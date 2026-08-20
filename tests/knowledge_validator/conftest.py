"""Shared fixtures for Knowledge Validator tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest


def write_project(root: Path) -> Path:
    """Create a minimal MATH-AI-LAB-like project root."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "元数据规范.md").write_text("# schema\n", encoding="utf-8")
    kb = root / "01_知识库"
    kb.mkdir(parents=True, exist_ok=True)
    (kb / "知识库模板.md").write_text(
        dedent(
            """\
            ---
            schema_version: 1
            id: K0000
            type: knowledge
            title: 模板
            aliases: []
            status: draft
            created: 2026-08-19
            updated: 2026-08-19
            ---

            template body
            """
        ),
        encoding="utf-8",
    )
    return root


def knowledge_md(
    *,
    kid: str,
    title: str = "示例",
    status: str = "draft",
    extras: str = "",
    aliases: str | None = None,
) -> str:
    lines = [
        "---",
        "schema_version: 1",
        f"id: {kid}",
        "type: knowledge",
        f"title: {title}",
    ]
    if aliases is not None:
        lines.append("aliases:")
        if aliases.strip():
            for a in aliases.split("|"):
                lines.append(f"  - {a}")
        else:
            # aliases: [] via empty marker
            lines[-1] = "aliases: []"
    lines.extend(
        [
            f"status: {status}",
            "created: 2026-08-19",
            "updated: 2026-08-19",
        ]
    )
    if extras:
        lines.append(extras.rstrip("\n"))
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    return "\n".join(lines) + "\n"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return write_project(tmp_path)
