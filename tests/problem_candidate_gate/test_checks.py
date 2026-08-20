from pathlib import Path

from tools.problem_candidate_gate.readiness import check_file, check_project

from .conftest import knowledge_md, problem_md


def _write_k(project: Path, kid: str = "K0001", status: str = "reviewed") -> None:
    (project / "01_知识库" / f"{kid}.md").write_text(
        knowledge_md(kid=kid, status=status), encoding="utf-8"
    )


def test_valid_draft(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = check_project(root=project)
    assert r.summary.result == "PASS"


def test_valid_reviewed(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(status="reviewed", extras="knowledge: []"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert r.summary.result == "PASS"


def test_invalid_schema_version(project: Path) -> None:
    text = problem_md().replace("schema_version: 1", "schema_version: 2")
    (project / "02_题目库" / "a.md").write_text(text, encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-BASE-002" for i in r.issues)


def test_invalid_p_id(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(pid="P001"), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-BASE-010" for i in r.issues)


def test_real_p0000(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(pid="P0000"), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-BASE-011" for i in r.issues)
    assert r.summary.result == "FAIL"


def test_duplicate_p_id(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(pid="P0001"), encoding="utf-8")
    (project / "02_题目库" / "b.md").write_text(problem_md(pid="P0001"), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-ID-001" for i in r.issues)
    r2 = check_file(project / "02_题目库" / "a.md", root=project)
    assert any(i.rule_id == "PCG-ID-001" for i in r2.issues)


def test_wrong_type(project: Path) -> None:
    text = problem_md().replace("type: problem", "type: knowledge")
    text = text.replace("id: P0001", "id: P0001")
    # type knowledge with P id still candidate via id
    (project / "02_题目库" / "a.md").write_text(text, encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-BASE-021" for i in r.issues)


def test_empty_title(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(title="   "), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-BASE-030" for i in r.issues)


def test_invalid_status(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(status="solved"), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-STATE-001" for i in r.issues)


def test_invalid_date(project: Path) -> None:
    text = problem_md().replace("created: 2026-08-19", "created: 19/08/2026")
    (project / "02_题目库" / "a.md").write_text(text, encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-DATE-001" for i in r.issues)


def test_updated_before_created(project: Path) -> None:
    text = problem_md().replace("updated: 2026-08-19", "updated: 2026-08-18")
    (project / "02_题目库" / "a.md").write_text(text, encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-DATE-003" for i in r.issues)


def test_draft_knowledge_omitted_pass(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = check_project(root=project)
    assert not any(i.rule_id.startswith("PCG-KNOW-") and i.severity.value == "ERROR" for i in r.issues)


def test_draft_valid_knowledge_pass(project: Path) -> None:
    _write_k(project)
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert r.summary.result == "PASS"


def test_reviewed_missing_knowledge_error(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(status="reviewed"), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-002" for i in r.issues)


def test_reviewed_knowledge_empty_pass(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(status="reviewed", extras="knowledge: []"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert r.summary.result == "PASS"


def test_invalid_k_id(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="knowledge:\n  - K1"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-003" for i in r.issues)


def test_k0000_target(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="knowledge:\n  - K0000"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-004" for i in r.issues)


def test_duplicate_k(project: Path) -> None:
    _write_k(project)
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="knowledge:\n  - K0001\n  - K0001"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-005" for i in r.issues)


def test_missing_target(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="knowledge:\n  - K0099"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-006" for i in r.issues)


def test_reviewed_problem_draft_knowledge_error(project: Path) -> None:
    _write_k(project, status="draft")
    (project / "02_题目库" / "a.md").write_text(
        problem_md(status="reviewed", extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-008" for i in r.issues)


def test_reviewed_problem_reviewed_knowledge_pass(project: Path) -> None:
    _write_k(project, status="reviewed")
    (project / "02_题目库" / "a.md").write_text(
        problem_md(status="reviewed", extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert r.summary.result == "PASS"


def test_no_parts_pass(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = check_project(root=project)
    assert not any(i.rule_id.startswith("PCG-PART-") for i in r.issues)


def test_parts_abc_pass(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="parts:\n  - a\n  - b\n  - c"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert r.summary.result == "PASS"


def test_parts_non_list(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="parts: a"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-PART-001" for i in r.issues)


def test_parts_empty_string(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="parts:\n  - a\n  - '  '"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-PART-002" for i in r.issues)


def test_parts_duplicate(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="parts:\n  - a\n  - a"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-PART-003" for i in r.issues)


def test_single_part_candidate_violation(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="parts:\n  - a"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-PART-004" for i in r.issues)


def test_complex_token_warning(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(extras="parts:\n  - 'part a with spaces'\n  - b"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert r.summary.result == "PASS"
    assert any(i.rule_id == "PCG-PART-W001" for i in r.issues)


def test_legacy_filename_warning(project: Path) -> None:
    path = project / "02_题目库" / "已解决" / "P001_x.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(problem_md(pid="P0001", extras="knowledge: []", status="reviewed"), encoding="utf-8")
    r = check_project(root=project)
    assert r.summary.result == "PASS"
    assert any(i.rule_id == "PCG-LEGACY-W001" for i in r.issues)


def test_content_review_marker_warning(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(body="> Candidate Content Review: PENDING\n"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-READY-W001" for i in r.issues)


def test_no_marker_no_content_warning(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(body="需要审核标量域，但没有精确 marker。\n"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert not any(i.rule_id == "PCG-READY-W001" for i in r.issues)


def test_knowledge_dependency_failure(project: Path) -> None:
    (project / "01_知识库" / "bad.md").write_text(
        "---\nschema_version: 1\nid: K0001\ntype: knowledge\n---\n",
        encoding="utf-8",
    )
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-KNOW-E010" for i in r.issues)
    assert r.readiness == "NOT_READY"
