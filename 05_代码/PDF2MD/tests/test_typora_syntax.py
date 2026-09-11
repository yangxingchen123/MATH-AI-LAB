# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from app.formula.cheap_repair import cheap_repair_formula_body
from app.formula.config import FormulaConfig
from app.formula.pipeline import FormulaPipeline
from app.formula.release_gate import check_release
from app.formula.typora_syntax import (
    assess_typora_syntax,
    count_unpublishable_math,
    is_typora_publishable,
)
from app.formula.validator import validate_latex
from app.repair import RepairConfig, RepairPipeline
from app.utils.md_postprocess import deterministic_typora_pass, postprocess_markdown
from app.utils.typora_math_repair import (
    repair_published_markdown,
    repair_renderer_delimiters,
    repair_typora_inline_math,
    repair_typora_math_body,
)


def test_thetan_is_not_publishable():
    issues = assess_typora_syntax(r"\thetan")
    assert any(i.code == "undefined_tex_command" for i in issues)
    assert not is_typora_publishable(r"\thetan")
    vr = validate_latex(r"\thetan")
    assert not vr.valid
    assert "undefined_tex_command" in vr.issues


def test_amp_in_left_paren_rejected_until_repaired():
    raw = r"\left( a & b \\ c & d \right)"
    assert any(i.code == "amp_outside_alignment" for i in assess_typora_syntax(raw))
    assert not validate_latex(raw).valid
    fixed = cheap_repair_formula_body(raw, display=True)
    assert r"pmatrix" in fixed
    assert validate_latex(fixed).valid


def test_texpatch_left_brace_and_align():
    assert r"\left\{" in repair_renderer_delimiters(r"\left{ x }")
    assert r"\begin{aligned}" in repair_renderer_delimiters(r"\begin{align} a &= b \end{align}")
    assert r"\end{aligned}" in repair_typora_math_body(r"\begin{align*} x&=1 \end{align*}")
    assert r"\begin{aligned}" in repair_renderer_delimiters(r"\begin{aligned} a &= b \end{aligned}")


def test_left_paren_close_does_not_eat_inner():
    assert repair_renderer_delimiters(r"\left( f(x), g(y) )") == r"\left( f(x), g(y) \right)"
    assert repair_renderer_delimiters(r"\left( f(x).") == r"\left( f(x)."
    assert repair_renderer_delimiters(r"\left( a+b )") == r"\left( a+b \right)"
    assert repair_renderer_delimiters(r"\left( a+b).") == r"\left( a+b\right)."


def test_warmup_katex_uses_backslash_seed():
    from app.formula.katex_engine import _WARMUP_TEX, katex_gate_available, katex_validate, reset_katex_engine

    assert "\\" in _WARMUP_TEX
    if not katex_gate_available():
        return
    reset_katex_engine()
    ok, _err = katex_validate("x")
    assert ok is True
    from app.formula import katex_engine as ke

    assert ke._PROC is None
    ok, _err = katex_validate(_WARMUP_TEX)
    assert ok is True
    assert ke._PROC is not None
    reset_katex_engine()


def test_mathbb_standalone_not_k0():
    assert r"\mathbb{N}" in repair_typora_math_body(r"n\in\N")
    assert r"\mathbb{K}0" not in repair_typora_math_body(r"K\K0")
    assert r"K_{0}" in repair_typora_math_body(r"K\K0")


def test_katex_gate_catches_what_heuristics_miss():
    from app.formula.katex_engine import (
        katex_gate_available,
        katex_validate,
        katex_validate_many,
    )

    if not katex_gate_available():
        return
    ok, _err = katex_validate(r"E=mc^2")
    assert ok is True
    ok, err = katex_validate(r"\left( a & b \right)")
    assert ok is False
    assert err
    rows = katex_validate_many([r"\theta_{n}", r"\thetan", r"E=mc^2"])
    assert rows[0][0] is True
    assert rows[1][0] is False
    assert rows[2][0] is True


def test_hline_and_check_are_known():
    assert is_typora_publishable(r"\begin{array}{c|c} a & b \\ \hline c & d \end{array}")
    assert is_typora_publishable(r"\check{x} + \mathring{u}")


def test_aligned_amp_is_legal():
    body = r"\begin{aligned} a &= b \\ c &= d \end{aligned}"
    assert is_typora_publishable(body)
    assert validate_latex(body).valid


