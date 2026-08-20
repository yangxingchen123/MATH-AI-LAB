"""Parse and mutate canonical Solution slots in Problem Markdown body."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import SolutionSlot

BEGIN_RE = re.compile(
    r"<!--\s*MATH-AI-LAB:SOLUTION\s+target=([^\s>]+)\s+BEGIN\s*-->",
    re.IGNORECASE,
)
END_RE = re.compile(
    r"<!--\s*MATH-AI-LAB:SOLUTION\s+target=([^\s>]+)\s+END\s*-->",
    re.IGNORECASE,
)
LEGACY_PART_RE = re.compile(
    r"^###\s*\(([a-z])\)\s+AI-generated Solution\s*$",
    re.MULTILINE | re.IGNORECASE,
)
SECTION_BOUNDARY_RE = re.compile(r"^(?:##|###)\s+", re.MULTILINE)


def normalize_target(problem_id: str, part: str | None = None) -> str:
    if part is None or part == "":
        return problem_id
    return f"{problem_id}/{part}"


def marker_begin(target: str) -> str:
    return f"<!-- MATH-AI-LAB:SOLUTION target={target} BEGIN -->"


def marker_end(target: str) -> str:
    return f"<!-- MATH-AI-LAB:SOLUTION target={target} END -->"


def wrap_slot_content(target: str, content: str) -> str:
    body = content.strip("\n")
    return f"{marker_begin(target)}\n{body}\n{marker_end(target)}"


def _normalize_content(text: str) -> str:
    return text.strip().replace("\r\n", "\n")


@dataclass
class SlotParseResult:
    slots: list[SolutionSlot]
    duplicate_targets: list[str]


def parse_canonical_slots(body: str) -> SlotParseResult:
    slots: list[SolutionSlot] = []
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for begin in BEGIN_RE.finditer(body):
        target = begin.group(1)
        end_pat = marker_end(target)
        end_idx = body.find(end_pat, begin.end())
        if end_idx < 0:
            continue
        content = body[begin.end() : end_idx]
        slot = SolutionSlot(
            target=target,
            content=content,
            start=begin.start(),
            end=end_idx + len(end_pat),
            canonical=True,
        )
        if target in seen:
            duplicates.append(target)
        seen[target] = seen.get(target, 0) + 1
        slots.append(slot)
    return SlotParseResult(slots=slots, duplicate_targets=duplicates)


def parse_legacy_part_slots(body: str, problem_id: str) -> list[SolutionSlot]:
    """Recognize legacy `### (a) AI-generated Solution` headings for read/upsert."""
    slots: list[SolutionSlot] = []
    for match in LEGACY_PART_RE.finditer(body):
        part = match.group(1)
        target = normalize_target(problem_id, part)
        start = match.end()
        next_heading = SECTION_BOUNDARY_RE.search(body, start)
        end = next_heading.start() if next_heading else len(body)
        content = body[start:end]
        slots.append(
            SolutionSlot(
                target=target,
                content=content,
                start=match.start(),
                end=end,
                canonical=False,
            )
        )
    return slots


def find_slot(
    body: str,
    *,
    problem_id: str,
    part: str | None = None,
) -> SolutionSlot | None:
    target = normalize_target(problem_id, part)
    canonical = parse_canonical_slots(body)
    for slot in canonical.slots:
        if slot.target == target:
            return slot
    for slot in parse_legacy_part_slots(body, problem_id):
        if slot.target == target:
            return slot
    return None


def count_slots_for_target(body: str, *, problem_id: str, part: str | None = None) -> int:
    target = normalize_target(problem_id, part)
    canonical = [s for s in parse_canonical_slots(body).slots if s.target == target]
    legacy = [s for s in parse_legacy_part_slots(body, problem_id) if s.target == target]
    return len(canonical) + len(legacy)


def content_equal(existing: str, candidate: str) -> bool:
    return _normalize_content(existing) == _normalize_content(candidate)


def upsert_body(
    body: str,
    *,
    problem_id: str,
    part: str | None,
    content: str,
) -> tuple[str, str]:
    """Return (new_body, action) where action is CREATE|UPDATE|NO_OP."""
    target = normalize_target(problem_id, part)
    wrapped = wrap_slot_content(target, content)
    canonical = parse_canonical_slots(body)
    if target in canonical.duplicate_targets:
        raise ValueError(f"duplicate canonical solution slot for target {target}")

    existing = find_slot(body, problem_id=problem_id, part=part)
    if existing is not None:
        if existing.canonical and content_equal(existing.content, content):
            return body, "NO_OP"
        if existing.canonical:
            new_body = body[: existing.start] + wrapped + body[existing.end :]
        else:
            new_body = body[: existing.start] + wrapped + "\n\n" + body[existing.end :].lstrip("\n")
        return new_body, "UPDATE"

    answer_heading = "## 解答"
    if answer_heading in body:
        idx = body.index(answer_heading)
        line_end = body.find("\n", idx)
        insert_at = len(body) if line_end < 0 else line_end + 1
        prefix = body[:insert_at]
        suffix = body[insert_at:]
        if not prefix.endswith("\n\n"):
            prefix = prefix.rstrip("\n") + "\n\n"
        new_body = prefix + wrapped + "\n\n" + suffix.lstrip("\n")
    else:
        new_body = body.rstrip() + f"\n\n{answer_heading}\n\n{wrapped}\n"
    return new_body, "CREATE"
