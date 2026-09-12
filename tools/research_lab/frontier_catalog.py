"""Read-only Erdős frontier catalog from the local vendor pin. Not theorems."""

from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache

import yaml

from .constants import FRONTIER_PKG, REPO_ROOT

ERDOS_INDEX_PATH = FRONTIER_PKG / "src" / "erdos-additive.json"
ERDOS_VENDOR = REPO_ROOT / "vendor" / "erdosproblems"
ERDOS_LICENSE = ERDOS_VENDOR / "LICENSE"
ERDOS_YAML = ERDOS_VENDOR / "data" / "problems.yaml"
ERDOS_README = ERDOS_VENDOR / "README.md"
ERDOS_SCHEMA = ERDOS_VENDOR / "schema" / "problems.schema.json"
ERDOS_PIN = "5308c57c700559416b9f205df274b136784203e7"
ERDOS_UPSTREAM = "https://github.com/teorth/erdosproblems"
SCOPE_TAG = "additive combinatorics"

UPSTREAM_TRACKED_FILES = (
    ".github/ISSUE_TEMPLATE/help-wanted.yml",
    ".github/workflows/deploy-pages.yml",
    ".github/workflows/update-formal-conjectures.yml",
    ".github/workflows/update-readme.yml",
    ".github/workflows/validate.yml",
    ".gitignore",
    "CITATIONS.cff",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "data/problems.yaml",
    "data/statistics_history.csv",
    "data/statistics_history_dark.svg",
    "data/statistics_history_light.svg",
    "docs/app.js",
    "docs/filters.js",
    "docs/index.html",
    "docs/styles.css",
    "docs/theme-toggle.js",
    "docs/url-state.js",
    "docs/utils.js",
    "requirements.txt",
    "schema/problems.schema.json",
    "scripts/derive_status.py",
    "scripts/generate_readme.py",
    "scripts/oeis_cons_compare.py",
    "scripts/plot_statistics_history.py",
    "scripts/update_formalization_status.py",
    "scripts/validate.py",
    "tests/test_oeis_cons_compare.py",
)

OVERLAY_FILES = (
    ERDOS_VENDOR / "UPSTREAM.md",
    ERDOS_VENDOR / "NOTICE",
)


def _status_state(row: dict) -> str:
    status = row.get("status") or {}
    if isinstance(status, dict):
        return str(status.get("state") or "")
    return str(status)


def _is_open_status(state: str) -> bool:
    return state == "open" or state.startswith("open ")


def _formalized_state(row: dict) -> str:
    formalized = row.get("formalized") or {}
    if isinstance(formalized, dict):
        return str(formalized.get("state") or "")
    return str(formalized)


def _oeis(row: dict) -> list[str]:
    values = row.get("oeis") or []
    if not isinstance(values, list):
        return []
    return [str(item) for item in values]


def _nickname(row: dict) -> str:
    comments = row.get("comments")
    if isinstance(comments, str) and comments.strip():
        return comments.strip()
    return ""


def _pointer(row: dict, *, open_question: bool) -> dict:
    number = str(row.get("number"))
    item = {
        "id": f"erdos:{number}",
        "number": number,
        "status": _status_state(row),
        "tags": [str(tag) for tag in (row.get("tags") or [])],
        "formalized": _formalized_state(row),
        "oeis": _oeis(row),
        "url": f"https://www.erdosproblems.com/{number}",
        "not_a_theorem": True,
    }
    nick = _nickname(row)
    if nick:
        item["nickname"] = nick
    if "prize" in row:
        item["prize"] = row.get("prize")
    if not open_question:
        item["not_an_open_question"] = True
    return item


