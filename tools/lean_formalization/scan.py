"""Lean sidecar scanner. Missing lake never fails Core math paths."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SORRY_RE = re.compile(r"\bsorry\b")
ADMIT_RE = re.compile(r"\badmit\b")
AXIOM_RE = re.compile(r"^\s*axiom\s+", re.MULTILINE)
BLOCK_COMMENT_RE = re.compile(r"/-.*?-/", re.S)


@dataclass(frozen=True)
class ScanHit:
    path: str
    kind: str
    line: int
    text: str


def _without_comments(text: str) -> str:
    stripped = BLOCK_COMMENT_RE.sub(lambda match: "\n" * match.group(0).count("\n"), text)
    lines: list[str] = []
    for line in stripped.splitlines(keepends=True):
        if "--" not in line:
            lines.append(line)
            continue
        code, newline = line.split("--", 1)[0], "\n" if line.endswith("\n") else ""
        lines.append(code + newline)
    return "".join(lines)


def scan_lean_text(text: str, *, path: str = "") -> list[ScanHit]:
    source = _without_comments(text)
    hits: list[ScanHit] = []
    for kind, pattern in (("sorry", SORRY_RE), ("admit", ADMIT_RE)):
        for match in pattern.finditer(source):
            line = source[: match.start()].count("\n") + 1
            hits.append(ScanHit(path=path, kind=kind, line=line, text=match.group(0)))
    for match in AXIOM_RE.finditer(source):
        line = source[: match.start()].count("\n") + 1
        hits.append(ScanHit(path=path, kind="axiom", line=line, text=match.group(0).strip()))
    return hits


def scan_lean_tree(root: Path) -> list[ScanHit]:
    hits: list[ScanHit] = []
    for path in sorted(Path(root).rglob("*.lean")):
        text = path.read_text(encoding="utf-8")
        hits.extend(scan_lean_text(text, path=str(path.as_posix())))
    return hits
