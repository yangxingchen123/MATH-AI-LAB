"""v1.8 research writing and artifact consistency checks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

INCLUDEGRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
KNOWLEDGE_ID = re.compile(r"^id:\s*(K\d+)", re.MULTILINE)
CITE_RE = re.compile(r"\\cite\{([^}]+)\}")
LEANREF_RE = re.compile(r"\\leanref\{([^}]+)\}")
AIC_MARKER = "AI_CONTRIBUTION"


@dataclass(frozen=True)
class ConsistencyResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


def check_latex_figures(tex_root: Path, artifact_root: Path) -> ConsistencyResult:
    errors: list[str] = []
    for tex in sorted(Path(tex_root).rglob("*.tex")):
        text = tex.read_text(encoding="utf-8")
        for match in INCLUDEGRAPHICS.finditer(text):
            name = Path(match.group(1)).stem
            manifest = Path(artifact_root) / name / "manifest.yaml"
            if not manifest.is_file():
                errors.append(f"unprovenanced figure {match.group(1)} in {tex.as_posix()}")
    return ConsistencyResult(ok=not errors, errors=errors)


def check_knowledge_promotion(knowledge_root: Path, *, authorized: bool) -> ConsistencyResult:
    errors: list[str] = []
    root = Path(knowledge_root)
    if not root.exists():
        return ConsistencyResult(ok=True)
    created = []
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if KNOWLEDGE_ID.search(text) or path.name.startswith("K"):
            created.append(path.as_posix())
    if created and not authorized:
        errors.append("Knowledge created without 开始知识沉淀: " + ", ".join(created))
    return ConsistencyResult(ok=not errors, errors=errors)


def check_p9_publish_boundary(write_path: Path, formal_pdf_root: Path) -> ConsistencyResult:
    """Compiler writes into formal PDF root are forbidden except via tools.latex_build."""
    errors: list[str] = []
    try:
        write_path.resolve().relative_to(Path(formal_pdf_root).resolve())
        inside = True
    except ValueError:
        inside = False
    if inside:
        errors.append("direct write into formal PDF root is forbidden; use tools.latex_build build")
    return ConsistencyResult(ok=not errors, errors=errors)


def check_citations(tex_text: str, literature_keys: set[str]) -> ConsistencyResult:
    errors: list[str] = []
    for group in CITE_RE.findall(tex_text):
        for key in (part.strip() for part in group.split(",")):
            if key and key not in literature_keys:
                errors.append(f"unknown citation key: {key}")
    return ConsistencyResult(ok=not errors, errors=errors)


def check_lean_refs(tex_text: str, formal_refs: set[str]) -> ConsistencyResult:
    errors: list[str] = []
    for ref in LEANREF_RE.findall(tex_text):
        if ref not in formal_refs:
            errors.append(f"unknown lean ref: {ref}")
    return ConsistencyResult(ok=not errors, errors=errors)


def check_ai_contribution(paper_text: str, governance_text: str) -> ConsistencyResult:
    errors: list[str] = []
    claims_ai = "AI" in paper_text and ("generated" in paper_text.lower() or "贡献" in paper_text)
    if claims_ai and AIC_MARKER not in governance_text:
        errors.append("AI contribution claimed without AI_CONTRIBUTION record")
    return ConsistencyResult(ok=not errors, errors=errors)