@lru_cache(maxsize=1)
def load_vendor_problems() -> tuple[dict, ...]:
    data = yaml.safe_load(ERDOS_YAML.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("vendor/erdosproblems/data/problems.yaml must be a list")
    return tuple(item for item in data if isinstance(item, dict))


def build_erdos_index() -> dict:
    records = load_vendor_problems()
    additive = [row for row in records if SCOPE_TAG in (row.get("tags") or [])]
    questions: list[dict] = []
    audit: list[dict] = []
    for row in additive:
        if _is_open_status(_status_state(row)):
            questions.append(_pointer(row, open_question=True))
        else:
            audit.append(_pointer(row, open_question=False))
    status_counts = dict(Counter(_status_state(row) for row in additive))
    return {
        "version": "1",
        "upstream": ERDOS_UPSTREAM,
        "pin": ERDOS_PIN,
        "source": "vendor/erdosproblems/data/problems.yaml",
        "scope_tag": SCOPE_TAG,
        "not_a_theorem": True,
        "writes_canonical": False,
        "network": False,
        "region": {
            "id": "region:additive-combinatorics",
            "title": "Additive combinatorics (external open index)",
            "description": "Unknown-region pointers from teorth/erdosproblems. Not Universe entities, not theorems.",
        },
        "direction": {
            "id": "dir:erdos-additive",
            "title": "Scan open Erdős problems in additive combinatorics",
            "motivation": "Lab domain is additive combinatorics. External open status is not a local proof.",
        },
        "counts": {
            "vendor_records": len(records),
            "additive_records": len(additive),
            "open_questions": len(questions),
            "audit_records": len(audit),
        },
        "additive_status_counts": status_counts,
        "questions": questions,
        "audit": audit,
    }


@lru_cache(maxsize=1)
def load_erdos_index() -> dict:
    return build_erdos_index()


def dump_erdos_index_json() -> dict:
    data = build_erdos_index()
    ERDOS_INDEX_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


def load_erdos_index_json() -> dict:
    data = json.loads(ERDOS_INDEX_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("erdos-additive.json must be an object")
    return data


def read_upstream_pin() -> str:
    text = (ERDOS_VENDOR / "UPSTREAM.md").read_text(encoding="utf-8")
    match = re.search(r"Pinned commit:\s*\n([0-9a-f]{40})", text)
    return match.group(1) if match else ""


def erdos_full_tree_ok() -> bool:
    return all((ERDOS_VENDOR / rel).is_file() for rel in UPSTREAM_TRACKED_FILES) and all(
        path.is_file() for path in OVERLAY_FILES
    )


def erdos_index_in_sync() -> bool:
    if not ERDOS_INDEX_PATH.is_file():
        return False
    built = build_erdos_index()
    mirrored = load_erdos_index_json()
    return all(
        mirrored.get(key) == built.get(key)
        for key in ("pin", "source", "counts", "additive_status_counts", "questions", "audit")
    )


def erdos_vendor_ok() -> bool:
    license_text = ERDOS_LICENSE.read_text(encoding="utf-8") if ERDOS_LICENSE.is_file() else ""
    return (
        erdos_full_tree_ok()
        and "Apache License" in license_text
        and read_upstream_pin() == ERDOS_PIN
        and erdos_index_in_sync()
        and not (ERDOS_VENDOR / "data" / "additive_combinatorics.yaml").exists()
    )


def erdos_health_detail() -> str:
    if not erdos_vendor_ok():
        return "erdos-frontier missing or out of sync"
    data = load_erdos_index()
    counts = data.get("counts") or {}
    return (
        f"pin={str(data.get('pin') or '')[:7]} "
        f"yaml={counts.get('vendor_records')} "
        f"open={counts.get('open_questions')} "
        f"audit={counts.get('audit_records')} "
        "json_sync=true"
    )


def erdos_title(row: dict) -> str:
    number = row.get("number")
    nick = row.get("nickname")
    if nick:
        return f"Erdős problem {number} ({nick})"
    return f"Erdős problem {number}"


def erdos_prompt(row: dict) -> str:
    number = row.get("number")
    status = row.get("status")
    url = row.get("url")
    return (
        f"Erdős problem {number} is listed {status} in additive combinatorics. "
        f"See {url}. Not a theorem in this warehouse."
    )


def frontier_briefing() -> dict:
    data = load_erdos_index()
    questions = list(data.get("questions") or [])
    return {
        "layer": "frontier",
        "writes_canonical": False,
        "not_a_theorem": True,
        "network": False,
        "upstream": data.get("upstream"),
        "pin": data.get("pin"),
        "source": data.get("source"),
        "scope_tag": data.get("scope_tag"),
        "region": data.get("region") or {},
        "direction": data.get("direction") or {},
        "questions": questions,
        "audit": list(data.get("audit") or []),
        "additive_status_counts": data.get("additive_status_counts") or {},
        "counts": data.get("counts") or {"open_questions": len(questions)},
    }


def _pointer_body(row: dict, *, open_question: bool) -> str:
    number = row.get("number")
    nick = row.get("nickname")
    extra = (
        ""
        if open_question
        else (
            "- not_an_open_question: true\n"
            "- OpenQuestion projection skipped; this is local audit of the vendor YAML.\n"
        )
    )
    nick_line = f"- nickname: {nick}\n" if nick else ""
    return (
        f"# {erdos_title(row)}\n\n"
        f"- id: `{row.get('id')}`\n"
        f"- status: {row.get('status')}\n"
        f"{nick_line}"
        f"- tags: {', '.join(row.get('tags') or [])}\n"
        f"- formalized (upstream flag): {row.get('formalized')}\n"
        f"- url: {row.get('url')}\n"
        "- not_a_theorem: true\n"
        f"{extra}\n"
        f"{erdos_prompt(row)}\n\n"
        "External formalized=yes is not Lean verification in this warehouse.\n\n"
        "Candidate / process record only. Not Canonical.\n"
    )


def frontier_catalog_rows() -> list[dict]:
    data = frontier_briefing()
    region = data.get("region") or {}
    counts = data.get("counts") or {}
    pin = str(data.get("pin") or "")
    status_counts = data.get("additive_status_counts") or {}
    hist = "\n".join(f"- {name}: {status_counts[name]}" for name in sorted(status_counts))
    rows = [
        {
            "id": "frontier",
            "title": str(region.get("title") or "前沿"),
            "group": "前沿",
            "body": (
                "# Additive combinatorics (external open index)\n\n"
                f"upstream: {data.get('upstream')}\n"
                f"pin: {pin}\n"
                f"source: {data.get('source')}\n"
                f"open_questions: {counts.get('open_questions')}\n"
                f"audit_records: {counts.get('audit_records')}\n"
                f"additive_records: {counts.get('additive_records')}\n"
                f"vendor_records: {counts.get('vendor_records')}\n"
                "writes_canonical: False\n"
                "network: False\n"
                "not_a_theorem: True\n\n"
                "Local vendor pin. Runtime reads data/problems.yaml. "
                "No GitHub API. No erdosproblems.com scrape. Not Canonical.\n"
            ),
        },
        {
            "id": str(region.get("id") or "region:additive-combinatorics"),
            "title": str(region.get("title") or "Additive combinatorics"),
            "group": "前沿",
            "body": (
                f"# {region.get('title')}\n\n"
                f"- id: `{region.get('id')}`\n"
                f"- status: `open`\n"
                f"- direction: `{(data.get('direction') or {}).get('id')}`\n"
                "- UnknownRegion ≠ Universe entity.\n"
                "- OpenQuestion ≠ theorem.\n\n"
                "Candidate / process record only. Not Canonical.\n"
            ),
        },
        {
            "id": "frontier-audit",
            "title": "Additive combinatorics (vendor audit)",
            "group": "前沿备查",
            "body": (
                "# Additive combinatorics (vendor audit)\n\n"
                "Non-open additive-combinatorics rows from the local pin. "
                "Not OpenQuestions. Not theorems.\n\n"
                f"audit_records: {counts.get('audit_records')}\n"
                f"additive_records: {counts.get('additive_records')}\n\n"
                f"{hist}\n\n"
                "Candidate / process record only. Not Canonical.\n"
            ),
        },
    ]
    for row in data.get("questions") or []:
        rows.append(
            {
                "id": str(row.get("id")),
                "title": erdos_title(row),
                "group": "前沿",
                "body": _pointer_body(row, open_question=True),
            }
        )
    for row in data.get("audit") or []:
        rows.append(
            {
                "id": str(row.get("id")),
                "title": erdos_title(row),
                "group": "前沿备查",
                "body": _pointer_body(row, open_question=False),
            }
        )
    return rows
