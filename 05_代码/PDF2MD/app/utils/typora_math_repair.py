# -*- coding: utf-8 -*-
"""Typora/MathJax 兼容：指标 OCR 错字与假 LaTeX 命令修复（不发明公式结构）。"""
from __future__ import annotations

import re
from dataclasses import dataclass

# 标准 AMS/MathJax 常见命令 + 本项目常用；不在表内且非希腊字母 → 假命令
_KNOWN_MATH_COMMANDS = frozenset(
    {
        "frac",
        "sum",
        "prod",
        "int",
        "mathrm",
        "mathbf",
        "mathit",
        "mathcal",
        "mathbb",
        "operatorname",
        "text",
        "hat",
        "bar",
        "tilde",
        "vec",
        "dot",
        "ddot",
        "cdot",
        "times",
        "pm",
        "mp",
        "leq",
        "geq",
        "neq",
        "approx",
        "equiv",
        "infty",
        "partial",
        "nabla",
        "left",
        "right",
        "begin",
        "end",
        "tag",
        "label",
        "ref",
        "quad",
        "qquad",
        "hspace",
        "vspace",
        "displaystyle",
        "limits",
        "arg",
        "max",
        "min",
        "log",
        "ln",
        "exp",
        "sin",
        "cos",
        "tan",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "varepsilon",
        "theta",
        "lambda",
        "mu",
        "sigma",
        "omega",
        "Gamma",
        "Delta",
        "Theta",
        "Lambda",
        "Sigma",
        "Omega",
        "colon",
        "to",
        "rightarrow",
        "Rightarrow",
        "Leftrightarrow",
        "forall",
        "exists",
        "in",
        "notin",
        "subset",
        "cup",
        "cap",
        "setminus",
        "emptyset",
        "cdots",
        "ldots",
        "vdots",
        "ddots",
        "stackrel",
        "overset",
        "underset",
        "binom",
        "choose",
        "atop",
        "over",
        "brace",
        "brack",
    }
)

_FAKE_CMD_FIXES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\\Precisio(?=_|\{|$)", re.I), r"\\mathrm{Precision}"),
    (re.compile(r"\\Precisi(?=_|\{|$)", re.I), r"\\mathrm{Precision}"),
    (re.compile(r"\\Recall(?=_|\{|$)"), r"\\mathrm{Recall}"),
    (re.compile(r"\\cdotMetric(?=\.|_|\\b|$)"), r"\\cdot \\mathrm{Metric}"),
    (re.compile(r"\\cdotMeric(?=\.|_|\\b|$)"), r"\\cdot \\mathrm{Metric}"),
)

_PLAIN_TYPO_FIXES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bAcuracy\b"), "Accuracy"),
    (re.compile(r"\bPrecisi(?=_|\b)"), "Precision"),
    (re.compile(r"\bPrecisio(?=_|\b)"), "Precision"),
    (re.compile(r"\bMeric(?=_|\b)"), "Metric"),
    (re.compile(r"\bMetricweighets\b"), r"\\mathrm{Metric}_{\\mathrm{weighted}}"),
)

_DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)


@dataclass(frozen=True)
class TyporaMathIssue:
    code: str
    message: str
    snippet: str = ""


def find_undefined_math_commands(body: str) -> list[str]:
    """返回疑似未定义 \\Command（Typora 爆红源）。"""
    unknown: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"\\([A-Za-z]+)", body or ""):
        cmd = m.group(1)
        if cmd in _KNOWN_MATH_COMMANDS:
            continue
        if cmd in seen:
            continue
        seen.add(cmd)
        unknown.append(cmd)
    return unknown


