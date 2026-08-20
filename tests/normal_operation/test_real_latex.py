"""Disposable real XeLaTeX acceptance (no mock of latex_build)."""

from __future__ import annotations

import shutil
from pathlib import Path

from tests.normal_operation.test_closure import _multipart_body, _write_p0002
from tools.normal_operation.naming import artifact_stem
from tools.normal_operation.reconcile import reconcile_problem
from tools.problem_solution.slots import wrap_slot_content
from tests.problem_validator.conftest import problem_md


def test_disposable_real_xelatex_pdf(tmp_path: Path) -> None:
    # Whole-problem (no parts) to keep generated TeX small.
    from tests.normal_operation.test_closure import _kb

    _kb(tmp_path)
    (tmp_path / "11_学习证据" / "尝试记录").mkdir(parents=True)
    dest = tmp_path / "02_题目库" / "研究中"
    dest.mkdir(parents=True)
    body = (
        "# Mini\n\n## 题目\n\nProve $1+1=2$.\n\n## 解答\n\n"
        + wrap_slot_content("P0099", "We have $1+1=2$ by Peano arithmetic.")
        + "\n"
    )
    (dest / "P0099.md").write_text(
        problem_md(pid="P0099", title="Mini Addition", body=body),
        encoding="utf-8",
    )

    real_tpl = Path(r"C:\MATH-AI-LAB\04_LATEX\模板\数学讲义模板_v1")
    real_cls = real_tpl / "vendor" / "ElegantBook-v4.7" / "elegantbook.cls"
    tpl = tmp_path / "04_LATEX" / "模板" / "数学讲义模板_v1"
    vendor = tpl / "vendor" / "ElegantBook-v4.7"
    vendor.mkdir(parents=True)
    shutil.copy2(real_tpl / "main.tex", tpl / "main.tex")
    shutil.copy2(real_cls, vendor / "elegantbook.cls")

    recon = reconcile_problem(
        tmp_path,
        problem_id="P0099",
        artifact_domain="未分类",
        include_verification=False,
    )
    assert recon.completion.complete
    assert recon.workflow_after == "已解决"
    assert recon.artifact is not None
    tex = recon.artifact.paths.entry_tex
    pdf = recon.artifact.paths.formal_pdf
    assert tex.is_file()
    assert not (tex.parent / "elegantbook.cls").exists()
    assert pdf.is_file()
    assert pdf.stat().st_size > 0
    assert pdf.read_bytes()[:5] == b"%PDF-"
    assert recon.artifact.pdf.value == "CURRENT"

    second = reconcile_problem(tmp_path, problem_id="P0099", artifact_domain="未分类")
    assert second.counters.builds == 0
    assert second.counters.latex_writes == 0
    assert second.counters.pdf_replaces == 0
    assert second.counters.workflow_moves == 0
