"""Write Evidence *candidates* from run metrics. Never mutates official evidence.md."""

from __future__ import annotations

import json
import re
from pathlib import Path

CLAIM_RE = re.compile(r"ref=(CLM-\d{4})")
EVD_RE = re.compile(r"ref=EVD-(\d{4})")
ENGINE_CLAIM: tuple[tuple[str, str], ...] = (
    ("soc_piecewise", "CLM-0004"),
    ("soc_sensitivity", "CLM-0002"),
    ("soc", "CLM-0001"),
)


def _first_claim_ref(text: str) -> str:
    match = CLAIM_RE.search(text)
    return match.group(1) if match else "CLM-0001"


def _claim_for_run(run_id: str, evidence_text: str) -> str:
    existing = set(CLAIM_RE.findall(evidence_text))
    for prefix, ref in ENGINE_CLAIM:
        if run_id.startswith(prefix) and ref in existing:
            return ref
    return _first_claim_ref(evidence_text)


def _next_evd(evidence_text: str) -> int:
    nums = [int(match.group(1)) for match in EVD_RE.finditer(evidence_text)]
    return (max(nums) + 1) if nums else 1


def write_evidence_candidates(project: Path, code: Path) -> list[Path]:
    project = Path(project)
    code = Path(code)
    dest = project / "documents" / "candidates"
    dest.mkdir(parents=True, exist_ok=True)
    evidence = project / "evidence.md"
    evidence_text = evidence.read_text(encoding="utf-8") if evidence.is_file() else ""
    next_n = _next_evd(evidence_text)
    written: list[Path] = []
    outputs = code / "outputs"
    if not outputs.is_dir():
        return written
    for run_dir in sorted(p for p in outputs.iterdir() if p.is_dir()):
        if run_dir.name in evidence_text:
            continue
        metrics = run_dir / "metrics.json"
        if not metrics.is_file():
            continue
        try:
            payload = json.loads(metrics.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        ref = f"EVD-{next_n:04d}"
        next_n += 1
        claim = _claim_for_run(run_dir.name, evidence_text)
        try:
            run_rel = run_dir.relative_to(code.parent.parent).as_posix()
        except ValueError:
            run_rel = run_dir.as_posix()
        path = dest / f"evd_{run_dir.name}.md"
        body_lines = [
            f"run_id: {run_dir.name}",
            f"metrics_path: {run_rel}/metrics.json",
            "metrics:",
        ]
        for key, value in payload.items():
            body_lines.append(f"  {key}: {value}")
        lines = [
            "<!-- CANDIDATE ONLY. Not official evidence. Review, then:",
            f"     python -m tools.research_project add-evidence --project \"{project.as_posix()}\" --candidate \"{path.as_posix()}\"",
            "-->",
            f"<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref={ref} BEGIN -->",
            f"- claim_ref: {claim}",
            "- polarity: SUPPORT",
            "- kind: COMPUTATION",
            f"- source_citation: run:{run_rel}",
            "---",
            *body_lines,
            f"<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref={ref} END -->",
            "",
        ]
        path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        written.append(path)
    return written
