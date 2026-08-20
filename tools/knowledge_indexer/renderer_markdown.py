"""Deterministic Markdown renderers for the derived Knowledge index."""

from __future__ import annotations

from pathlib import PurePosixPath

from .constants import GENERATED_BANNER
from .models import KnowledgeIndexEntry, KnowledgeIndexModel


def escape_table_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", "")


def link_to_source(entry: KnowledgeIndexEntry) -> str:
    """Markdown link from 01_知识库/_索引/ to the Knowledge file."""
    # entry.path like 01_知识库/数学变换/勒让德变换.md
    parts = PurePosixPath(entry.path).parts
    if len(parts) >= 2 and parts[0] == "01_知识库":
        rel = PurePosixPath(*([".."] + list(parts[1:])))
    else:
        rel = PurePosixPath("..") / PurePosixPath(entry.path).name
    href = rel.as_posix()
    label = escape_table_cell(entry.title)
    return f"[{label}]({href})"


def _fmt_id_list(ids: list[str] | None) -> str:
    if ids is None:
        return "—"
    if not ids:
        return "[]"
    return ", ".join(ids)


def render_readme(model: KnowledgeIndexModel) -> str:
    lines: list[str] = []
    lines.append("# Knowledge 自动索引")
    lines.append("")
    lines.append(f"> {GENERATED_BANNER}")
    lines.append("")
    lines.append("## 1. 总体统计")
    lines.append("")
    lines.append(f"- Knowledge objects: {model.knowledge_objects}")
    lines.append(f"- Domains (非空): {len(model.domains)}")
    lines.append(f"- Without domain: {len(model.without_domain)}")
    lines.append(f"- Prerequisite edges: {model.prerequisite_edges}")
    lines.append(f"- Related declared edges: {model.related_declared_edges}")
    lines.append(
        f"- Related effective edges (undirected pairs): {model.related_effective_edges}"
    )
    lines.append(f"- Source metadata SHA-256: `{model.source_metadata_sha256}`")
    lines.append("")
    lines.append("## 2. Knowledge 总表")
    lines.append("")
    lines.append(
        "| ID | 标题 | Status | Domain | Prerequisites | Required By | Related |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for kid in sorted(model.entries.keys()):
        e = model.entries[kid]
        domain = escape_table_cell(e.domain) if e.domain else "—"
        lines.append(
            "| "
            + " | ".join(
                [
                    kid,
                    link_to_source(e),
                    escape_table_cell(e.status),
                    domain,
                    escape_table_cell(_fmt_id_list(e.prerequisites)),
                    escape_table_cell(_fmt_id_list(e.required_by)),
                    escape_table_cell(_fmt_id_list(e.related)),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## 3. Status 统计")
    lines.append("")
    for st in ("draft", "reviewed", "archived"):
        lines.append(f"- {st}: {model.status_counts.get(st, 0)}")
    lines.append("")
    lines.append("## 4. Domain 统计")
    lines.append("")
    for domain in sorted(model.domains.keys()):
        lines.append(f"- {escape_table_cell(domain)}: {len(model.domains[domain])}")
    if model.without_domain:
        lines.append(f"- 未设置 domain: {len(model.without_domain)}")
    elif not model.domains:
        lines.append("- （无）")
    lines.append("")
    lines.append("## 5. 关系统计")
    lines.append("")
    lines.append(f"- prerequisite_edges: {model.prerequisite_edges}")
    lines.append(f"- related_declared_edges: {model.related_declared_edges}")
    lines.append(
        f"- related_effective_edges (无向 pair): {model.related_effective_edges}"
    )
    lines.append("")
    lines.append("## 6. 使用说明")
    lines.append("")
    lines.append("- 本目录为 **DERIVED / GENERATED DATA**，可随时删除并用 Indexer 重建。")
    lines.append("- Knowledge YAML Metadata 是权威事实源；索引不得反向写回 Knowledge。")
    lines.append("- `required_by` / `related_effective` 仅为派生视图。")
    lines.append("- 请勿在 `_索引/` 中放置手工文件。")
    lines.append("- 重建：`python -m tools.knowledge_indexer build`")
    lines.append("- 检查是否过期：`python -m tools.knowledge_indexer check`")
    lines.append("")
    return "\n".join(lines)


def render_by_domain(model: KnowledgeIndexModel) -> str:
    lines: list[str] = []
    lines.append("# 按领域索引")
    lines.append("")
    lines.append(f"> {GENERATED_BANNER}")
    lines.append("")
    for domain in sorted(model.domains.keys()):
        lines.append(f"## {domain}")
        lines.append("")
        for kid in model.domains[domain]:
            e = model.entries[kid]
            lines.append(f"- {kid} {link_to_source(e)}")
        lines.append("")
    lines.append("## 未设置 domain")
    lines.append("")
    if not model.without_domain:
        lines.append("- （无）")
        lines.append("")
    else:
        for kid in model.without_domain:
            e = model.entries[kid]
            lines.append(f"- {kid} {link_to_source(e)}")
        lines.append("")
    return "\n".join(lines)


def render_relations(model: KnowledgeIndexModel) -> str:
    lines: list[str] = []
    lines.append("# 关系索引")
    lines.append("")
    lines.append(f"> {GENERATED_BANNER}")
    lines.append("")
    lines.append(
        "说明：`Prerequisites` / `Related Declared` 来自 YAML 事实；"
        "`Required By` / `Related Effective` 为派生视图，禁止写回 Knowledge。"
    )
    lines.append("")
    lines.append(
        "| ID | Title | Prerequisites | Required By | Related Declared | Related Effective |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for kid in sorted(model.entries.keys()):
        e = model.entries[kid]
        lines.append(
            "| "
            + " | ".join(
                [
                    kid,
                    link_to_source(e),
                    escape_table_cell(_fmt_id_list(e.prerequisites)),
                    escape_table_cell(_fmt_id_list(e.required_by)),
                    escape_table_cell(_fmt_id_list(e.related)),
                    escape_table_cell(_fmt_id_list(e.related_effective)),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def render_all_markdown(model: KnowledgeIndexModel) -> dict[str, str]:
    return {
        "README.md": render_readme(model),
        "按领域.md": render_by_domain(model),
        "关系索引.md": render_relations(model),
    }
