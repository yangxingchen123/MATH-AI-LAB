"""Runner dependency, safety, and profile tests. Isolated from GitHub/TeX."""

from __future__ import annotations

from pathlib import Path

from tools.verification.checks import CheckHooks
from tools.verification.models import FailureCategory, VerificationCheckResult, VerificationStatus
from tools.verification.profiles import ALL_CHECK_ORDER, CORE_CHECK_ORDER
from tools.verification.runner import run_verification


def _project(tmp_path: Path) -> Path:
    (tmp_path / "元数据规范.md").write_text("# schema\n", encoding="utf-8")
    (tmp_path / "01_知识库").mkdir(exist_ok=True)
    return tmp_path


def _ok(name: str, layer: str) -> VerificationCheckResult:
    return VerificationCheckResult(
        name=name,
        status=VerificationStatus.PASS,
        summary="ok",
        layer=layer,
    )


def _fail(name: str, layer: str, category: FailureCategory) -> VerificationCheckResult:
    return VerificationCheckResult(
        name=name,
        status=VerificationStatus.FAIL,
        category=category,
        summary="failed",
        layer=layer,
    )


def _source_pass_hooks(*, pytest_status=VerificationStatus.PASS, latex=None) -> CheckHooks:
    def knowledge(root):
        return _ok("Knowledge Validator", "SOURCE INTEGRITY"), object()

    def problem(root, knowledge_result=None):
        return _ok("Problem Validator", "SOURCE INTEGRITY"), object()

    def attempt(root, problem_result=None):
        return _ok("Attempt Validator", "SOURCE INTEGRITY"), object()

    def method(root, knowledge_result=None):
        return _ok("Method Validator", "SOURCE INTEGRITY"), object()

    def indexer(root):
        return _ok("Workspace Indexer", "DERIVED INTEGRITY")

    def wcheck(root):
        return _ok("Workspace Check", "DERIVED INTEGRITY")

    def pytest_fn(root):
        return VerificationCheckResult(
            name="pytest",
            status=pytest_status,
            category=FailureCategory.TEST_FAILURE if pytest_status == VerificationStatus.FAIL else None,
            summary="pytest",
            layer="SOFTWARE INTEGRITY",
        )

    return CheckHooks(
        knowledge=knowledge,
        problem=problem,
        attempt=attempt,
        method=method,
        workspace_indexer=indexer,
        workspace_check=wcheck,
        pytest=pytest_fn,
        latex=latex,
    )


def test_source_pass_runs_workspace(tmp_path: Path) -> None:
    called = {"indexer": 0, "wcheck": 0}
    hooks = _source_pass_hooks()

    def indexer(root):
        called["indexer"] += 1
        return _ok("Workspace Indexer", "DERIVED INTEGRITY")

    def wcheck(root):
        called["wcheck"] += 1
        return _ok("Workspace Check", "DERIVED INTEGRITY")

    hooks.workspace_indexer = indexer
    hooks.workspace_check = wcheck
    run = run_verification("core", root=_project(tmp_path), hooks=hooks)
    assert called == {"indexer": 1, "wcheck": 1}
    assert [c.name for c in run.checks] == list(CORE_CHECK_ORDER)
    assert run.overall_status == VerificationStatus.PASS


def test_source_fail_blocks_workspace_but_runs_pytest(tmp_path: Path) -> None:
    _project(tmp_path)
    derived_called = {"n": 0}

    def knowledge(root):
        return (
            _fail("Knowledge Validator", "SOURCE INTEGRITY", FailureCategory.SOURCE_INVALID),
            object(),
        )

    hooks = _source_pass_hooks()
    hooks.knowledge = knowledge

    def indexer(root):
        derived_called["n"] += 1
        return _ok("Workspace Indexer", "DERIVED INTEGRITY")

    hooks.workspace_indexer = indexer
    pytest_ran = {"n": 0}

    def pytest_fn(root):
        pytest_ran["n"] += 1
        return _ok("pytest", "SOFTWARE INTEGRITY")

    hooks.pytest = pytest_fn
    run = run_verification("core", root=tmp_path, hooks=hooks)
    assert derived_called["n"] == 0
    assert pytest_ran["n"] == 1
    workspace = [c for c in run.checks if c.layer == "DERIVED INTEGRITY"]
    assert all(c.status == VerificationStatus.BLOCKED for c in workspace)
    assert run.overall_status == VerificationStatus.FAIL
    assert [c.name for c in run.checks if c.status == VerificationStatus.FAIL] == ["Knowledge Validator"]


