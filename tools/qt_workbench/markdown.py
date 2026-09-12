"""Typora-like Markdown + math HTML for the Qt reading pane.

stdlib only. KaTeX assets come from tools/studio/static/vendor (already vendored).
This is a display pipeline, not Frozen Schema.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import NamedTuple

from .style import DARK, LIGHT

VENDOR_DIR = Path(__file__).resolve().parent.parent / "studio" / "static" / "vendor"

FENCE_RE = re.compile(r"```([^\n]*)\n?([\s\S]*?)```")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
DISPLAY_RE = re.compile(r"\$\$([\s\S]+?)\$\$")
BRACKET_RE = re.compile(r"\\\[([\s\S]+?)\\\]")
PAREN_RE = re.compile(r"\\\(([\s\S]+?)\\\)")
INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+)\$(?!\$)")
UNCLOSED_DISPLAY_RE = re.compile(r"\$\$([^$]*)")
UNCLOSED_INLINE_RE = re.compile(r"\$([^$\n]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
HR_RE = re.compile(r"^\s*([-*_])\1{2,}\s*$")
UL_RE = re.compile(r"^[-*+]\s+")
OL_RE = re.compile(r"^\d+\.\s+")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")
CODE_TOKEN_RE = re.compile(r"^@@CODE(\d+)@@$")
MATH_TOKEN_RE = re.compile(r"@@MATH(\d+)@@")
P_MATH_RE = re.compile(r"<p>\s*@@MATH(\d+)@@\s*</p>")
P_CODE_RE = re.compile(r"(?:<p>)?@@CODE(\d+)@@(?:</p>)?")


class MathSlot(NamedTuple):
    tex: str
    display: bool


def vendor_href() -> str:
    uri = VENDOR_DIR.resolve().as_uri()
    return uri if uri.endswith("/") else uri + "/"


def _asset_uri(name: str) -> str:
    return (VENDOR_DIR / name).resolve().as_uri()


def render_body_html(source: str) -> str:
    text = (source or "").replace("\r\n", "\n")
    protected, code_bags = _protect_code(text)
    working, slots = _extract_math(protected)
    html_body = _markdown_to_html(working)
    html_body = _restore_code(html_body, code_bags)
    return _restore_math(html_body, slots)


def render_reading_page(source: str, *, dark: bool = True) -> str:
    tokens = DARK if dark else LIGHT
    body = render_body_html(source)
    css = html.escape(_asset_uri("katex.min.css"), quote=True)
    katex = html.escape(_asset_uri("katex.min.js"), quote=True)
    auto = html.escape(_asset_uri("auto-render.min.js"), quote=True)
    return (
        "<!DOCTYPE html><html lang='zh-CN'><head>"
        "<meta charset='utf-8'>"
        f"<base href='{html.escape(vendor_href(), quote=True)}'>"
        f"<link rel='stylesheet' href='{css}'>"
        f"<style>{_page_css(tokens)}</style>"
        "</head><body>"
        f"<article class='reading'>{body}</article>"
        f"<script src='{katex}'></script>"
        f"<script src='{auto}'></script>"
        "<script>"
        "if (typeof renderMathInElement === 'function') {"
        "  renderMathInElement(document.body, {"
        "    delimiters: ["
        "      {left: '$$', right: '$$', display: true},"
        "      {left: '\\\\[', right: '\\\\]', display: true},"
        "      {left: '$', right: '$', display: false},"
        "      {left: '\\\\(', right: '\\\\)', display: false}"
        "    ],"
        "    throwOnError: false,"
        "    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']"
        "  });"
        "}"
        "</script>"
        "</body></html>"
    )


def _protect_code(source: str) -> tuple[str, list[str]]:
    bags: list[str] = []

    def hold(match: re.Match[str]) -> str:
        bags.append(match.group(0))
        return f"@@CODE{len(bags) - 1}@@"

    text = FENCE_RE.sub(hold, source)
    text = INLINE_CODE_RE.sub(hold, text)
    return text, bags


def _extract_math(source: str) -> tuple[str, list[MathSlot]]:
    slots: list[MathSlot] = []

    def hold(display: bool, tex: str) -> str:
        slots.append(MathSlot(tex=tex, display=display))
        token = f"@@MATH{len(slots) - 1}@@"
        return f"\n\n{token}\n\n" if display else token

    text = DISPLAY_RE.sub(lambda m: hold(True, m.group(1)), source)
    text = BRACKET_RE.sub(lambda m: hold(True, m.group(1)), text)
    text = PAREN_RE.sub(lambda m: hold(False, m.group(1)), text)
    text = INLINE_MATH_RE.sub(lambda m: hold(False, m.group(1)), text)
    text = UNCLOSED_DISPLAY_RE.sub(lambda m: hold(True, m.group(1)), text)
    text = UNCLOSED_INLINE_RE.sub(lambda m: hold(False, m.group(1)), text)
    return text, slots


def _markdown_to_html(source: str) -> str:
    lines = source.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            index += 1
            continue
        token = CODE_TOKEN_RE.match(raw.strip())
        if token:
            out.append(raw.strip())
            index += 1
            continue
        heading = HEADING_RE.match(raw)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            index += 1
            continue
        if HR_RE.match(raw):
            out.append("<hr />")
            index += 1
            continue
        if raw.lstrip().startswith(">"):
            chunk, index = _collect_blockquote(lines, index)
            out.append(chunk)
            continue
        if UL_RE.match(raw) or OL_RE.match(raw):
            chunk, index = _collect_list(lines, index)
            out.append(chunk)
            continue
        if "|" in raw and index + 1 < len(lines) and TABLE_SEP_RE.match(lines[index + 1]):
            chunk, index = _collect_table(lines, index)
            out.append(chunk)
            continue
        chunk, index = _collect_paragraph(lines, index)
        out.append(chunk)
    return "\n".join(out)


def _collect_blockquote(lines: list[str], start: int) -> tuple[str, int]:
    rows: list[str] = []
    index = start
    while index < len(lines) and lines[index].lstrip().startswith(">"):
        rows.append(re.sub(r"^\s*>\s?", "", lines[index]))
        index += 1
    inner = _inline(" ".join(row.strip() for row in rows if row.strip()))
    return f"<blockquote><p>{inner}</p></blockquote>", index


def _collect_list(lines: list[str], start: int) -> tuple[str, int]:
    ordered = OL_RE.match(lines[start]) is not None
    items: list[str] = []
    index = start
    pattern = OL_RE if ordered else UL_RE
    while index < len(lines) and pattern.match(lines[index]):
        text = pattern.sub("", lines[index], count=1)
        items.append(f"<li>{_inline(text)}</li>")
        index += 1
    tag = "ol" if ordered else "ul"
    return f"<{tag}>{''.join(items)}</{tag}>", index


def _collect_table(lines: list[str], start: int) -> tuple[str, int]:
    rows: list[str] = [lines[start]]
    index = start + 2
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        rows.append(lines[index])
        index += 1

    def cells(line: str) -> list[str]:
        stripped = line.strip()
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        return [_inline(part.strip()) for part in stripped.split("|")]

    header = "".join(f"<th>{cell}</th>" for cell in cells(rows[0]))
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells(row)) + "</tr>" for row in rows[1:]
    )
    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>", index


def _collect_paragraph(lines: list[str], start: int) -> tuple[str, int]:
    rows: list[str] = [lines[start]]
    index = start + 1
    while index < len(lines):
        nxt = lines[index]
        if not nxt.strip():
            break
        if HEADING_RE.match(nxt) or HR_RE.match(nxt) or CODE_TOKEN_RE.match(nxt.strip()):
            break
        if UL_RE.match(nxt) or OL_RE.match(nxt) or nxt.lstrip().startswith(">"):
            break
        if "|" in nxt and index + 1 < len(lines) and TABLE_SEP_RE.match(lines[index + 1]):
            break
        rows.append(nxt)
        index += 1
    text = "<br />".join(_inline(row.strip()) for row in rows)
    return f"<p>{text}</p>", index


def _inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: _link(m.group(1), m.group(2)),
        escaped,
    )
    return escaped


def _link(label: str, url: str) -> str:
    href = url.strip()
    if not href.startswith(("http://", "https://", "mailto:", "#")):
        return label
    return f'<a href="{html.escape(href, quote=True)}">{label}</a>'


def _restore_code(fragment: str, bags: list[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if index >= len(bags):
            return ""
        return _code_to_html(bags[index])

    return P_CODE_RE.sub(repl, fragment)


def _code_to_html(raw: str) -> str:
    if raw.startswith("```"):
        match = re.match(r"^```([^\n]*)\n?([\s\S]*?)```$", raw)
        lang = (match.group(1) if match else "").strip()
        body = match.group(2) if match else raw
        cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
        return f"<pre><code{cls}>{html.escape(body, quote=False)}</code></pre>"
    return f"<code>{html.escape(raw.strip('`'), quote=False)}</code>"


def _restore_math(fragment: str, slots: list[MathSlot]) -> str:
    def render(index: int) -> str:
        if index >= len(slots):
            return ""
        slot = slots[index]
        tex = html.escape(slot.tex.strip(), quote=False)
        if slot.display:
            return f'<div class="math-display">$${tex}$$</div>'
        return f"${tex}$"

    def block(match: re.Match[str]) -> str:
        return render(int(match.group(1)))

    html_body = P_MATH_RE.sub(block, fragment)
    return MATH_TOKEN_RE.sub(lambda m: render(int(m.group(1))), html_body)


def _page_css(t: dict[str, str]) -> str:
    return f"""
