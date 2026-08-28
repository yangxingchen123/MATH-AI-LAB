"""Append-only guard for research decisions."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .constants import PROJECTS_DIRNAME, TEMPLATE_DIRNAME
from .models import ResearchProjectValidationResult
from .parser import parse_records
from .validator import validate_project


def _git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(Path(repo).resolve()),
        capture_output=True,
        text=True,
        check=False,
    )


def assert_decisions_append_only(base_text: str, current_text: str) -> None:
    if current_text == base_text:
        return
    if not current_text.startswith(base_text):
        raise ValueError(
            "decision history was edited, deleted, reordered, inserted before, "
            "or whitespace-mutated inside historical records"
        )
    rest = current_text[len(base_text) :]
    if rest.strip() == "":
        return
    records = parse_records(rest)
    if not records or any(item.type != "DECISION" for item in records):
        raise ValueError("decision tail is not a complete Decision record sequence")


def _is_decisions_path(posix: str) -> bool:
    parts = posix.split("/")
    if len(parts) != 3:
        return False
    return (
        parts[0] == PROJECTS_DIRNAME
        and parts[2] == "decisions.md"
        and parts[1] != TEMPLATE_DIRNAME
        and TEMPLATE_DIRNAME not in parts
    )


def _base_paths(repo: Path, base_ref: str) -> set[str] | None:
    listed = _git(repo, ["ls-tree", "-r", "--name-only", "-z", base_ref])
    if listed.returncode != 0:
        listed = _git(repo, ["ls-tree", "-r", "--name-only", base_ref])
        if listed.returncode != 0:
            return None
        names = [line.replace("\\", "/") for line in listed.stdout.splitlines() if line]
    else:
        names = [item.replace("\\", "/") for item in listed.stdout.split("\0") if item]
    return {name for name in names if _is_decisions_path(name)}


def _current_paths(repo: Path) -> set[str]:
    root = Path(repo).resolve() / PROJECTS_DIRNAME
    found: set[str] = set()
    if not root.is_dir():
        return found
    for child in root.iterdir():
        if child.name == TEMPLATE_DIRNAME:
            continue
        decisions = child / "decisions.md"
        if decisions.is_file():
            found.add(decisions.relative_to(root.parent).as_posix())
    return found


def _show_base(repo: Path, base_ref: str, posix: str) -> str | None:
    shown = _git(repo, ["show", f"{base_ref}:{posix}"])
    if shown.returncode != 0:
        return None
    return shown.stdout.replace("\r\n", "\n")


def check_append_only_all(repo_root: Path, base_ref: str) -> ResearchProjectValidationResult:
    repo = Path(repo_root).resolve()
    parsed = _git(repo, ["rev-parse", "--verify", f"{base_ref}^{{commit}}"])
    if parsed.returncode != 0:
        return ResearchProjectValidationResult(
            ok=False,
            errors=[f"invalid or unfetched base_ref: {base_ref}"],
        )
    base_paths = _base_paths(repo, parsed.stdout.strip())
    if base_paths is None:
        return ResearchProjectValidationResult(
            ok=False,
            errors=[f"cannot list tree for base_ref: {base_ref}"],
        )
    current_paths = _current_paths(repo)
    errors: list[str] = []
    for posix in sorted(base_paths | current_paths):
        in_base = posix in base_paths
        in_current = posix in current_paths
        if in_base and not in_current:
            errors.append(f"deleted decisions path: {posix}")
            continue
        current_file = repo / Path(*posix.split("/"))
        current_text = (
            current_file.read_text(encoding="utf-8") if current_file.is_file() else ""
        )
        base_text = _show_base(repo, parsed.stdout.strip(), posix) if in_base else ""
        if base_text is None:
            base_text = ""
        try:
            assert_decisions_append_only(base_text, current_text)
        except ValueError as exc:
            errors.append(f"{posix}: {exc}")
    return ResearchProjectValidationResult(ok=not errors, errors=errors)


def check_append_only(project: Path, base_ref: str) -> ResearchProjectValidationResult:
    project = Path(project).resolve()
    repo = project.parent.parent
    all_result = check_append_only_all(repo, base_ref)
    if not all_result.ok and all_result.errors and all_result.errors[0].startswith("invalid"):
        return all_result
    posix = f"{PROJECTS_DIRNAME}/{project.name}/decisions.md"
    filtered = [err for err in all_result.errors if posix in err or err.startswith("deleted")]
    if any(posix in err for err in all_result.errors) or any(
        err.endswith(posix) or posix in err for err in all_result.errors
    ):
        return ResearchProjectValidationResult(ok=False, errors=filtered or all_result.errors)
    local = validate_project(project)
    return ResearchProjectValidationResult(ok=True, errors=[], warnings=local.warnings)
