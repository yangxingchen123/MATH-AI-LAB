"""Atomic research-project operations."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from pathlib import Path

from tools.source_io.atomic import atomic_replace_text

from .constants import (
    DOSSIER_BEGIN,
    DOSSIER_END,
    KIND_OVERLAY,
    PROJECT_KINDS,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    TEMPLATE_ROOT,
)
from .governance import assess_external_processing as assess_project_external_processing
from .models import ResearchProjectOperationKind, ResearchProjectOperationResult
from .parser import (
    canonical_record_content,
    parse_project,
    parse_records,
    render_file,
    replace_record_metadata,
    serialize_record,
    split_preamble_and_records,
)
from .paths import path_safety_error, rejected, resolve_repo_root
from .stale import DamagedDossierMarkers, dossier_is_stale, expected_generated_region, split_dossier
from .validator import validate_project

assess_external_processing = assess_project_external_processing


def _result(
    kind: ResearchProjectOperationKind,
    message: str,
    project: Path,
    *touched: Path,
) -> ResearchProjectOperationResult:
    return ResearchProjectOperationResult(
        kind=kind,
        message=message,
        project=project,
        touched_paths=tuple(touched),
    )


def _read_candidate(candidate: Path) -> str:
    return Path(candidate).read_text(encoding="utf-8")


def _single_record(candidate: Path, expected_type: str | None = None):
    records = parse_records(_read_candidate(candidate))
    if len(records) != 1:
        raise ValueError("candidate must contain exactly one research record")
    record = records[0]
    if expected_type is not None and record.type != expected_type:
        raise ValueError(f"candidate type must be {expected_type}")
    return record


def _validate_tree(project: Path, filename: str, new_text: str):
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "project"
        shutil.copytree(project, dest)
        target = dest / filename
        target.write_text(new_text, encoding="utf-8", newline="\n")
        return validate_project(dest)


def _replace_if_valid(
    project: Path,
    filename: str,
    new_text: str,
    *,
    success_message: str,
) -> ResearchProjectOperationResult:
    official = project / filename
    before = official.read_bytes() if official.is_file() else None
    result = _validate_tree(project, filename, new_text)
    if not result.ok:
        if official.is_file() and before is not None:
            assert official.read_bytes() == before
        return _result(
            ResearchProjectOperationKind.REJECTED,
            "; ".join(result.errors) or "validation failed",
            project,
        )
    atomic_replace_text(official, new_text)
    return _result(
        ResearchProjectOperationKind.WRITTEN,
        success_message,
        project,
        official,
    )


def _add_only(
    project: Path,
    candidate: Path,
    *,
    expected_type: str,
    filename: str,
    mutate_records=None,
) -> ResearchProjectOperationResult:
    project = Path(project)
    official = project / filename
    try:
        if Path(candidate).resolve() == official.resolve():
            return rejected("candidate path must not be the official file", project)
        new_record = _single_record(candidate, expected_type)
    except (ValueError, OSError) as exc:
        return rejected(str(exc), project)
    preamble, records = split_preamble_and_records(
        official.read_text(encoding="utf-8") if official.is_file() else ""
    )
    existing = next((item for item in records if item.ref == new_record.ref), None)
    if existing is not None:
        if canonical_record_content(existing) == canonical_record_content(new_record):
            return _result(
                ResearchProjectOperationKind.NO_OP,
                f"{new_record.ref} already present",
                project,
            )
        return rejected(
            f"{new_record.ref} already exists with different content",
            project,
        )
    records.append(new_record if new_record.raw else new_record)
    if not new_record.raw:
        new_record.raw = serialize_record(new_record)
    if mutate_records is not None:
        try:
            records = mutate_records(records, new_record)
        except ValueError as exc:
            return rejected(str(exc), project)
    new_text = render_file(preamble, records)
    return _replace_if_valid(
        project,
        filename,
        new_text,
        success_message=f"wrote {new_record.ref}",
    )


def _sort_evd_refs(refs: list[str]) -> list[str]:
    unique = sorted(set(refs), key=lambda ref: int(ref.split("-")[1]))
    return unique


def add_assumption(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    return _add_only(
        project,
        candidate,
        expected_type="ASSUMPTION",
        filename="assumptions.md",
    )


def add_claim(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    try:
        record = _single_record(candidate, "CLAIM")
    except (ValueError, OSError) as exc:
        return rejected(str(exc), Path(project))
    refs = [
        item.strip()
        for item in record.metadata.get("evidence_refs", "").split(",")
        if item.strip()
    ]
    if refs:
        return rejected("add_claim must omit evidence_refs or leave them empty", Path(project))
    return _add_only(
        project,
        candidate,
        expected_type="CLAIM",
        filename="evidence.md",
    )


def add_evidence(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    def mutate(records, new_record):
        claim_ref = new_record.metadata["claim_ref"]
        found = False
        updated = []
        for item in records:
            if item.type == "CLAIM" and item.ref == claim_ref:
                found = True
                current = [
                    part.strip()
                    for part in item.metadata.get("evidence_refs", "").split(",")
                    if part.strip()
                ]
                current.append(new_record.ref)
                joined = ", ".join(_sort_evd_refs(current))
                item = replace_record_metadata(item, {"evidence_refs": joined})
            updated.append(item)
        if not found:
            raise ValueError(f"{new_record.ref} claim_ref {claim_ref} does not exist")
        return updated

    return _add_only(
        project,
        candidate,
        expected_type="EVIDENCE",
        filename="evidence.md",
        mutate_records=mutate,
    )


def append_decision(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    return _add_only(
        project,
        candidate,
        expected_type="DECISION",
        filename="decisions.md",
    )


def record_negative_result(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    return _add_only(
        project,
        candidate,
        expected_type="NEGATIVE_RESULT",
        filename="negative_results.md",
    )


def add_literature(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    return _add_only(
        project,
        candidate,
        expected_type="LITERATURE",
        filename="literature.md",
    )


def add_novelty(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    return _add_only(
        project,
        candidate,
        expected_type="NOVELTY",
        filename="novelty.md",
    )


def add_review(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    return _add_only(
        project,
        candidate,
        expected_type="REVIEW",
        filename="reviews/reviews.md",
    )


def supersede_assumption(
    project: Path,
    ref: str,
    candidate: Path,
) -> ResearchProjectOperationResult:
    project = Path(project)
    official = project / "assumptions.md"
    try:
        if Path(candidate).resolve() == official.resolve():
            return rejected("candidate path must not be the official file", project)
        replacement = _single_record(candidate, "ASSUMPTION")
    except (ValueError, OSError) as exc:
        return rejected(str(exc), project)
    preamble, records = split_preamble_and_records(official.read_text(encoding="utf-8"))
    existing = next((item for item in records if item.ref == ref), None)
    if existing is None:
        return rejected(f"{ref} does not exist", project)
    if existing.metadata.get("status") != "ACTIVE":
        return rejected(f"{ref} is not ACTIVE", project)
    if replacement.ref == ref:
        return rejected("replacement must use a new assumption ref", project)
    updated = []
    found = False
    for item in records:
        if item.ref == ref:
            found = True
            item = replace_record_metadata(
                item,
                {
                    "status": "SUPERSEDED",
                    "superseded_by": replacement.ref,
                },
            )
        updated.append(item)
    if not found:
        return rejected(f"{ref} does not exist", project)
    meta = dict(replacement.metadata)
    meta["status"] = "ACTIVE"
    meta["supersedes"] = ref
    replacement.metadata = meta
    replacement.raw = serialize_record(replacement)
    updated.append(replacement)
    return _replace_if_valid(
        project,
        "assumptions.md",
        render_file(preamble, updated),
        success_message=f"superseded {ref} with {replacement.ref}",
    )


def update_governance(project: Path, candidate: Path) -> ResearchProjectOperationResult:
    project = Path(project)
    official = project / "governance.md"
    try:
        if Path(candidate).resolve() == official.resolve():
            return rejected("candidate path must not be the official file", project)
        record = _single_record(candidate)
    except (ValueError, OSError) as exc:
        return rejected(str(exc), project)
    if record.type not in {"GOVERNANCE", "AI_CONTRIBUTION"}:
        return rejected("update_governance candidate must be GOVERNANCE or AI_CONTRIBUTION", project)
    if record.type == "AI_CONTRIBUTION":
        return _add_only(
            project,
            candidate,
            expected_type="AI_CONTRIBUTION",
            filename="governance.md",
        )
    if record.ref != "GOV-0001":
        return rejected("GOVERNANCE ref must be GOV-0001", project)
    preamble, records = split_preamble_and_records(official.read_text(encoding="utf-8"))
    existing = next((item for item in records if item.type == "GOVERNANCE"), None)
    if existing is not None and canonical_record_content(existing) == canonical_record_content(
        record
    ):
        return _result(ResearchProjectOperationKind.NO_OP, "GOV-0001 unchanged", project)
    if not record.raw:
        record.raw = serialize_record(record)
    replaced = False
    updated = []
    for item in records:
        if item.type == "GOVERNANCE":
            updated.append(record)
            replaced = True
        else:
            updated.append(item)
    if not replaced:
        updated.insert(0, record)
    return _replace_if_valid(
        project,
        "governance.md",
        render_file(preamble, updated),
        success_message="updated GOV-0001",
    )


def reconcile_project(project: Path) -> ResearchProjectOperationResult:
    project = Path(project)
    path = project / "research_dossier.md"
    before = path.read_bytes()
    text = path.read_text(encoding="utf-8")
    try:
        human, current, tail = split_dossier(text)
    except DamagedDossierMarkers as exc:
        assert path.read_bytes() == before
        return rejected(str(exc), project)
    expected = expected_generated_region(project)
    if current == expected:
        return _result(ResearchProjectOperationKind.NO_OP, "dossier already fresh", project)
    new_text = f"{human}{DOSSIER_BEGIN}{expected}{DOSSIER_END}{tail}"
    result = _validate_tree(project, "research_dossier.md", new_text)
    if not result.ok:
        assert path.read_bytes() == before
        return rejected("; ".join(result.errors) or "validation failed", project)
    atomic_replace_text(path, new_text)
    return _result(
        ResearchProjectOperationKind.WRITTEN,
        "reconciled generated dossier",
        project,
        path,
    )


def _template_is_complete(project: Path) -> bool:
    return all((project / name).is_file() for name in REQUIRED_FILES) and all(
        (project / name).is_dir() for name in REQUIRED_DIRS
    )


def _write_scaffold(dest: Path, title: str, kind: str = "research") -> None:
    shutil.copytree(TEMPLATE_ROOT, dest)
    overlay = KIND_OVERLAY.get(kind)
    if overlay is not None:
        for path in overlay.rglob("*"):
            if not path.is_file():
                continue
            target = dest / path.relative_to(overlay)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    dossier = dest / "research_dossier.md"
    text = dossier.read_text(encoding="utf-8").replace("{{TITLE}}", title)
    dossier.write_text(text, encoding="utf-8", newline="\n")
    for name in REQUIRED_DIRS:
        (dest / name).mkdir(parents=True, exist_ok=True)


def init_project(
    project: Path,
    title: str,
    *,
    repo_root: Path | None = None,
    kind: str = "research",
) -> ResearchProjectOperationResult:
    project = Path(project)
    root = resolve_repo_root(repo_root)
    if kind not in PROJECT_KINDS:
        return rejected(f"unknown project kind: {kind}", project)
    safety = path_safety_error(project, root)
    if safety:
        return rejected(safety, project)
    if project.exists():
        if project.is_dir() and _template_is_complete(project) and validate_project(project).ok:
            return _result(
                ResearchProjectOperationKind.NO_OP,
                "complete scaffold already present",
                project,
            )
        return rejected("destination is incomplete or conflicting", project)
    staging = project.parent / f".{project.name}.{uuid.uuid4().hex}.staging"
    try:
        project.parent.mkdir(parents=True, exist_ok=True)
        _write_scaffold(staging, title, kind)
        check = validate_project(staging)
        if not check.ok:
            shutil.rmtree(staging, ignore_errors=True)
            return rejected("; ".join(check.errors) or "template scaffold invalid", project)
        if project.exists():
            shutil.rmtree(staging, ignore_errors=True)
            return rejected("destination appeared during publish", project)
        staging.rename(project)
    except OSError as exc:
        shutil.rmtree(staging, ignore_errors=True)
        return rejected(f"init failed: {exc}", project)
    return _result(
        ResearchProjectOperationKind.WRITTEN,
        "created research project scaffold",
        project,
        project,
    )