def repair_typora_math_body(body: str) -> str:
    """修单行公式体（不含外围 $$）。"""
    s = (body or "").strip()
    if not s:
        return s

    for pat, repl in _FAKE_CMD_FIXES:
        s = pat.sub(repl, s)
    for pat, repl in _PLAIN_TYPO_FIXES:
        s = pat.sub(repl, s)

    # Docling 拆字下标：M _ { i j } → M_{ij}
    def _compact_subscript(m: re.Match[str]) -> str:
        inner = re.sub(r"\s+", "", m.group(2))
        return f"{m.group(1)}_{{{inner}}}"

    s = re.sub(
        r"([A-Za-z])\s+_\s*\{\s*([^}]+)\s*\}",
        _compact_subscript,
        s,
    )
    # A U C _ { c } → AUC_{c}
    def _compact_spaced_subscript(m: re.Match[str]) -> str:
        base = re.sub(r"\s+", "", m.group(1))
        inner = re.sub(r"\s+", "", m.group(2))
        return f"{base}_{{{inner}}}"

    s = re.sub(
        r"\b((?:[A-Za-z]\s+){1,6}[A-Za-z])\s+_\s*\{\s*([^}]+)\s*\}",
        _compact_spaced_subscript,
        s,
    )
    # 混淆矩阵：iand\hat → i \text{ and } \hat
    s = re.sub(
        r"=\s*i\s*and\s*\\hat",
        r"= i \\text{ and } \\hat",
        s,
        flags=re.I,
    )
    s = re.sub(r"iand\\hat", r"i \\text{ and } \\hat", s, flags=re.I)
    s = re.sub(r"\\hat\s*\{\s*y\s*\}\s*_\s*\{\s*k\s*\}", r"\\hat{y}_{k}", s)

    # 指标名统一用 \mathrm{}（仅常见 TP/FP 分式块）
    if re.search(r"TP_\{c\}|TP_c|FP_\{c\}|FN_\{c\}", s):
        s = re.sub(
            r"(?<![\\a-zA-Z])Accuracy(?=_|\b|=)",
            r"\\mathrm{Accuracy}",
            s,
        )
        s = re.sub(
            r"(?<![\\a-zA-Z])Precision(?=_|\b|=)",
            r"\\mathrm{Precision}",
            s,
        )
        s = re.sub(
            r"(?<![\\a-zA-Z])Recall(?=_|\b|=)",
            r"\\mathrm{Recall}",
            s,
        )
        s = re.sub(r"(?<![\\a-zA-Z])F1(?=_|\b|=)", r"\\mathrm{F1}", s)
        s = re.sub(
            r"(?<![\\a-zA-Z])Metric(?=_|\b|=)",
            r"\\mathrm{Metric}",
            s,
        )

    return s.strip()


def audit_typora_red_risk(md: str) -> dict:
    """Typora 整篇爆红风险：未闭合 $$、标题粘 $、图片 URL 里的 $。"""
    text = md or ""
    bodies = list(_DISPLAY.finditer(text))
    used: set[int] = set()
    for m in bodies:
        used.add(m.start())
        used.add(m.end() - 2)
    unpaired = [m.start() for m in re.finditer(r"\$\$", text) if m.start() not in used]
    heading_open = re.findall(r"(?m)^(#{1,6}\s+[\d.]*)\$([^\n$]*)", text)
    img_dollar = 0
    for m in re.finditer(
        r"!\[[^\]]*\]\(([\s\S]*?\.(?:png|jpg|jpeg|webp|gif))\)", text, re.I
    ):
        if "$" in (m.group(1) or ""):
            img_dollar += 1
    swallowed = 0
    for m in bodies:
        b = m.group(1) or ""
        if ("![" in b or re.search(r"(?m)^#{1,6}\s", b)) and len(b) > 200:
            swallowed += 1
    stripped = _DISPLAY.sub("", text)
    odd_inline = stripped.count("$") % 2
    heading_hash_dollar = len(re.findall(r"(?m)^#{1,6}\$", text))
    midline_dd = len(re.findall(r"(?<!\n)\$\$(?!\n)", text))
    red_risk = bool(
        unpaired
        or heading_open
        or heading_hash_dollar
        or img_dollar
        or swallowed
        or odd_inline
    )
    return {
        "n_dollar": text.count("$"),
        "n_dd": text.count("$$"),
        "unpaired_dd": len(unpaired),
        "odd_inline_dollar": odd_inline,
        "heading_dollar_open": len(heading_open),
        "heading_hash_dollar": heading_hash_dollar,
        "img_dollar": img_dollar,
        "midline_dd": midline_dd,
        "swallowed_md_in_display": swallowed,
        "red_risk": red_risk,
        "heading_samples": [h[0] + "$" + h[1][:40] for h in heading_open[:3]],
        "unpaired_at": unpaired[:5],
    }


