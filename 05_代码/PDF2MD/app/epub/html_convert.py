"""章节 XHTML / HTML → Markdown。不读 ZIP、不拷图。"""
from __future__ import annotations

import html as html_lib
import re
from collections.abc import Callable
from html.parser import HTMLParser

RewriteHref = Callable[[str], str]
RewriteImage = Callable[[str, str], str]

_SKIP = {"script", "style", "head", "meta", "link", "noscript"}
_VOID = {"img", "br", "hr", "meta", "link", "input", "source", "area", "col"}
_BLOCK = {
    "p",
    "div",
    "section",
    "article",
    "header",
    "footer",
    "aside",
    "main",
    "nav",
    "figure",
    "figcaption",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}


def _strip_doctype(text: str) -> str:
    text = re.sub(r"<\?xml[^?]*\?>", "", text, count=1, flags=re.I)
    return re.sub(r"<!DOCTYPE[^>]*>", "", text, count=1, flags=re.I)


class _XhtmlToMd(HTMLParser):
    def __init__(
        self,
        *,
        rewrite_href: RewriteHref | None = None,
        rewrite_image: RewriteImage | None = None,
    ) -> None:
        super().__init__(convert_charrefs=True)
        self._rewrite_href = rewrite_href
        self._rewrite_image = rewrite_image
        self._out: list[str] = []
        self._skip = 0
        self._in_pre = False
        self._pre_buf: list[str] = []
        self._table_rows: list[list[str]] = []
        self._row: list[str] = []
        self._in_cell = False
        self._cell_buf: list[str] = []
        self._list_stack: list[dict[str, int | str]] = []
        self._in_a = 0
        self._a_href = ""
        self._a_buf: list[str] = []
        self._in_blockquote = 0

    def handle_startendtag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in _VOID or tag == "img":
            self.handle_starttag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in _SKIP:
            self._skip += 1
            return
        if self._skip:
            return
        ad = {k.lower(): (v or "") for k, v in attrs}

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._emit("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "p":
            self._emit("\n\n")
        elif tag == "br":
            self._emit("\n")
        elif tag == "hr":
            self._emit("\n\n---\n\n")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag == "code" and not self._in_pre:
            self._emit("`")
        elif tag == "pre":
            self._in_pre = True
            self._pre_buf = []
        elif tag == "blockquote":
            self._in_blockquote += 1
            self._emit("\n\n")
        elif tag in ("ul", "ol"):
            self._list_stack.append({"type": tag, "n": 0})
            self._emit("\n")
        elif tag == "li":
            depth = max(0, len(self._list_stack) - 1)
            indent = "  " * depth
            kind = self._list_stack[-1]["type"] if self._list_stack else "ul"
            if kind == "ol":
                self._list_stack[-1]["n"] = int(self._list_stack[-1]["n"]) + 1
                n = int(self._list_stack[-1]["n"])
                self._emit(f"\n{indent}{n}. ")
            else:
                self._emit(f"\n{indent}- ")
        elif tag == "table":
            self._table_rows = []
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._in_cell = True
            self._cell_buf = []
        elif tag == "img":
            src = ad.get("src") or ad.get("xlink:href") or ""
            alt = ad.get("alt") or ""
            if self._rewrite_image:
                md = self._rewrite_image(src, alt)
            else:
                md = f"![{alt}]({src})" if src else (alt or "")
            self._emit(md)
        elif tag == "a":
            self._in_a += 1
            if self._in_a == 1:
                self._a_href = ad.get("href") or ""
                self._a_buf = []
        elif tag in _BLOCK:
            self._emit("\n\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p"):
            self._emit("\n\n")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag == "code" and not self._in_pre:
            self._emit("`")
        elif tag == "pre":
            self._in_pre = False
            block = "".join(self._pre_buf).strip("\n")
            self._emit(f"\n\n```\n{block}\n```\n\n")
            self._pre_buf = []
        elif tag == "blockquote":
            self._in_blockquote = max(0, self._in_blockquote - 1)
            self._emit("\n\n")
        elif tag in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()
            self._emit("\n")
        elif tag in ("td", "th"):
            cell = re.sub(r"\s+", " ", "".join(self._cell_buf)).strip()
            self._row.append(cell.replace("|", "\\|"))
            self._in_cell = False
            self._cell_buf = []
        elif tag == "tr":
            if self._row:
                self._table_rows.append(self._row)
            self._row = []
        elif tag == "table":
            self._flush_table()
        elif tag == "a":
            if self._in_a == 1:
                text = "".join(self._a_buf).strip()
                href = self._a_href
                if self._rewrite_href:
                    href = self._rewrite_href(href)
                piece = ""
                if href and text:
                    piece = f"[{text}]({href})"
                elif text:
                    piece = text
                elif href:
                    piece = f"<{href}>"
                self._a_buf = []
                self._a_href = ""
                self._in_a = 0
                if piece:
                    self._emit(piece)
                return
            self._in_a = max(0, self._in_a - 1)
        elif tag in _BLOCK:
            self._emit("\n\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        if self._in_pre:
            self._pre_buf.append(data)
            return
        if self._in_cell:
            self._cell_buf.append(data)
            return
        if self._in_a:
            self._a_buf.append(data)
            return
        self._emit(data)

    def _emit(self, s: str) -> None:
        if self._in_cell:
            self._cell_buf.append(s)
            return
        if self._in_a:
            self._a_buf.append(s)
            return
        self._out.append(s)

    def _flush_table(self) -> None:
        rows = self._table_rows
        self._table_rows = []
        if not rows:
            return
        width = max(len(r) for r in rows)
        norm = [r + [""] * (width - len(r)) for r in rows]
        lines = ["| " + " | ".join(r) + " |" for r in norm]
        sep = "| " + " | ".join("---" for _ in range(width)) + " |"
        lines.insert(1, sep)
        self._emit("\n\n" + "\n".join(lines) + "\n\n")

    def get_markdown(self) -> str:
        text = "".join(self._out)
        text = html_lib.unescape(text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def xhtml_to_markdown(
    html: str,
    *,
    rewrite_href: RewriteHref | None = None,
    rewrite_image: RewriteImage | None = None,
) -> str:
    fragment = _strip_doctype(html or "")
    if not fragment.strip():
        return ""
    parser = _XhtmlToMd(rewrite_href=rewrite_href, rewrite_image=rewrite_image)
    try:
        parser.feed(fragment)
        parser.close()
    except Exception:
        return fragment.strip()
    return parser.get_markdown()
