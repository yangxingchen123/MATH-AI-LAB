"""Render WorkspaceSnapshot to deterministic Markdown."""

from __future__ import annotations

from tools.derived_evidence.constants import ASSISTANCE_CATEGORIES, OUTCOME_CATEGORIES
from tools.derived_evidence.models import DerivedEvidenceSnapshot, TargetKey
from tools.knowledge_relations.models import KnowledgeRelationSnapshot, RelationEdge

from .constants import ASSISTANCE_OMITTED_LABEL, GENERATED_HEADER, OUTCOME_VALUES
from .models import WorkspaceSnapshot


def _header() -> str:
    return GENERATED_HEADER + "\n"


def render_project_statistics(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 项目统计",
        "",
        "> Generated from repository state.",
        "",
        "## Knowledge",
        "",
        f"- total: {len(snapshot.knowledge_rows)}",
    ]
    for status in sorted(snapshot.knowledge_status_counts):
        lines.append(f"- {status}: {snapshot.knowledge_status_counts[status]}")

    lines.extend(["", "## Problems", "", f"- total: {len(snapshot.problem_rows)}"])
    for status in sorted(snapshot.problem_yaml_status_counts):
        lines.append(f"- YAML {status}: {snapshot.problem_yaml_status_counts[status]}")
    for wf in sorted(snapshot.problem_workflow_counts):
        lines.append(f"- operational {wf}: {snapshot.problem_workflow_counts[wf]}")

    lines.extend(
        [
            "",
            "## Attempts",
            "",
            f"- total: {len(snapshot.attempt_rows)}",
            "",
            "By outcome:",
        ]
    )
    for outcome in OUTCOME_VALUES:
        lines.append(f"- {outcome}: {snapshot.attempt_outcome_counts.get(outcome, 0)}")

    lines.extend(["", "By assistance:"])
    for label in ("independent", "assisted", ASSISTANCE_OMITTED_LABEL):
        lines.append(f"- {label}: {snapshot.attempt_assistance_counts.get(label, 0)}")

    lines.extend(["", "## Methods", "", f"- total: {len(snapshot.method_rows)}"])
    for status in sorted(snapshot.method_status_counts):
        lines.append(f"- {status}: {snapshot.method_status_counts[status]}")

    lines.extend(
        [
            "",
            "## LaTeX",
            "",
            f"- project count: {snapshot.latex_project_count}",
            "",
            "## Published outputs",
            "",
            f"- PDF count: {snapshot.pdf_count}",
            f"- image count: {snapshot.image_count}",
            "",
        ]
    )
    return "\n".join(lines)


