# -*- coding: utf-8 -*-
"""行内公式：中文误包进 $、$ 切断括号、\\timesB 粘连。"""
from __future__ import annotations

import re

from app.utils.md_postprocess import (
    paren_matrix_to_pmatrix,
    repair_display_formula_scraps,
    repair_display_math_light,
)
from app.utils.typora_math_repair import (
    repair_typora_inline_math,
    repair_typora_math_in_markdown,
    split_glued_math_commands,
)


def test_times_glued_to_letter():
    assert split_glued_math_commands(r"A\timesB") == r"A\times B"
    assert split_glued_math_commands(r"m \inN") == r"m \in N"
    assert split_glued_math_commands(r"\partialP") == r"\partial P"
    assert split_glued_math_commands(r"\partialQ") == r"\partial Q"
    assert split_glued_math_commands(r"\partialy") == r"\partial y"
    assert split_glued_math_commands(r"\partiallambda") == r"\partial \lambda"
    assert split_glued_math_commands(r"G\approxG") == r"G\approx G"
    assert split_glued_math_commands(r"W\oplusU") == r"W\oplus U"
    assert split_glued_math_commands(r"\sqrtI") == r"\sqrt{I}"
    assert split_glued_math_commands(r"\sqrtkg") == r"\sqrt{kg}"


def test_greek_glued_becomes_subscript():
    assert split_glued_math_commands(r"\thetan") == r"\theta_{n}"
    assert split_glued_math_commands(r"\alphai") == r"\alpha_{i}"
    assert split_glued_math_commands(r"\alphan") == r"\alpha_{n}"
    assert split_glued_math_commands(r"\betai") == r"\beta_{i}"


def test_prose_thetan_gets_math_wrap():
    raw = r"E/F 是n次分圆扩张, \thetan 是本原单位根, Kummer 扩张."
    out = repair_typora_inline_math(raw)
    assert r"\thetan" not in out
    assert r"$\theta_{n}$" in out


def test_dollar_theta_then_n_merges_subscript():
    raw = r"其中任何n阶元$\theta$n称为n次本原单位根."
    out = repair_typora_inline_math(raw)
    assert r"$\theta$n" not in out
    assert r"$\theta_{n}$" in out


def test_sqrt_inside_false_markdown_link_is_still_split():
    raw = r"2. f = exp$[2(\sqrty - 1)](\sqrtx-\sqrty+1)2(\sqrt{z} - \sqrt{y} + 1)2."
    out = repair_typora_math_in_markdown(raw)
    assert r"\sqrty" not in out
    assert r"\sqrtx" not in out
    assert r"\sqrt{y}" in out
    assert r"\sqrt{x}" in out


def test_dollar_letter_then_digit_merges_subscript():
    raw = r"记$a$1为第一个根."
    out = repair_typora_inline_math(raw)
    assert r"$a$1" not in out
    assert r"$a_{1}$" in out


def test_dollar_times_then_n_gets_space():
    raw = r"直积$A\times$n次"
    out = repair_typora_inline_math(raw)
    assert r"$\times$n" not in out
    assert r"$A\times n$" in out or r"$A\times n$" in out.replace(" ", "")


def test_does_not_split_inf_or_infty():
    assert split_glued_math_commands(r"\inf S") == r"\inf S"
    assert split_glued_math_commands(r"\infty") == r"\infty"


def test_cjk_taken_out_of_inline_math():
    raw = r"设A,B为两个非空集合,$用A\timesB表示A 与B的直积集合$,它是由"
    out = repair_typora_inline_math(raw)
    assert r"\timesB" not in out
    assert r"$A\times B$" in out
    assert "表示" in out
    assert "$用" not in out
    assert r"$B$" in out or r"$B$" in out.replace(" ", "")


def test_in_n_and_split_paren_dollar():
    raw = r"并求A $\in SL(2$,Zn)的逆.试对任意 $m \inN定义 SL(m$, Zn)."
    out = repair_typora_inline_math(raw)
    assert r"\inN" not in out
    assert r"$\in SL(2, Zn)$" in out or r"$A \in SL(2, Zn)$" in out
    assert r"$SL(m, Zn)$" in out or r"$SL(m,  Zn)$" in out
    assert "定义" in out
    assert r"$m \in N$" in out or r"$m \in N$" in out.replace("  ", " ")


def test_does_not_eat_trailing_equals_one():
    raw = (
        r"$$a ^ { \varphi ( n )} \equiv 1 \, ( \bmod n ) , "
        r"\ \ a \in \mathbb{N} , \ \ ( a , n ) = 1 .$$"
    )
    out = repair_display_math_light(raw)
    compact = out.replace(" ", "")
    assert r"(a,n)=1" in compact