_SINGLE_LINE_DISPLAY = re.compile(r"^\s*\$\$(.+)\$\$\s*$")
_BARE_DISPLAY = re.compile(r"^\s*\$\$\s*$")
_ATX_HEADING = re.compile(r"^#{1,6}(?:\s|$|\$)")


def _sanitize_heading_core(core: str) -> str:
    """只处理 ATX 标题。#include 不是标题；奇数 $ 时只去掉多余的那一个，保留成对公式。"""
    m = re.match(r"^(#{1,6})(.*)$", core)
    if not m:
        return core
    hashes, rest = m.group(1), m.group(2)
    if rest and rest[0] not in " \t$":
        return core
    if rest.startswith("$") and not rest.startswith("$$"):
        rest = rest[1:]
    rest = rest.lstrip()
    rest = re.sub(r"(?<=[\d.])\$(?=[\u4e00-\u9fff])", " ", rest)
    if rest.count("$") % 2 == 1 and rest.startswith("$"):
        rest = rest[1:].lstrip()
    if rest.count("$") % 2 == 1 and rest.endswith("$") and not rest.endswith("$$"):
        rest = rest[:-1].rstrip()
    if rest.count("$") % 2 == 1:
        rest2, n = re.subn(r"\$(?=\d)", "", rest, count=1)
        if n and rest2.count("$") % 2 == 0:
            rest = rest2
    rest = rest.strip()
    return hashes + (" " + rest if rest else "")


def _strip_dollars_in_images(md: str) -> str:
    out: list[str] = []
    i = 0
    n = len(md)
    while i < n:
        start = md.find("![", i)
        if start < 0:
            out.append(md[i:])
            break
        rb = md.find("](", start)
        if rb < 0 or rb < start:
            out.append(md[i:])
            break
        depth = 1
        p = rb + 2
        while p < n and depth:
            if md[p] == "(":
                depth += 1
            elif md[p] == ")":
                depth -= 1
            p += 1
        if depth != 0:
            out.append(md[i : start + 2])
            i = start + 2
            continue
        url = md[rb + 2 : p - 1]
        if "$" in url:
            url = url.replace("$", "")
        out.append(md[i : rb + 2])
        out.append(url)
        out.append(")")
        i = p
    return "".join(out)


def _split_glued_inlines_outside_math(md: str) -> str:
    """只拆正文里的 `$a$$b$`，不动行间公式和代码围栏。"""
    out: list[str] = []
    in_fence = False
    in_display = False
    for line in md.splitlines(keepends=True):
        raw, nl = (line[:-1], "\n") if line.endswith("\n") else (line, "")
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if _SINGLE_LINE_DISPLAY.match(raw):
            out.append(line)
            continue
        if _BARE_DISPLAY.match(raw):
            in_display = not in_display
            out.append(line)
            continue
        if in_display:
            out.append(line)
            continue
        out.append(re.sub(r"(?<=[^$])\$\$(?=[^$])", "$ $", raw) + nl)
    return "".join(out)