def render_knowledge_index(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 知识索引",
        "",
        "| ID | Title | Status | Domain | Source path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in snapshot.knowledge_rows:
        title = row.title.replace("|", "\\|")
        domain = row.domain.replace("|", "\\|")
        lines.append(
            f"| {row.object_id} | {title} | {row.status} | {domain} | {row.source_path} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_problem_index(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 题目索引",
        "",
        "> YAML status ≠ Operational workflow.",
        "",
        "| ID | Title | YAML status | Operational workflow | Parts | Attempts | Source path |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in snapshot.problem_rows:
        title = row.title.replace("|", "\\|")
        lines.append(
            f"| {row.object_id} | {title} | {row.yaml_status} | "
            f"{row.operational_workflow} | {row.parts} | {row.attempt_count} | {row.source_path} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_evidence_index(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 证据索引",
        "",
        "| Attempt ID | Problem | Target | Outcome | Assistance | Attempted At | Source path |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in snapshot.attempt_rows:
        lines.append(
            f"| {row.object_id} | {row.problem_id} | {row.target} | {row.outcome} | "
            f"{row.assistance} | {row.attempted_at} | {row.source_path} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_method_index(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 方法索引",
        "",
        "> Generated navigation view. Source of truth: `12_方法库/` via Method Validator.",
        "",
        "| Method ID | Title | Status | Knowledge | Source path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in snapshot.method_rows:
        title = row.title.replace("|", "\\|")
        lines.append(
            f"| {row.object_id} | {title} | {row.status} | {row.knowledge} | {row.source_path} |"
        )
    lines.append("")
    return "\n".join(lines)


def _format_count_map(counts: dict[str, int], categories: tuple[str, ...]) -> str:
    return " · ".join(f"{name}={counts.get(name, 0)}" for name in categories)


def _format_part_counts(part_counts: dict[str, int]) -> str:
    if not part_counts:
        return "—"
    return ", ".join(f"{part}={count}" for part, count in part_counts.items())


def _target_display(key: TargetKey) -> str:
    if key.part is None:
        return f"{key.problem_id} / whole"
    return f"{key.problem_id} / {key.part}"


def _target_sort_keys(
    snapshot: WorkspaceSnapshot,
) -> list[TargetKey]:
    problem_parts: dict[str, list[str]] = {}
    for row in snapshot.problem_rows:
        if row.parts:
            problem_parts[row.object_id] = [p.strip() for p in row.parts.split(",") if p.strip()]

    def sort_key(key: TargetKey) -> tuple:
        declared = problem_parts.get(key.problem_id, [])
        if key.part is None:
            return (key.problem_id, 0, 0)
        if key.part in declared:
            return (key.problem_id, 1, declared.index(key.part))
        return (key.problem_id, 1, 999)

    derived = snapshot.derived_evidence
    if derived is None:
        return []
    return sorted(derived.target_states.keys(), key=sort_key)


def render_learning_evidence_state(snapshot: WorkspaceSnapshot) -> str:
    derived: DerivedEvidenceSnapshot | None = snapshot.derived_evidence
    lines = [
        _header().rstrip(),
        "",
        "# 学习证据状态",
        "",
        "> AUTO-GENERATED · DESCRIPTIVE DERIVED VIEW · NOT SOURCE OF TRUTH",
        "> Rebuildable from validated Attempt/Problem evidence via Descriptive Evidence State v1.",
        "",
    ]
    if derived is None or (not derived.target_states and not derived.problem_rollups):
        lines.extend(["No descriptive evidence available.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "## Target Evidence",
            "",
            "| Target | Attempts | Outcomes | Assistance |",
            "| --- | --- | --- | --- |",
        ]
    )
    for key in _target_sort_keys(snapshot):
        state = derived.target_states[key]
        target = _target_display(key)
        attempts = ", ".join(state.attempt_ids)
        outcomes = _format_count_map(dict(state.outcome_counts), OUTCOME_CATEGORIES)
        assistance = _format_count_map(dict(state.assistance_counts), ASSISTANCE_CATEGORIES)
        lines.append(f"| {target} | {attempts} | {outcomes} | {assistance} |")

    lines.extend(
        [
            "",
            "## Problem Evidence Rollup",
            "",
            "| Problem | Attempts | Whole Attempts | Attempted Parts | Part Attempt Counts | Outcomes | Assistance |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for problem_id in sorted(derived.problem_rollups):
        rollup = derived.problem_rollups[problem_id]
        attempts = ", ".join(rollup.attempt_ids)
        parts = ", ".join(rollup.attempted_parts) if rollup.attempted_parts else "—"
        part_counts = _format_part_counts(dict(rollup.part_attempt_counts))
        outcomes = _format_count_map(dict(rollup.outcome_counts), OUTCOME_CATEGORIES)
        assistance = _format_count_map(dict(rollup.assistance_counts), ASSISTANCE_CATEGORIES)
        lines.append(
            f"| {problem_id} | {attempts} | {rollup.whole_problem_attempt_count} | "
            f"{parts} | {part_counts} | {outcomes} | {assistance} |"
        )

    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "| Target / Problem | Attempt IDs |",
            "| --- | --- |",
        ]
    )
    for key in _target_sort_keys(snapshot):
        state = derived.target_states[key]
        lines.append(f"| {_target_display(key)} | {', '.join(state.attempt_ids)} |")
    for problem_id in sorted(derived.problem_rollups):
        rollup = derived.problem_rollups[problem_id]
        lines.append(f"| {problem_id} (rollup) | {', '.join(rollup.attempt_ids)} |")

    lines.append("")
    return "\n".join(lines)


def _knowledge_titles(snapshot: WorkspaceSnapshot) -> dict[str, str]:
    return {row.object_id: row.title for row in snapshot.knowledge_rows}


def render_knowledge_associated_evidence(snapshot: WorkspaceSnapshot) -> str:
    ka = snapshot.knowledge_associated_evidence
    titles = _knowledge_titles(snapshot)
    lines = [
        _header().rstrip(),
        "",
        "# 知识关联证据",
        "",
        "> AUTO-GENERATED · DESCRIPTIVE ASSOCIATION VIEW · NOT SOURCE OF TRUTH",
        "> Formal whole-target Attempt → Problem.knowledge → Knowledge association only.",
        "> Not mastery · not assessment · not correctness of Knowledge.",
        "",
    ]
    if ka is None or not ka.knowledge_rollups:
        lines.extend(["No knowledge-associated evidence available.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "## Knowledge Associated Evidence",
            "",
            "| Knowledge | Associated Attempts | Associated Outcomes | Associated Assistance |",
            "| --- | --- | --- | --- |",
        ]
    )
    for kid in sorted(ka.knowledge_rollups):
        rollup = ka.knowledge_rollups[kid]
        title = titles.get(kid, "")
        label = f"{kid} — {title}" if title else kid
        label = label.replace("|", "\\|")
        attempts = ", ".join(rollup.associated_attempt_ids)
        outcomes = _format_count_map(dict(rollup.associated_outcome_counts), OUTCOME_CATEGORIES)
        assistance = _format_count_map(dict(rollup.associated_assistance_counts), ASSISTANCE_CATEGORIES)
        lines.append(f"| {label} | {attempts} | {outcomes} | {assistance} |")

    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "| Knowledge | Associated Attempt IDs |",
            "| --- | --- |",
        ]
    )
    for kid in sorted(ka.knowledge_rollups):
        rollup = ka.knowledge_rollups[kid]
        lines.append(f"| {kid} | {', '.join(rollup.associated_attempt_ids)} |")

    lines.append("")
    return "\n".join(lines)


def _relation_titles(snapshot: WorkspaceSnapshot) -> dict[str, str]:
    titles: dict[str, str] = {}
    for row in snapshot.knowledge_rows:
        titles[row.object_id] = row.title
    for row in snapshot.problem_rows:
        titles[row.object_id] = row.title
    for row in snapshot.method_rows:
        titles[row.object_id] = row.title
    return titles


def _label(object_id: str, titles: dict[str, str]) -> str:
    title = titles.get(object_id, "")
    if title:
        return f"{object_id} — {title.replace('|', '\\|')}"
    return object_id


def render_knowledge_relations(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 知识关系",
        "",
        "> Formal Relation Derived View — from Frozen + Validated structured relations only.",
        "",
    ]
    kr: KnowledgeRelationSnapshot | None = snapshot.knowledge_relations
    titles = _relation_titles(snapshot)
    edges: tuple[RelationEdge, ...] = kr.edges if kr is not None else ()

    if not edges:
        lines.extend(["No formal knowledge relations available.", ""])
        return "\n".join(lines)

    relation_counts: dict[str, int] = {}
    for edge in edges:
        relation_counts[edge.relation] = relation_counts.get(edge.relation, 0) + 1

    lines.extend(["## Summary", ""])
    for relation in sorted(relation_counts):
        lines.append(f"- {relation}: {relation_counts[relation]}")
    lines.append("")

    lines.extend(
        [
            "## Formal Relations",
            "",
            "| Source | Relation | Target |",
            "| --- | --- | --- |",
        ]
    )
    for edge in edges:
        lines.append(
            f"| {_label(edge.source_id, titles)} | {edge.relation} | {_label(edge.target_id, titles)} |"
        )
    lines.append("")

    incident: dict[str, list[RelationEdge]] = {}
    for edge in edges:
        incident.setdefault(edge.source_id, []).append(edge)
        incident.setdefault(edge.target_id, []).append(edge)

    knowledge_ids = sorted(
        kid
        for kid in incident
        if kid.startswith("K") and incident[kid]
    )
    if knowledge_ids:
        lines.extend(["## Knowledge Neighborhoods", ""])
        for kid in knowledge_ids:
            title = titles.get(kid, "")
            heading = f"### {kid} — {title}" if title else f"### {kid}"
            lines.append(heading)
            lines.append("")

            outgoing_prereq = sorted(
                e.target_id
                for e in edges
                if e.source_id == kid and e.relation == "prerequisites"
            )
            if outgoing_prereq:
                lines.append("Prerequisites:")
                for tid in outgoing_prereq:
                    lines.append(f"- {_label(tid, titles)}")
                lines.append("")

            outgoing_related = sorted(
                e.target_id
                for e in edges
                if e.source_id == kid and e.relation == "related"
            )
            if outgoing_related:
                lines.append("Related Knowledge:")
                for tid in outgoing_related:
                    lines.append(f"- {_label(tid, titles)}")
                lines.append("")

            incoming_related = sorted(
                e.source_id
                for e in edges
                if e.target_id == kid and e.relation == "related"
            )
            if incoming_related:
                lines.append("Incoming Related:")
                for sid in incoming_related:
                    lines.append(f"- {_label(sid, titles)}")
                lines.append("")

            incoming_prereq = sorted(
                e.source_id
                for e in edges
                if e.target_id == kid and e.relation == "prerequisites"
            )
            if incoming_prereq:
                lines.append("Required by:")
                for sid in incoming_prereq:
                    lines.append(f"- {_label(sid, titles)}")
                lines.append("")

            incoming_problems = sorted(
                e.source_id
                for e in edges
                if e.target_id == kid and e.relation == "knowledge" and e.source_id.startswith("P")
            )
            if incoming_problems:
                lines.append("Incoming Problems:")
                for sid in incoming_problems:
                    lines.append(f"- {_label(sid, titles)}")
                lines.append("")

            incoming_methods = sorted(
                e.source_id
                for e in edges
                if e.target_id == kid and e.relation == "knowledge" and e.source_id.startswith("M")
            )
            if incoming_methods:
                lines.append("Incoming Methods:")
                for sid in incoming_methods:
                    lines.append(f"- {_label(sid, titles)}")
                lines.append("")

    return "\n".join(lines)


def render_output_index(snapshot: WorkspaceSnapshot) -> str:
    lines = [
        _header().rstrip(),
        "",
        "# 成果索引",
        "",
        f"- PDF total: {snapshot.pdf_count}",
        f"- image total: {snapshot.image_count}",
        "",
        "| Relative path | Type | Filename |",
        "| --- | --- | --- |",
    ]
    for row in snapshot.output_rows:
        lines.append(f"| {row.relative_path} | {row.kind} | {row.filename} |")
    lines.append("")
    return "\n".join(lines)


def render_all(snapshot: WorkspaceSnapshot) -> dict[str, str]:
    return {
        "项目统计.md": render_project_statistics(snapshot),
        "知识索引.md": render_knowledge_index(snapshot),
        "题目索引.md": render_problem_index(snapshot),
        "成果索引.md": render_output_index(snapshot),
        "证据索引.md": render_evidence_index(snapshot),
        "方法索引.md": render_method_index(snapshot),
        "学习证据状态.md": render_learning_evidence_state(snapshot),
        "知识关联证据.md": render_knowledge_associated_evidence(snapshot),
        "知识关系.md": render_knowledge_relations(snapshot),
    }