def test_sl2_pmatrix_and_ocr_stripped():
    raw = (
        r"$$"
        r"\begin{aligned}1 3 . \, \ddot{\vartheta} \, SL ( 2 , \mathbb{Z} _ { n} ) "
        r"= \left \{ \, A = \left ( \bar{a} & \bar{b} \\ \bar{c} & \bar{d} \right ) "
        r"\Big | \bar{a} , \bar{b} , \bar{c} , \bar{d} \in \mathbb{Z} _ { n} , "
        r"\bar{a} \cdot \bar{d} - \bar{b} \cdot \bar{c} = \bar{1} \right \} . "
        r"\, \ddot{\vartheta} \, \mathbb{H} \, SL ( 2 , \mathbb{Z} _ { n} )"
        r"\end{aligned}"
        r"$$"
    )
    out = repair_display_math_light(raw)
    assert r"\left (" not in out.replace(" ", "") or r"\begin{pmatrix}" in out
    assert r"\begin{pmatrix}" in out
    assert r"\ddot{\vartheta}" not in out
    assert "1 3 ." not in out
    assert r"\mathbb{H}" not in out
    assert r"\bar{a}" in out


def test_full_postprocess_keeps_times_in_math():
    raw = r"用$A\timesB表示A 与B$的直积"
    out = repair_typora_math_in_markdown(raw)
    assert r"\timesB" not in out
    assert r"$A\times B$" in out


def test_set_builder_right_bar_and_ocr():
    raw = (
        r"$$"
        r"\dot{\vec{\alpha}} V = \left \{ \begin{pmatrix}\alpha & \beta \\ "
        r"- \bar{\beta} & \bar{\alpha}\end{pmatrix} \right | \alpha , \beta "
        r"\in \mathbb{C} \right \} . \ \mathbb{X} \neq \mathbb{A} \mathbb{A} , "
        r"B \in V , \mathbb{Z} \neq \mathbb{A} \mathbb{A} \mathbb{U} "
        r"\left ( A , B \right ) = \frac{1} { 2} \text{tr} \left ( A \bar{B} ^ { \prime} \right )"
        r"$$"
    )
    out = repair_display_math_light(raw)
    assert r"\right |" not in out and r"\right|" not in out.replace(" ", " ")
    assert r"\mid" in out
    assert r"\begin{pmatrix}" in out
    assert r"\mathbb{X}" not in out
    assert r"\dot{\vec{\alpha}}" not in out
    assert r"\text{tr}" in out or r"\mathrm{tr}" in out or "tr" in out


def test_vmatrix_from_left_bar():
    raw = (
        r"$$\begin{aligned}\frac{D [ y , y ^ { \prime} ]} { D [ C_{1} , C_{2} ]} "
        r"= \left | e ^ { x} \cos x & e ^ { x} \sin x \\ "
        r"e ^ { x} ( \cos x - \sin x ) & e ^ { x} ( \sin x + \cos x ) \right | "
        r"= e ^ { 2 x} \neq 0 .\end{aligned}$$"
    )
    out = repair_display_math_light(raw)
    assert r"\begin{vmatrix}" in out
    assert r"\end{vmatrix}" in out
    compact = out.replace(" ", "")
    assert r"\begin{aligned}" not in compact


def test_space_matrix_unary_minus():
    raw = r"$$i = \left ( \sqrt{- 1} 0 \\ 0 - \sqrt{- 1} \right )$$"
    out = repair_display_math_light(raw)
    compact = re.sub(r"\s+", "", out)
    assert r"\begin{pmatrix}" in out
    assert r"0&-" in compact or r"0&-\sqrt" in compact
    assert r"&-&" not in compact
    raw = r"$$1 = \left ( 1 0 \\ 0 1 \right )$$"
    out = repair_display_math_light(raw)
    assert r"\begin{pmatrix}" in out
    assert "&" in out


def test_keeps_true_aligned_equals():
    raw = (
        r"$$\begin{aligned}&(2x\sin y\,dx)\\&=d(x^2\sin y).\end{aligned}$$"
    )
    out = repair_display_math_light(raw)
    assert r"\begin{aligned}" in out


def test_array_missing_end_in_left():
    raw = (
        r"$$\frac{d} { d x} \left ( y_{1} \\ y_{2} \right ) = "
        r"\left ( \begin{array} { c c} \cos ^ { 2} x & a \\ b & "
        r"\sin ^ { 2} x \right ) \left ( \begin{array} { c} y_{1} \\ y_{2} \right )$$"
    )
    out = repair_display_math_light(raw)
    assert r"\begin{pmatrix}" in out
    assert r"\begin{array}" not in out or out.count(r"\begin{pmatrix}") >= 2
    raw = r"A = \left ( \alpha & \beta \\ -\bar{\beta} & \bar{\alpha} \right )"
    out = paren_matrix_to_pmatrix(raw)
    assert r"\begin{pmatrix}" in out
    assert r"\end{pmatrix}" in out


def test_display_scraps_still_drops_red_al():
    raw = (
        r"$$\begin{array} { l l } \text {red} & \log i ( P _ { s j c } ) = "
        r"\beta _ { 0 } + \beta _ { 1 } T M A 1 _ { s } "
        r"\\ \text {al} & + \sum _ { k = 4 } ^ { 9 } \beta _ { k } X _ { k s } "
        r"+ \gamma _ { 0 j c } + \zeta _ { 0 c } & ( 1 ) \\ \end{array}$$"
    )
    out = repair_display_formula_scraps(raw)
    assert r"\operatorname{logit}" in out
    assert "TMA1" in out
