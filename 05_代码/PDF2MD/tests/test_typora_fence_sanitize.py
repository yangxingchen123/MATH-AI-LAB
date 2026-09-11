# -*- coding: utf-8 -*-
"""Typora 整篇爆红：转换不得把汉字吞进 $，出口必须消掉未闭合围栏。"""
from __future__ import annotations

from app.utils.md_postprocess import convert_inline_unicode_math, postprocess_markdown
from app.utils.typora_math_repair import audit_typora_red_risk, sanitize_typora_math_fences


def test_cjk_not_swallowed_into_inline_math():
    out = convert_inline_unicode_math("正文 α∈G。\n", mode="safe")
    assert "$正文" not in out
    assert r"\alpha" in out and r"\in" in out
    assert out.count("$") % 2 == 0


def test_heading_unicode_subscript_does_not_wrap_title():
    out = convert_inline_unicode_math("## 1.1 群 G₁ 与半群\n", mode="safe")
    assert not out.startswith("## $1.1")
    assert "G_{1}" in out
    assert audit_typora_red_risk(out)["heading_dollar_open"] == 0 or out.count("$") % 2 == 0


def test_sanitize_unclosed_heading_dollar():
    src = "### $6.3 高阶线性微分方程式\n\n后文全部应是正文。\n"
    out = sanitize_typora_math_fences(src)
    assert out.startswith("### 6.3 高阶线性微分方程式")
    assert audit_typora_red_risk(out)["red_risk"] is False
    assert "后文全部应是正文" in out


def test_sanitize_adjacent_inlines_and_stray_display():
    src = "设 $H_{1}$$H_{2}$ 是子群。\n\n$$\n\n![Image](foo.png)\n"
    out = sanitize_typora_math_fences(src)
    assert "$H_{1}$ $H_{2}$" in out
    a = audit_typora_red_risk(out)
    assert a["unpaired_dd"] == 0
    assert a["odd_inline_dollar"] == 0


def test_postprocess_does_not_pass_through_heading_red():
    src = "## 1.1$半群与群\n\n正文。\n"
    out = postprocess_markdown(src, pdf_path=None, fix_bold=False, mode="safe")
    assert audit_typora_red_risk(out)["red_risk"] is False
    assert "1.1$半群" not in out


def test_sanitize_keeps_single_line_display():
    src = "正文\n$$a+b=c$$\n后文\n"
    assert "$$a+b=c$$" in sanitize_typora_math_fences(src)


def test_sanitize_ignores_code_fence_include_and_tex():
    src = "```c\n#include <stdio.h>\n```\n\n```tex\n$$\\frac{1}{2}$$\n```\n"
    out = sanitize_typora_math_fences(src)
    assert "#include <stdio.h>" in out
    assert r"$$\frac{1}{2}$$" in out


def test_sanitize_heading_keeps_paired_math():
    src = "### $6.3 方程 $y'=f(x)$\n后文\n"
    out = sanitize_typora_math_fences(src)
    assert "$y'=f(x)$" in out
    assert not out.startswith("### $6.3")
    assert audit_typora_red_risk(out)["odd_inline_dollar"] == 0


def test_postprocess_does_not_close_display_on_inner_dollars():
    src = "$$\nH_{1}$$H_{2}\n$$\n"
    out = postprocess_markdown(src, pdf_path=None, fix_bold=False, mode="safe")
    assert out.strip().startswith("$$")
    assert out.strip().endswith("$$")
    assert "H_{1}$$H_{2}" in out.replace("\n", "")
