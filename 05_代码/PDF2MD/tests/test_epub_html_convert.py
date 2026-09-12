# -*- coding: utf-8 -*-
from __future__ import annotations

from app.epub.assemble import apply_export_rules
from app.epub.html_convert import xhtml_to_markdown


def test_headings_lists_links():
    html = """
    <html><body>
      <h1>Title</h1>
      <p>See <a href="ch2.xhtml#sec">next</a>.</p>
      <ul><li>a</li><li>b</li></ul>
      <ol><li>one</li></ol>
    </body></html>
    """
    md = xhtml_to_markdown(html, rewrite_href=lambda h: "#sec" if "#" in h else h)
    assert md.startswith("# Title")
    assert "[next](#sec)" in md
    assert "- a" in md
    assert "- b" in md
    assert "1. one" in md


def test_table_and_image():
    html = """
    <p><img src="cover.png" alt="cover"/></p>
    <table>
      <tr><th>A</th><th>B</th></tr>
      <tr><td>1</td><td>2</td></tr>
    </table>
    """
    md = xhtml_to_markdown(
        html,
        rewrite_image=lambda src, alt: f"![{alt}](images/{src})",
    )
    assert "![cover](images/cover.png)" in md
    assert "| A | B |" in md
    assert "| 1 | 2 |" in md


def test_export_rules_table_image_gap():
    raw = "| A | B |\n| --- | --- |\n| 1 | 2 |\n![cover](images/cover.png)\n"
    out = apply_export_rules(raw)
    assert "|\n\n![" in out or "|\r\n\r\n![" in out
