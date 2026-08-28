"""v1.7 six-role defect detection. Not Frozen Schema."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.artifact_consistency.checks import INCLUDEGRAPHICS
from tools.lean_formalization.scan import scan_lean_text

ROLES = (
    "PROOF",
    "EVIDENCE_REVIEW",
    "MODEL",
    "REPRODUCIBILITY",
    "FORMALIZATION",
    "EDITOR",
)

TODO_PROOF = re.compile(r"TODO:\s*prove|\bno derivation\b|proof omitted", re.I)
CITATION_CLAIM = re.compile(r"according to\s+\w+|cite:|showed that", re.I)
HAS_SOURCE = re.compile(r"source_citation:|literature_ref:|source_sha256:", re.I)
UNIT_MISMATCH = re.compile(r"unit:\s*(\w+).*compared_unit:\s*(\w+)", re.I | re.S)
NO_COMMAND = re.compile(r"run_id:", re.I)
HAS_COMMAND = re.compile(r"command:|seed:", re.I)
MANIFEST_HINT = re.compile(r"figure_id:|manifest\.yaml")


@dataclass(frozen=True)
class Finding:
    role: str
    severity: str
    path: str
    detail: str


def scan_text(text: str, *, path: str = "") -> list[Finding]:
    findings: list[Finding] = []
    suffix = Path(path).suffix.lower() if path else ""
    if TODO_PROOF.search(text):
        findings.append(Finding("PROOF", "BLOCKING", path, "missing derivation"))
    if CITATION_CLAIM.search(text) and not HAS_SOURCE.search(text):
        findings.append(Finding("EVIDENCE_REVIEW", "BLOCKING", path, "uncited attribution"))
    match = UNIT_MISMATCH.search(text)
    if match and match.group(1).lower() != match.group(2).lower():
        findings.append(Finding("MODEL", "BLOCKING", path, "unit mismatch"))
    if NO_COMMAND.search(text) and not HAS_COMMAND.search(text):
        findings.append(Finding("REPRODUCIBILITY", "BLOCKING", path, "run lacks command/seed"))
    if suffix == ".lean" and scan_lean_text(text, path=path):
        findings.append(Finding("FORMALIZATION", "BLOCKING", path, "sorry/admit/axiom present"))
    if suffix == ".tex" and INCLUDEGRAPHICS.search(text) and not MANIFEST_HINT.search(text):
        findings.append(Finding("EDITOR", "BLOCKING", path, "includegraphics without provenance"))
    return findings


def scan_tree(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".tex", ".lean", ".yaml", ".yml", ".json", ".txt"}:
            continue
        findings.extend(scan_text(path.read_text(encoding="utf-8"), path=str(path.as_posix())))
    return findings


def blocking_findings(findings: list[Finding]) -> list[Finding]:
    return [item for item in findings if item.severity == "BLOCKING"]
