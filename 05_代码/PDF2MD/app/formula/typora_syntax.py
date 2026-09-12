# -*- coding: utf-8 -*-
"""Typora / KaTeX 可发布语法闸。

Docling CodeFormula 按版面“画”TeX，括号能配平也仍可能无法渲染。
这里只判语法，不发明公式内容。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.utils.typora_math_repair import find_undefined_math_commands

_DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
_INLINE = re.compile(r"(?<!\$)\$(?!\$)((?:\\.|[^$\\])+?)\$(?!\$)")
_FENCE = re.compile(r"```[\s\S]*?```")
_DOLLAR_CLOSED_SUB = re.compile(
    r"\$(?:\\[A-Za-z]+|[A-Za-z])\$[A-Za-z0-9]"
)
_AMP_ENVS = (
    "pmatrix",
    "bmatrix",
    "vmatrix",
    "Bmatrix",
    "Vmatrix",
    "matrix",
    "smallmatrix",
    "array",
    "cases",
    "aligned",
    "align",
    "align*",
    "split",
    "gather",
    "gather*",
    "gathered",
)
_AMP_ENV_RE = re.compile(
    r"\\begin\{("
    + "|".join(re.escape(env) for env in _AMP_ENVS)
    + r")\}.*?\\end\{\1\}",
    re.DOTALL,
)
_BOXED_TEXT = re.compile(
    r"\\(?:text|mathrm|mathbf|mathit|mathsf|mbox|hbox|operatorname|"
    r"textrm|textit|textbf|textcolor)\s*(?:\[[^\]]*\])?\s*\{[^{}]*\}"
)
_CJK = re.compile(r"[\u4e00-\u9fff]")
# 会让 Typora 直接爆红 / 无法对齐的问题才进 validate / 发布闸。
# 公式里夹中文在中文教材里极常见，只进 lint，不因此触发 OCR。
_BLOCKING_CODES = frozenset(
    {
        "undefined_tex_command",
        "amp_outside_alignment",
        "left_right_mismatch",
        "broken_set_builder",
        "dollar_closed_subscript",
        "katex_parse_failed",
    }
)


@dataclass(frozen=True)
class TyporaSyntaxIssue:
    code: str
    message: str
    snippet: str = ""


def _strip_alignment_envs(body: str) -> str:
    prev = None
    out = body
    while prev != out:
        prev = out
        out = _AMP_ENV_RE.sub(" ", out)
    return out


def assess_typora_syntax(body: str, *, use_katex: bool = True) -> list[TyporaSyntaxIssue]:
    """检查单条公式体（不含外围 $ / $$）。"""
    raw = (body or "").strip()
    if not raw:
        return []
    issues: list[TyporaSyntaxIssue] = []
    snippet = raw[:120]

    for cmd in find_undefined_math_commands(raw):
        issues.append(
            TyporaSyntaxIssue(
                code="undefined_tex_command",
                message=f"未定义 LaTeX 命令 \\{cmd}",
                snippet=snippet,
            )
        )

    stripped = _strip_alignment_envs(raw)
    if "&" in stripped:
        issues.append(
            TyporaSyntaxIssue(
                code="amp_outside_alignment",
                message="& 出现在 aligned/array/matrix 之外（Typora 无法对齐）",
                snippet=snippet,
            )
        )

    lefts = len(re.findall(r"\\left(?![A-Za-z])", raw))
    rights = len(re.findall(r"\\right(?![A-Za-z])", raw))
    if lefts != rights:
        issues.append(
            TyporaSyntaxIssue(
                code="left_right_mismatch",
                message=r"\left / \right 数量不匹配",
                snippet=snippet,
            )
        )

    if re.search(r"\\left\s*\\\{.*?\\right\s*\|", raw, re.DOTALL):
        issues.append(
            TyporaSyntaxIssue(
                code="broken_set_builder",
                message=r"\left\{ ... \right| 会提前结束定界（应用 \mid）",
                snippet=snippet,
            )
        )

    unboxed = _BOXED_TEXT.sub(" ", raw)
    if _CJK.search(unboxed):
        issues.append(
            TyporaSyntaxIssue(
                code="cjk_in_math",
                message="数学模式里有未放入 \\text 的中文",
                snippet=snippet,
            )
        )

    # 启发式都过了、且含 TeX 命令才问 KaTeX（无反斜杠的 E=mc^2 不必起 Node）
    if (
        use_katex
        and "\\" in raw
        and not any(i.code in _BLOCKING_CODES for i in issues)
    ):
        from app.formula.katex_engine import katex_validate

        ok, err = katex_validate(raw, display=True)
        if ok is False:
            issues.append(
                TyporaSyntaxIssue(
                    code="katex_parse_failed",
                    message=f"KaTeX 无法解析：{err[:160]}",
                    snippet=snippet,
                )
            )

    return issues


def blocking_typora_issues(
    body: str,
    *,
    extra: list[TyporaSyntaxIssue] | None = None,
    use_katex: bool = True,
) -> list[TyporaSyntaxIssue]:
    issues = list(assess_typora_syntax(body, use_katex=use_katex))
    if extra:
        issues.extend(extra)
    return [i for i in issues if i.code in _BLOCKING_CODES]


def is_typora_publishable(body: str) -> bool:
    return not blocking_typora_issues(body)


def _looks_like_math_span(body: str, *, display: bool) -> bool:
    """丢掉未配对 $ 吞进去的大段中文正文，避免发布闸误报。"""
    if not body:
        return False
    if display:
        return True
    if len(body) > 220 and len(_CJK.findall(body)) >= 12:
        return False
    return True


def iter_math_bodies(md: str) -> list[tuple[str, str]]:
    """返回 [(mode, body), ...]，display 优先，再扫去掉 $$ 后的行内公式。"""
    if not md:
        return []
    plain = _FENCE.sub(" ", md)
    out: list[tuple[str, str]] = []
    for m in _DISPLAY.finditer(plain):
        body = (m.group(1) or "").strip()
        if body and _looks_like_math_span(body, display=True):
            out.append(("display", body))
    no_display = _DISPLAY.sub(" ", plain)
    for m in _INLINE.finditer(no_display):
        body = (m.group(1) or "").strip()
        if body and _looks_like_math_span(body, display=False):
            out.append(("inline", body))
    return out


def assess_markdown_typora_syntax(md: str) -> list[TyporaSyntaxIssue]:
    """扫描整篇 Markdown 的公式与 $\\theta$n 切断下标。"""
    issues: list[TyporaSyntaxIssue] = []
    if not md:
        return issues
    plain = _FENCE.sub(" ", md)
    if _DOLLAR_CLOSED_SUB.search(plain):
        issues.append(
            TyporaSyntaxIssue(
                code="dollar_closed_subscript",
                message="行内 $ 在下标前关闭（如 $\\theta$n）",
                snippet=_DOLLAR_CLOSED_SUB.search(plain).group(0),
            )
        )
    pending: list[str] = []
    for _mode, body in iter_math_bodies(md):
        local = assess_typora_syntax(body, use_katex=False)
        issues.extend(local)
        if "\\" in body and not any(i.code in _BLOCKING_CODES for i in local):
            pending.append(body)
    if pending:
        from app.formula.katex_engine import katex_validate_many

        for body, (ok, err) in zip(pending, katex_validate_many(pending)):
            if ok is False:
                issues.append(
                    TyporaSyntaxIssue(
                        code="katex_parse_failed",
                        message=f"KaTeX 无法解析：{err[:160]}",
                        snippet=body[:120],
                    )
                )
    return issues


def count_unpublishable_math(md: str) -> int:
    """发布闸用：仍无法在 Typora 渲染的公式条数（不含中文夹杂）。"""
    if not md:
        return 0
    n = 0
    plain = _FENCE.sub(" ", md)
    n += len(_DOLLAR_CLOSED_SUB.findall(plain))
    pending: list[str] = []
    for _mode, body in iter_math_bodies(md):
        if blocking_typora_issues(body, use_katex=False):
            n += 1
        elif "\\" in body:
            pending.append(body)
    if pending:
        from app.formula.katex_engine import katex_validate_many

        for ok, _err in katex_validate_many(pending):
            if ok is False:
                n += 1
    return n