def test_cjk_in_math_is_lint_only():
    issues = assess_typora_syntax(r"x = 当 n>0")
    assert any(i.code == "cjk_in_math" for i in issues)
    assert is_typora_publishable(r"x = 当 n>0")
    assert validate_latex(r"x = 当 n>0").valid
    assert validate_latex(r"x=\text{当} n>0").valid


def test_cheap_repair_thetan_then_valid():
    assert cheap_repair_formula_body(r"\thetan", display=False) == r"\theta_{n}"
    assert validate_latex(r"\theta_{n}").valid


def test_pipeline_cheap_repairs_without_ocr():
    md = "$$\n\\thetan\n$$"
    res = FormulaPipeline(FormulaConfig(recovery_enabled=False)).process_markdown(md)
    assert r"\thetan" not in res.markdown
    assert r"\theta_{n}" in res.markdown
    assert res.report.corrupted_formula_count == 0


def test_pipeline_cheap_repairs_inline_without_ocr():
    md = r"本原单位根 $\thetan$ 属于圆扩张"
    res = FormulaPipeline(FormulaConfig(recovery_enabled=False)).process_markdown(md)
    assert r"\thetan" not in res.markdown
    assert r"\theta_{n}" in res.markdown
    assert res.report.corrupted_formula_count == 0


def test_pipeline_converts_left_amp_to_pmatrix():
    md = r"$$\left( a & b \\ c & d \right)$$"
    res = FormulaPipeline(FormulaConfig(recovery_enabled=False)).process_markdown(md)
    assert r"pmatrix" in res.markdown
    assert res.report.corrupted_formula_count == 0


def test_prose_swallowed_by_dollar_not_counted():
    md = (
        "$未闭合开头 此表称为G的群表.群表的表示方法显然也适用于有限半群。"
        "更一般地如果一个有限集合上定义了二元运算我们就列表。"
        "下面我们给出群的若干简单而且重要的性质 结尾$"
    )
    assert count_unpublishable_math(md) == 0


def test_release_gate_counts_leftover_thetan():
    dq = check_release("$$\n\\thetan\n$$", None, FormulaConfig())
    assert not dq.publishable
    assert "typora_syntax" in dq.reasons
    assert dq.formula_failures >= 1
    assert count_unpublishable_math("$$\n\\theta_{n}\n$$") == 0


def test_wrap_plain_subscripts_galois():
    raw = "于是 K0 = F0，且 Fi+1 = Fi，多项式 xn-ai 的根。令K0是可分闭包。"
    out = repair_typora_inline_math(raw)
    assert "$K_{0}$" in out
    assert "$F_{0}$" in out
    assert "$F_{i+1}$" in out
    assert "$F_{i}$" in out
    assert "$x_{n}-a_{i}$" in out or ("$x_{n}$" in out and "$a_{i}$" in out)
    assert "令$K_{0}$是" in out


def test_wrap_does_not_break_image_hash():
    raw = (
        r"![Image](images/image_000001_e598c931dfc775578a5823a2f53df42084bbccf4dc52fe4d99b5880f116e2e79.png)"
    )
    out = repair_typora_inline_math(raw)
    assert "116e2e79.png" in out
    assert "$e_{2}$" not in out


def test_restore_wrapped_image_url():
    from app.utils.typora_math_repair import restore_wrapped_markdown_urls

    raw = (
        "![Image](dir/foo (bar)/images/foo116$e_{2}$$\n"
        "e_{79}$.png)"
    )
    out = restore_wrapped_markdown_urls(raw)
    assert "116e2e79.png" in out
    assert "foo (bar)" in out


def test_restore_dollar_in_image_dirname():
    from app.utils.typora_math_repair import restore_wrapped_markdown_urls

    raw = (
        r"![Image](../../../../1 (1)\github-submit\output\$抽象代数 (邓少强，朱富海$)"
        r" (z-library.sk)\images\image_000000_abc.png)"
    )
    out = restore_wrapped_markdown_urls(raw)
    assert r"output\抽象代数 (邓少强，朱富海)" in out
    assert "$" not in out[out.index("](") : out.index(".png")]


