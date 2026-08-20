"""YAML Front Matter extraction and parsing for Method Validator v1."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .discovery import relative_to_root
from .models import ParseResult, Severity, ValidationIssue


FRONT_MATTER_RE = re.compile(
    r"\A---\r?\n(.*?)(?:\r?\n---\r?\n|\r?\n---\s*\Z)",
    re.DOTALL,
)


class DuplicateKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode, deep: bool = False):
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key!r}",
                key_node.start_mark,
            )
        value = loader.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping


DuplicateKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def extract_front_matter(text: str) -> tuple[str | None, str, list[ValidationIssue]]:
    if not text.startswith("---"):
        return None, text, []

    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text, [
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="M-PARSE-E002",
                message="YAML Front Matter has opening '---' but missing closing delimiter.",
            )
        ]
    body = text[match.end() :]
    return match.group(1), body, []


def parse_yaml_mapping(raw_yaml: str) -> tuple[dict[str, Any] | None, list[ValidationIssue]]:
    try:
        data = yaml.load(raw_yaml, Loader=DuplicateKeySafeLoader)
    except yaml.constructor.ConstructorError as exc:
        msg = str(exc)
        if "duplicate key" in msg.lower():
            return None, [
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="M-PARSE-E004",
                    message=f"Duplicate YAML key detected: {exc}",
                )
            ]
        return None, [
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="M-PARSE-E001",
                message=f"YAML Front Matter cannot be parsed: {exc}",
            )
        ]
    except (yaml.YAMLError, ValueError) as exc:
        return None, [
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="M-PARSE-E001",
                message=f"YAML Front Matter cannot be parsed: {exc}",
            )
        ]

    if data is None:
        return None, [
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="M-PARSE-E003",
                message="YAML Front Matter root is empty; expected a mapping.",
            )
        ]
    if not isinstance(data, dict):
        return None, [
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="M-PARSE-E003",
                message=f"YAML Front Matter root must be a mapping, got {type(data).__name__}.",
            )
        ]
    return data, []


def parse_markdown_file(path: Path, project_root: Path) -> ParseResult:
    rel = relative_to_root(path, project_root)
    text = path.read_text(encoding="utf-8")
    raw_yaml, body, extract_issues = extract_front_matter(text)
    result = ParseResult(
        path=path,
        relative_path=rel,
        has_front_matter=raw_yaml is not None or any(i.rule_id == "M-PARSE-E002" for i in extract_issues),
        issues=[],
        raw_yaml=raw_yaml,
        body=body,
    )

    for issue in extract_issues:
        result.issues.append(
            ValidationIssue(
                severity=issue.severity,
                rule_id=issue.rule_id,
                message=issue.message,
                file=rel,
            )
        )
    if extract_issues:
        return result

    if raw_yaml is None:
        result.has_front_matter = False
        result.issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="M-PARSE-E005",
                message="Method data file must have YAML Front Matter.",
                file=rel,
            )
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
    if data is not None:
        result.data = data
    return result