def _drop_unclosed_bare_display(md: str) -> str:
    """代码围栏外，独立 $$ 行若不成对，丢掉最后那个开门的 $$。"""
    lines = md.splitlines(keepends=True)
    in_fence = False
    bare_idx: list[int] = []
    for i, line in enumerate(lines):
        raw = line[:-1] if line.endswith("\n") else line
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or _SINGLE_LINE_DISPLAY.match(raw):
            continue
        if _BARE_DISPLAY.match(raw):
            bare_idx.append(i)
    if len(bare_idx) % 2 == 0:
        return md
    del lines[bare_idx[-1]]
    return "".join(lines)


def sanitize_typora_math_fences(md: str) -> str:
    """转换出口消毒：去掉会让 Typora 整篇爆红的未闭合 $ / $$，不改公式内容。"""
    if not md:
        return md
    lines: list[str] = []
    in_fence = False
    for line in md.splitlines(keepends=True):
        raw, nl = (line[:-1], "\n") if line.endswith("\n") else (line, "")
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        if in_fence:
            lines.append(line)
            continue
        core = raw.lstrip()
        indent = raw[: len(raw) - len(core)]
        if _ATX_HEADING.match(core):
            lines.append(indent + _sanitize_heading_core(core) + nl)
        else:
            lines.append(raw + nl)
    text = "".join(lines)
    text = _split_glued_inlines_outside_math(text)
    text = _strip_dollars_in_images(text)
    text = _drop_unclosed_bare_display(text)
    return text


def map_display_blocks(md: str, rewrite_body) -> str:
    """对代码围栏外的行间公式调用 rewrite_body(body) → 整段替换文本。

    只认整行 `$$` 或单行 `$$...$$`。行内 `$a$$b$`、公式体里的 `$$` 不当成围栏结束。
    """
    if not md or "$$" not in md:
        return md
    lines = md.splitlines(keepends=True)
    out: list[str] = []
    in_fence = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        raw = line[:-1] if line.endswith("\n") else line
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue
        sm = _SINGLE_LINE_DISPLAY.match(raw)
        if sm:
            out.append(rewrite_body(sm.group(1)))
            if line.endswith("\n") and not out[-1].endswith("\n"):
                out[-1] += "\n"
            i += 1
            continue
        if _BARE_DISPLAY.match(raw):
            j = i + 1
            found = None
            while j < n:
                raw_j = lines[j][:-1] if lines[j].endswith("\n") else lines[j]
                if raw_j.strip().startswith("```"):
                    break
                if _BARE_DISPLAY.match(raw_j):
                    found = j
                    break
                j += 1
            if found is None:
                out.append(line)
                i += 1
                continue
            body = "".join(lines[i + 1 : found])
            if body.endswith("\n"):
                body = body[:-1]
            repl = rewrite_body(body)
            out.append(repl)
            if lines[found].endswith("\n") and not out[-1].endswith("\n"):
                out[-1] += "\n"
            i = found + 1
            continue
        out.append(line)
        i += 1
    return "".join(out)


def repair_typora_math_in_markdown(md: str) -> str:
    if not md or "$$" not in md:
        return md

    def _rew(body: str) -> str:
        return f"$$\n{repair_typora_math_body(body or '')}\n$$"

    return map_display_blocks(md, _rew)
    """扫描最终 MD；用于 repair.json / 批跑汇总。"""
    issues: list[TyporaMathIssue] = []
    if not md:
        return issues

    for m in _DISPLAY.finditer(md):
        body = (m.group(1) or "").strip()
        if not body:
            continue
        for cmd in find_undefined_math_commands(body):
            issues.append(
                TyporaMathIssue(
                    code="T-undef-cmd",
                    message=f"未定义 LaTeX 命令 \\{cmd}",
                    snippet=body[:120],
                )
            )
        for typo_pat, _ in _PLAIN_TYPO_FIXES:
            if typo_pat.search(body):
                issues.append(
                    TyporaMathIssue(
                        code="T-metric-typo",
                        message="疑似指标名 OCR 错字",
                        snippet=body[:120],
                    )
                )
                break
    return issues
