"""v2.1 controlled multi-agent research. Agents emit Candidates only."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools.artifact_consistency.checks import INCLUDEGRAPHICS
from tools.lean_formalization.scan import scan_lean_text
from tools.review.detect import scan_tree

ROLES: tuple[str, ...] = (
    "SOLVER",
    "SKEPTIC",
    "VERIFIER",
    "LITERATURE",
    "MODELING",
    "FORMALIZER",
    "REPRODUCER",
    "EDITOR",
)

SOURCE_ROOTS = ("01_知识库", "08_成果输出", "11_学习证据")


@dataclass
class RoleOutput:
    role: str
    status: str
    candidate: bool
    findings: list[str]
    tool_calls: list[str]
    cost: dict
    strategy_hash: str
    claims_reviewed: bool = False


@dataclass
class TaskAudit:
    task_id: str
    goal: str
    data_level: str
    inputs: list[str]
    roles: list[RoleOutput]
    disagreements: list[str]
    final_status: str
    fallback: str | None
    source_mutations: list[str]
    restricted_remote_sends: int
    candidate: bool = True
    missing_roles: list[str] = field(default_factory=list)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def solver_role(_root: Path) -> RoleOutput:
    return RoleOutput(
        role="SOLVER",
        status="SUCCEEDED",
        candidate=True,
        findings=[],
        tool_calls=["read-bundle"],
        cost={"calls": 1},
        strategy_hash=_hash("solver-optimistic-v1"),
        claims_reviewed=False,
    )


def _findings_for(root: Path, role: str) -> list[str]:
    found = [f"{item.role}:{item.detail}" for item in scan_tree(root)]
    if role == "SKEPTIC":
        return [item for item in found if item.startswith(("PROOF", "MODEL"))]
    if role == "VERIFIER":
        return [item for item in found if item.startswith("PROOF")]
    if role == "LITERATURE":
        return [item for item in found if item.startswith("EVIDENCE_REVIEW")]
    if role == "MODELING":
        return [item for item in found if item.startswith(("MODEL", "REPRODUCIBILITY"))]
    if role == "FORMALIZER":
        extra = []
        for path in Path(root).rglob("*.lean"):
            extra.extend(f"FORMALIZATION:{hit.kind}" for hit in scan_lean_text(path.read_text(encoding="utf-8")))
        return extra
    if role == "REPRODUCER":
        return [item for item in found if item.startswith("REPRODUCIBILITY")]
    if role == "EDITOR":
        extra = []
        for path in Path(root).rglob("*.tex"):
            if INCLUDEGRAPHICS.search(path.read_text(encoding="utf-8")):
                extra.append("EDITOR:includegraphics")
        return extra or [item for item in found if item.startswith("EDITOR")]
    return found


def run_role(role: str, root: Path) -> RoleOutput:
    if role == "SOLVER":
        return solver_role(root)
    findings = _findings_for(root, role)
    return RoleOutput(
        role=role,
        status="SUCCEEDED",
        candidate=True,
        findings=findings,
        tool_calls=[f"scan:{role.lower()}"],
        cost={"calls": 1},
        strategy_hash=_hash(f"{role}-v1"),
        claims_reviewed=role != "SOLVER",
    )


def run_task(
    root: Path,
    *,
    task_id: str = "task-001",
    goal: str = "review defects",
    data_level: str = "PUBLIC",
    remote: bool = False,
    roles: tuple[str, ...] | None = None,
    cancel: bool = False,
    timeout_role: str | None = None,
    allow_source_write: bool = False,
    write_root: Path | None = None,
) -> TaskAudit:
    chosen = roles or ROLES
    source_mutations: list[str] = []
    restricted_sends = 0
    if data_level == "RESTRICTED" and remote:
        restricted_sends = 0  # blocked, never sent
        return TaskAudit(
            task_id=task_id,
            goal=goal,
            data_level=data_level,
            inputs=[str(root)],
            roles=[],
            disagreements=[],
            final_status="FAILED",
            fallback="local-only",
            source_mutations=[],
            restricted_remote_sends=restricted_sends,
            missing_roles=list(chosen),
        )
    if cancel:
        return TaskAudit(
            task_id=task_id,
            goal=goal,
            data_level=data_level,
            inputs=[str(root)],
            roles=[],
            disagreements=[],
            final_status="CANCELLED",
            fallback="SOLVER",
            source_mutations=[],
            restricted_remote_sends=0,
            missing_roles=list(chosen),
        )
    outputs: list[RoleOutput] = []
    missing: list[str] = []
    for role in chosen:
        if timeout_role == role:
            outputs.append(
                RoleOutput(
                    role=role,
                    status="TIMEOUT",
                    candidate=True,
                    findings=[],
                    tool_calls=[],
                    cost={"calls": 0},
                    strategy_hash=_hash("timeout"),
                )
            )
            missing.append(role)
            continue
        outputs.append(run_role(role, Path(root)))
    if allow_source_write and write_root is not None:
        _ = write_root
    solver_ok = not any(item.findings for item in outputs if item.role == "SOLVER")
    others = [item for item in outputs if item.role != "SOLVER" and item.findings]
    disagreements = []
    if solver_ok and others:
        disagreements.append("SOLVER found no issues; other roles reported defects")
    fallback = "SOLVER" if timeout_role or cancel else None
    if missing:
        status = "PARTIAL"
    elif any(item.status == "FAILED" for item in outputs):
        status = "FAILED"
    else:
        status = "SUCCEEDED"
    return TaskAudit(
        task_id=task_id,
        goal=goal,
        data_level=data_level,
        inputs=[str(root)],
        roles=outputs,
        disagreements=disagreements,
        final_status=status,
        fallback=fallback,
        source_mutations=source_mutations,
        restricted_remote_sends=restricted_sends,
        missing_roles=missing,
    )


def defect_recall(audit: TaskAudit) -> int:
    found = {item for role in audit.roles for item in role.findings}
    return len(found)


def audit_complete(audit: TaskAudit) -> bool:
    if audit.final_status in {"CANCELLED", "FAILED"} and audit.fallback:
        return True
    for role in audit.roles:
        if not role.candidate:
            return False
        if role.status == "SUCCEEDED" and not role.tool_calls:
            return False
        if "calls" not in role.cost:
            return False
        if not role.strategy_hash:
            return False
    return True


def dump_audit(audit: TaskAudit) -> str:
    payload = asdict(audit)
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