def test_pytest_fail_preserves_source_results(tmp_path: Path) -> None:
    _project(tmp_path)
    hooks = _source_pass_hooks(pytest_status=VerificationStatus.FAIL)
    run = run_verification("core", root=tmp_path, hooks=hooks)
    source = [c for c in run.checks if c.layer == "SOURCE INTEGRITY"]
    assert all(c.status == VerificationStatus.PASS for c in source)
    assert run.overall_status == VerificationStatus.FAIL


def test_multiple_failures_all_reported(tmp_path: Path) -> None:
    _project(tmp_path)
    hooks = _source_pass_hooks(pytest_status=VerificationStatus.FAIL)

    def knowledge(root):
        return (
            _fail("Knowledge Validator", "SOURCE INTEGRITY", FailureCategory.SOURCE_INVALID),
            object(),
        )

    hooks.knowledge = knowledge
    run = run_verification("core", root=tmp_path, hooks=hooks)
    names = [c.name for c in run.checks if c.status in (VerificationStatus.FAIL, VerificationStatus.BLOCKED)]
    assert "Knowledge Validator" in names
    assert "Workspace Indexer" in names
    assert "Workspace Check" in names
    assert "pytest" in names


def test_no_sync_or_rebuild_in_core(tmp_path: Path, monkeypatch) -> None:
    _project(tmp_path)
    calls: list[str] = []

    def boom_sync(*_a, **_k):
        calls.append("sync")
        raise AssertionError("sync must not be called")

    def boom_rebuild(*_a, **_k):
        calls.append("rebuild")
        raise AssertionError("rebuild must not be called")

    monkeypatch.setattr("tools.workspace_indexer.service.sync_index", boom_sync)
    monkeypatch.setattr("tools.workspace_indexer.service.rebuild_index", boom_rebuild)
    monkeypatch.setattr("tools.verification.checks.sync_index", boom_sync, raising=False)
    run = run_verification("core", root=tmp_path, hooks=_source_pass_hooks())
    assert calls == []
    assert run.overall_status == VerificationStatus.PASS


def test_latex_smoke_never_calls_build(tmp_path: Path) -> None:
    _project(tmp_path)
    called = {"build": 0, "check": 0}

    def latex(root, project):
        called["check"] += 1
        assert project == "04_LATEX/demo"
        return _ok("LaTeX Smoke", "ARTIFACT INTEGRITY")

    hooks = CheckHooks(
        latex=latex,
    )
    run = run_verification(
        "latex-smoke",
        root=tmp_path,
        latex_project="04_LATEX/demo",
        hooks=hooks,
    )
    assert called == {"build": 0, "check": 1}
    assert [c.name for c in run.checks] == ["LaTeX Smoke"]
    assert run.overall_status == VerificationStatus.PASS


def test_all_profile_order(tmp_path: Path) -> None:
    _project(tmp_path)
    hooks = _source_pass_hooks(
        latex=lambda root, project: _ok("LaTeX Smoke", "ARTIFACT INTEGRITY"),
    )
    run = run_verification(
        "all",
        root=tmp_path,
        latex_project="04_LATEX/demo",
        hooks=hooks,
    )
    assert [c.name for c in run.checks] == list(ALL_CHECK_ORDER)


def test_suggested_action_not_executed(tmp_path: Path, monkeypatch) -> None:
    _project(tmp_path)
    executed = {"n": 0}

    def fake_sync(*_a, **_k):
        executed["n"] += 1
        raise AssertionError("suggested action must not auto-run")

    monkeypatch.setattr("tools.workspace_indexer.sync_index", fake_sync, raising=False)
    hooks = _source_pass_hooks()

    def indexer(root):
        return VerificationCheckResult(
            name="Workspace Indexer",
            status=VerificationStatus.FAIL,
            category=FailureCategory.GENERATED_STALE,
            summary="Generated files are stale.",
            suggested_action="python -m tools.workspace_indexer sync",
            layer="DERIVED INTEGRITY",
        )

    hooks.workspace_indexer = indexer
    run = run_verification("core", root=tmp_path, hooks=hooks)
    assert executed["n"] == 0
    stale = next(c for c in run.checks if c.name == "Workspace Indexer")
    assert stale.suggested_action == "python -m tools.workspace_indexer sync"
    assert run.overall_status == VerificationStatus.FAIL
