"""Problem-scoped Attempt Ledger loader (Storage Contract v1)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .constants import ID_PATTERN, PROBLEM_ID_PATTERN, STORAGE_FORMAT_LEDGER
from .discovery import is_ledger_filename, relative_to_root
from .models import AttemptDocument, Severity, ValidationIssue
from .parser import extract_front_matter, parse_yaml_mapping

SECTION_HEADING_RE = re.compile(r"^## (A\d{6})\s*$", re.MULTILINE)


@dataclass
class LedgerLoadResult:
    path: Path
    relative_path: str
    problem_id: str | None = None
    storage_format: str | None = None
    attempts: list[dict[str, Any]] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)
    section_order: list[str] = field(default_factory=list)
    preamble: str = ""
    issues: list[ValidationIssue] = field(default_factory=list)


def ledger_problem_id_from_filename(name: str) -> str | None:
    match = re.fullmatch(r"^(P\d{4})\.md$", name)
    return match.group(1) if match else None


def _issue(
    rule_id: str,
    message: str,
    rel: str,
    *,
    field: str | None = None,
    object_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        severity=Severity.ERROR,
        rule_id=rule_id,
        message=message,
        file=rel,
        field=field,
        object_id=object_id,
        details=details or {},
    )


def _attempt_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    attempted_at = record.get("attempted_at")
    ts = str(attempted_at) if attempted_at is not None else ""
    aid = str(record.get("id") or "")
    return (ts, aid)


def is_chronological(records: list[dict[str, Any]]) -> bool:
    keys = [_attempt_sort_key(r) for r in records]
    return keys == sorted(keys)


def parse_narrative_sections(body: str) -> tuple[str, dict[str, str], list[str]]:
    """Return preamble, section map, orphan section ids without metadata."""
    matches = list(SECTION_HEADING_RE.finditer(body))
    if not matches:
        return body.strip(), {}, []

    preamble = body[: matches[0].start()].strip()
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        aid = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[aid] = body[start:end].strip()
    return preamble, sections, list(sections.keys())


def load_ledger_file(path: Path, project_root: Path) -> LedgerLoadResult:
    rel = relative_to_root(path, project_root)
    text = path.read_text(encoding="utf-8")
    raw_yaml, body, extract_issues = extract_front_matter(text)
    result = LedgerLoadResult(path=path, relative_path=rel, issues=[])

    for issue in extract_issues:
        result.issues.append(
            ValidationIssue(
                severity=issue.severity,
                rule_id=issue.rule_id,
                message=issue.message,
                file=rel,
            )
        )
    if extract_issues or raw_yaml is None:
        if raw_yaml is None and not extract_issues:
            result.issues.append(
                _issue("A-PARSE-E005", "Attempt ledger must have YAML Front Matter.", rel)
            )
        return result

    data, parse_issues = parse_yaml_mapping(raw_yaml)
    for issue in parse_issues:
        result.issues.append(
            ValidationIssue(
                severity=issue.severity,
                rule_id=issue.rule_id,
                message=issue.message,
                file=rel,
            )
        )
    if data is None:
        return result

    result.storage_format = data.get("storage_format") if isinstance(data.get("storage_format"), str) else None
    result.problem_id = data.get("problem") if isinstance(data.get("problem"), str) else None
    attempts = data.get("attempts")
    if isinstance(attempts, list):
        result.attempts = [item for item in attempts if isinstance(item, dict)]
    elif attempts is not None:
        result.issues.append(
            _issue("A-LEDG-E004", "attempts must be a non-empty list.", rel, field="attempts")
        )

    preamble, sections, section_order = parse_narrative_sections(body)
    result.preamble = preamble
    result.sections = sections
    result.section_order = section_order
    return result


def validate_ledger_container(
    ledger: LedgerLoadResult,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    rel = ledger.relative_path
    filename = ledger.path.name

    if not is_ledger_filename(filename):
        issues.append(
            _issue(
                "A-LEDG-E001",
                f"Ledger filename must match P{{dddd}}.md, got {filename!r}.",
                rel,
            )
        )

    expected_pid = ledger_problem_id_from_filename(filename)
    if ledger.storage_format != STORAGE_FORMAT_LEDGER:
        issues.append(
            _issue(
                "A-LEDG-E002",
                f"storage_format must be {STORAGE_FORMAT_LEDGER!r}, got {ledger.storage_format!r}.",
                rel,
                field="storage_format",
            )
        )

    if not isinstance(ledger.problem_id, str) or re.fullmatch(PROBLEM_ID_PATTERN, ledger.problem_id) is None:
        issues.append(
            _issue(
                "A-LEDG-E003",
                f"Ledger problem must match {PROBLEM_ID_PATTERN}, got {ledger.problem_id!r}.",
                rel,
                field="problem",
            )
        )
    elif expected_pid is not None and ledger.problem_id != expected_pid:
        issues.append(
            _issue(
                "A-LEDG-E003",
                f"Ledger problem {ledger.problem_id!r} must match filename {expected_pid}.",
                rel,
                field="problem",
            )
        )

    if not ledger.attempts:
        issues.append(
            _issue("A-LEDG-E004", "attempts must be a non-empty list.", rel, field="attempts")
        )
        return issues

    seen_in_ledger: dict[str, int] = {}
    for index, record in enumerate(ledger.attempts):
        aid = record.get("id")
        if isinstance(aid, str):
            seen_in_ledger[aid] = seen_in_ledger.get(aid, 0) + 1
        rec_problem = record.get("problem")
        if (
            isinstance(ledger.problem_id, str)
            and isinstance(rec_problem, str)
            and rec_problem != ledger.problem_id
        ):
            issues.append(
                _issue(
                    "A-LEDG-E006",
                    f"attempts[{index}].problem {rec_problem!r} must equal ledger problem {ledger.problem_id!r}.",
                    rel,
                    field=f"attempts[{index}].problem",
                    object_id=str(aid) if isinstance(aid, str) else None,
                )
            )

    for aid, count in sorted(seen_in_ledger.items()):
        if count > 1:
            issues.append(
                _issue(
                    "A-LEDG-E005",
                    f"Duplicate Attempt ID {aid} within ledger.",
                    rel,
                    field="attempts",
                    object_id=aid,
                )
            )

    if not is_chronological(ledger.attempts):
        issues.append(
            _issue(
                "A-LEDG-E009",
                "attempts must be in canonical chronological order (attempted_at ascending; tie-break by A ID).",
                rel,
                field="attempts",
            )
        )

    metadata_ids = {
        str(record["id"])
        for record in ledger.attempts
        if isinstance(record.get("id"), str) and re.fullmatch(ID_PATTERN, record["id"])
    }
    section_ids = set(ledger.sections.keys())

    for aid in sorted(metadata_ids - section_ids):
        issues.append(
            _issue(
                "A-LEDG-E007",
                f"Attempt metadata {aid} has no narrative section ## {aid}.",
                rel,
                object_id=aid,
            )
        )

    for aid in sorted(section_ids - metadata_ids):
        issues.append(
            _issue(
                "A-LEDG-E008",
                f"Orphan narrative section ## {aid} has no matching metadata record.",
                rel,
                object_id=aid,
            )
        )

    body_order = ledger.section_order
    meta_order = [
        str(r.get("id"))
        for r in ledger.attempts
        if isinstance(r.get("id"), str)
    ]
    if body_order != meta_order:
        issues.append(
            _issue(
                "A-LEDG-E010",
                "Narrative section order must match frontmatter attempts order.",
                rel,
                field="attempts",
            )
        )

    return issues


def expand_ledger_to_documents(ledger: LedgerLoadResult) -> list[AttemptDocument]:
    documents: list[AttemptDocument] = []
    for record in ledger.attempts:
        aid = record.get("id")
        body = ledger.sections.get(str(aid), "") if isinstance(aid, str) else ""
        doc = AttemptDocument(
            path=ledger.path,
            relative_path=ledger.relative_path,
            data=dict(record),
            body=body,
            record_anchor=str(aid) if isinstance(aid, str) else None,
        )
        documents.append(doc)
    return documents


def collect_attempt_ids_from_ledgers(ledger_paths: list[Path], project_root: Path) -> list[str]:
    ids: list[str] = []
    for path in ledger_paths:
        loaded = load_ledger_file(path, project_root)
        for record in loaded.attempts:
            aid = record.get("id")
            if isinstance(aid, str):
                ids.append(aid)
    return ids


def allocate_next_attempt_id(project_root: Path) -> str:
    from .discovery import attempt_dir, discover_ledger_files

    ledger_paths = discover_ledger_files(project_root)
    used: set[int] = set()
    for path in ledger_paths:
        loaded = load_ledger_file(path, project_root)
        for record in loaded.attempts:
            aid = record.get("id")
            if isinstance(aid, str) and re.fullmatch(ID_PATTERN, aid):
                used.add(int(aid[1:]))
    next_num = max(used) + 1 if used else 1
    return f"A{next_num:06d}"


def serialize_ledger(
    *,
    problem_id: str,
    attempts: list[dict[str, Any]],
    sections: dict[str, str],
    title: str | None = None,
) -> str:
    ordered = sorted(attempts, key=_attempt_sort_key)
    front = {
        "storage_format": STORAGE_FORMAT_LEDGER,
        "problem": problem_id,
        "attempts": ordered,
    }
    yaml_text = yaml.dump(
        front,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    heading = title or f"# {problem_id} 尝试记录"
    parts = ["---", yaml_text, "---", "", heading, ""]
    for record in ordered:
        aid = str(record["id"])
        parts.append(f"## {aid}")
        parts.append("")
        parts.append(sections.get(aid, "").rstrip())
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


@dataclass
class LedgerAppendResult:
    action: str
    problem_id: str
    attempt_id: str
    ledger_path: str
    written: bool = False
    error: str | None = None


def append_attempt_to_ledger(
    project_root: Path,
    *,
    problem_id: str,
    record: dict[str, Any],
    narrative: str,
) -> LedgerAppendResult:
    """Append one Attempt to the Problem ledger with validate-then-atomic-replace."""
    from tools.source_io.atomic import atomic_replace_text

    from .discovery import attempt_dir
    from .validator import validate_project

    project_root = project_root.resolve()
    aid = str(record.get("id", ""))
    ledger_path = attempt_dir(project_root) / f"{problem_id}.md"
    sections: dict[str, str] = {aid: narrative.rstrip()}
    attempts: list[dict[str, Any]] = [record]

    if ledger_path.is_file():
        loaded = load_ledger_file(ledger_path, project_root)
        if loaded.problem_id and loaded.problem_id != problem_id:
            return LedgerAppendResult(
                action="FAIL",
                problem_id=problem_id,
                attempt_id=aid,
                ledger_path=str(ledger_path),
                error="ledger problem mismatch",
            )
        for existing in loaded.attempts:
            if str(existing.get("id")) == aid:
                return LedgerAppendResult(
                    action="FAIL",
                    problem_id=problem_id,
                    attempt_id=aid,
                    ledger_path=str(ledger_path),
                    error=f"duplicate attempt id {aid} in ledger",
                )
        attempts = list(loaded.attempts) + [record]
        sections = dict(loaded.sections)
        sections[aid] = narrative.rstrip()
        action = "APPEND"
    else:
        action = "CREATE"

    candidate_text = serialize_ledger(
        problem_id=problem_id,
        attempts=attempts,
        sections=sections,
    )
    original_text = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else None
    atomic_replace_text(ledger_path, candidate_text)
    try:
        result = validate_project(root=project_root)
        if result.summary.errors > 0:
            if original_text is None:
                ledger_path.unlink(missing_ok=True)
            else:
                atomic_replace_text(ledger_path, original_text)
            return LedgerAppendResult(
                action="FAIL",
                problem_id=problem_id,
                attempt_id=aid,
                ledger_path=relative_to_root(ledger_path, project_root),
                error="candidate ledger validation failed",
            )
    except Exception:
        if original_text is None:
            ledger_path.unlink(missing_ok=True)
        else:
            atomic_replace_text(ledger_path, original_text)
        raise

    return LedgerAppendResult(
        action=action,
        problem_id=problem_id,
        attempt_id=aid,
        ledger_path=relative_to_root(ledger_path, project_root),
        written=True,
    )
