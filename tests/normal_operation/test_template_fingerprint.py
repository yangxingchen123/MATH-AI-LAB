"""Template fingerprint includes main.tex + vendor cls, not docs."""

from __future__ import annotations

from pathlib import Path

from tests.latex_build.conftest import install_pinned_vendor
from tests.normal_operation.test_closure import _multipart_body, _write_p0002
from tools.normal_operation.artifact import (
    TEMPLATE_DEPENDENCY_MISSING,
    FreshnessState,
    inspect_artifact,
    materialize_problem_latex,
    template_sha_for_project,
)
from tools.normal_operation.freshness import template_fingerprint


def test_fingerprint_includes_main_and_cls(tmp_path: Path) -> None:
    install_pinned_vendor(tmp_path, main_text="A\n", cls_text="CLS-B")
    fp = template_sha_for_project(tmp_path)
    assert fp == template_fingerprint(main_tex="A\n", cls_bytes=b"CLS-B")
    install_pinned_vendor(tmp_path, main_text="A2\n", cls_text="CLS-B")
    assert template_sha_for_project(tmp_path) != fp
    install_pinned_vendor(tmp_path, main_text="A\n", cls_text="CLS-B2")
    assert template_sha_for_project(tmp_path) != fp


def test_docs_do_not_change_fingerprint(tmp_path: Path) -> None:
    vendor = install_pinned_vendor(tmp_path, main_text="A\n", cls_text="CLS-B")
    before = template_sha_for_project(tmp_path)
    (vendor / "README.md").write_text("changed", encoding="utf-8")
    (vendor / "UPSTREAM.md").write_text("changed", encoding="utf-8")
    (vendor / "License").write_text("changed", encoding="utf-8")
    (vendor / "examples").mkdir(exist_ok=True)
    (vendor / "examples" / "elegantbook-cn.tex").write_text("% ex", encoding="utf-8")
    assert template_sha_for_project(tmp_path) == before


def test_cls_change_marks_artifact_stale(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path, main_text="A\n", cls_text="CLS-B")
    mat = materialize_problem_latex(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert mat.written
    assert mat.paths is not None
    assert not (mat.paths.project_dir / "elegantbook.cls").exists()
    insp = inspect_artifact(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert insp.latex == FreshnessState.CURRENT
    install_pinned_vendor(tmp_path, main_text="A\n", cls_text="CLS-B2")
    insp2 = inspect_artifact(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert insp2.latex == FreshnessState.STALE


def test_main_tex_change_marks_artifact_stale(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path, main_text="A\n", cls_text="CLS-B")
    materialize_problem_latex(tmp_path, problem_id="P0002", artifact_domain="未分类")
    install_pinned_vendor(tmp_path, main_text="A2\n", cls_text="CLS-B")
    insp = inspect_artifact(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert insp.latex == FreshnessState.STALE


def test_vendor_missing_inspect_fails(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    insp = inspect_artifact(tmp_path, problem_id="P0002")
    assert insp.latex == FreshnessState.FAILED
    assert insp.error == TEMPLATE_DEPENDENCY_MISSING


def test_materializer_does_not_copy_vendor(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    vendor = install_pinned_vendor(tmp_path)
    mat = materialize_problem_latex(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert mat.error is None
    assert mat.paths is not None
    assert not (mat.paths.project_dir / "elegantbook.cls").exists()
    assert not (mat.paths.project_dir / "vendor").exists()
    assert vendor.is_dir()