html, body {{
  margin: 0;
  padding: 0;
  background: {t["paper"]};
  color: {t["ink"]};
  font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
  font-size: 16px;
  line-height: 1.75;
}}
article.reading {{
  padding: 4px 8px 48px 2px;
  max-width: 46rem;
}}
h1, h2, h3, h4 {{
  color: {t["ink"]};
  font-weight: 650;
  line-height: 1.35;
  margin: 1.55em 0 0.55em;
}}
h1 {{ font-size: 1.7em; margin-top: 0.2em; }}
h2 {{ font-size: 1.32em; }}
h3 {{ font-size: 1.12em; }}
p {{ margin: 0.85em 0; }}
strong {{ font-weight: 650; }}
em {{ font-style: italic; }}
code {{
  font-family: Consolas, "Cascadia Mono", "Microsoft YaHei UI", monospace;
  font-size: 0.9em;
  background: {t["chip"]};
  padding: 0.08em 0.35em;
  border-radius: 4px;
}}
pre {{
  background: {t["bg"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 12px 14px;
  overflow: auto;
}}
pre code {{ background: none; padding: 0; }}
hr {{
  border: none;
  border-top: 1px solid {t["line"]};
  margin: 1.5em 0;
}}
ul, ol {{ padding-left: 1.4em; }}
li {{ margin: 0.25em 0; }}
blockquote {{
  margin: 1em 0;
  padding: 0.15em 0 0.15em 1em;
  border-left: 3px solid {t["accent"]};
  color: {t["muted"]};
}}
table {{
  border-collapse: collapse;
  margin: 1em 0;
}}
th, td {{
  border: 1px solid {t["line"]};
  padding: 6px 10px;
}}
a {{ color: {t["accent"]}; }}
.math-display {{
  overflow-x: auto;
  padding: 0.35em 0 0.7em;
  text-align: center;
}}
.katex {{ color: inherit; }}
.katex-display {{ margin: 0.6em 0; }}
"""
