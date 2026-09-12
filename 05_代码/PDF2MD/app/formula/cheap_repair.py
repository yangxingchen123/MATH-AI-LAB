# -*- coding: utf-8 -*-
"""确定性公式体修复：先于 validate / OCR，避免把可修 TeX 送去模型。"""
from __future__ import annotations


def cheap_repair_formula_body(body: str, *, display: bool = True) -> str:
    """修单条公式体（不含外围 $ / $$）。不发明缺失符号。"""
    s = (body or "").strip()
    if not s:
        return s
    from app.utils.typora_math_repair import repair_typora_math_body

    s = repair_typora_math_body(s)
    if display:
        from app.utils.md_postprocess import (
            repair_display_delimiters,
            strip_display_ocr_marks,
        )

        s = strip_display_ocr_marks(s)
        s = repair_display_delimiters(s)
    return s.strip()
