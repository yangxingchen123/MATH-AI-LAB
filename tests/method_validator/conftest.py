"""Shared fixtures for Method Validator tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest


def write_project(root: Path) -> Path:
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
    method_root = root / "12_方法库"
    method_root.mkdir(parents=True, exist_ok=True)
    return root


def knowledge_md(
    *,
    kid: str,
    title: str = "示例",
    status: str = "reviewed",
    extras: str = "",
) -> str:
    aliases = "aliases: []" if status == "reviewed" else ""
    domain = "domain: 凸分析" if status == "reviewed" else ""
    prereq = "prerequisites: []" if status == "reviewed" else ""
    related = "related: []" if status == "reviewed" else ""
    extra_lines = "\n".join(x for x in (aliases, domain, prereq, related, extras.rstrip()) if x)
    return (
        "---\n"
        "schema_version: 1\n"
        f"id: {kid}\n"
        "type: knowledge\n"
        f"title: {title}\n"
        f"{extra_lines}\n"
        f"status: {status}\n"
        "created: 2026-08-19\n"
        "updated: 2026-08-19\n"
        "---\n\n"
        f"# {title}\n"
    )


def method_md(
    *,
    mid: str = "M0001",
    title: str = "Test Method",
    status: str = "draft",
    extras: str = "",
    body: str = "body\n",
) -> str:
    extra = (extras.rstrip() + "\n") if extras.strip() else ""
    return (
        "---\n"
        "schema_version: 1\n"
        f"id: {mid}\n"
        "type: method\n"
        f"title: {title}\n"
        f"status: {status}\n"
        f"{extra}"
        "---\n\n"
        f"{body}"
    )


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return write_project(tmp_path)