def test_accidental_fences_do_not_swallow_document():
    from app.utils.typora_math_repair import repair_accidental_math_fences

    raw = (
        "## 1.1$半群与群\n"
        "$##$ 习题$2.8\n"
        "$$\n"
        "![Image](images/foo.png)\n"
        "后文不应再被当成公式 $K_{4}$ 正常。\n"
        r"$i_{1}$$i_{2}$"
    )
    out = repair_accidental_math_fences(raw)
    assert "## 1.1 半群与群" in out
    assert "## 习题2.8" in out
    assert not out.startswith("##$")
    assert "$$\n![" not in out.replace("\r\n", "\n")
    assert r"$i_{1}$ $i_{2}$" in out or r"$i_{1}$ $i_{2}$" in out.replace("  ", " ")


def test_wrap_skips_english_an_introduction():
    raw = "See An Introduction to Galois Theory. 交错群 An 是 Sn 的正规子群。"
    out = repair_typora_inline_math(raw)
    assert "An Introduction" in out
    assert "$A_{n}$" in out
    assert "$S_{n}$" in out


def test_wrap_skips_in_on_eq():
    raw = "In the field On Eq. (4) we set K0."
    out = repair_typora_inline_math(raw)
    assert "$I_{n}$" not in out
    assert "$O_{n}$" not in out
    assert "$E_{q}$" not in out
    assert "$K_{0}$" in out


def test_postprocess_keeps_pmatrix_amps():
    raw = r"$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$$"
    out = postprocess_markdown(raw, pdf_path=None, fix_bold=False, mode="safe")
    compact = out.replace(" ", "")
    assert r"a&b" in compact
    assert r"c&d" in compact


def test_repair_runs_deterministic_pass_before_formula_pipeline(tmp_path: Path):
    raw = tmp_path / "doc.raw.md"
    raw.write_text("$$\\thetan$$\n", encoding="utf-8")
    seen: dict[str, str] = {}

    class _FakeReport:
        document_quality = None
        corrupted_formula_count = 0
        recovery_attempted_count = 0
        recovery_success_count = 0
        recovery_failed_count = 0
        suspected_unwrapped = 0
        writeback = {}

        def to_dict(self):
            return {"formula_count": 1, "validated": 1}

    class _FakeResult:
        markdown = "$$\\theta_{n}$$"
        report = _FakeReport()

    def _capture(md, **_kw):
        seen["md"] = md
        return _FakeResult()

    with patch("app.formula.FormulaPipeline") as fp_cls:
        fp_cls.return_value.process_markdown.side_effect = _capture
        RepairPipeline(RepairConfig(keep_formulas=True, write_final_md=True)).run(
            pdf_path=tmp_path / "doc.pdf",
            raw_markdown_path=raw,
            out_dir=tmp_path,
        )

    assert r"\thetan" not in seen["md"]
    assert r"\theta_{n}" in seen["md"]


def test_deterministic_pass_does_not_blank_display():
    raw = r"$$\left( a & b \\ c & d \right)$$"
    out = deterministic_typora_pass(raw)
    assert "formula-not-decoded" not in out
    assert r"pmatrix" in out


def test_unwrap_prose_display_keeps_real_tex():
    from app.utils.typora_math_repair import unwrap_prose_displays

    keep = r"$$设$$\frac{a}{b}=1$$当 n>0$$"
    # 上面这条会被非贪婪 $$ 拆开；用独立块
    keep = "正文\n$$\n" + r"x=\frac{a}{b}" + "\n$$\n"
    assert r"\frac" in unwrap_prose_displays(keep)
    prose = "$$\n思考题1.2.24Lagrange定理说明任何子群的阶一定是群本身的阶的因子，那么对群的阶的任何因子m，是否都存在子群使得其阶恰为m?\n$$"
    out = unwrap_prose_displays(prose)
    assert "$$" not in out
    assert "Lagrange" in out


def test_published_repair_unwraps_heading_and_keeps_image():
    raw = (
        "$$思考题1.2\n\n"
        "## 习题1.2\n\n"
        r"![Image](dir/foo (bar)/images/image_000001_e598c931dfc775578a5823a2f53df42084bbccf4dc52fe4d99b5880f116e2e79.png)"
        "\n$$"
        "\n设K为F的代数扩张,令K0是可分闭包。"
    )
    out = repair_published_markdown(raw)
    assert "## 习题1.2" in out
    assert "116e2e79.png" in out
    assert "$e_{2}$" not in out
    assert "令$K_{0}$是" in out
    assert out.count("$$") % 2 == 0
