from pathlib import Path

from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import assess_external_processing, update_governance
from tools.research_project.validator import validate_project


def test_handwritten_invalid_gov_fixture_fails_validate():
    project = Path("tests/research_project/fixtures/governance/missing_data_level")
    result = validate_project(project)
    assert result.ok is False


def test_invalid_gov_candidate_rejected_bytes_unchanged(tmp_project, candidate_gov_missing_level):
    before = (tmp_project / "governance.md").read_bytes()
    result = update_governance(tmp_project, candidate_gov_missing_level)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert (tmp_project / "governance.md").read_bytes() == before


def test_restricted_unauthorized_validate_pass_assessment_blocked():
    project = Path("tests/research_project/fixtures/governance/restricted_unauthorized")
    assert validate_project(project).ok is True
    assert assess_external_processing(project).verdict == "BLOCKED"


def test_personal_unauthorized_validate_pass_assessment_blocked(tmp_project):
    assert validate_project(tmp_project).ok is True
    assert assess_external_processing(tmp_project).verdict == "BLOCKED"


def test_public_authorized_verified_allows_preflight(tmp_project, candidate_gov_public_verified):
    result = update_governance(tmp_project, candidate_gov_public_verified)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    assert validate_project(tmp_project).ok is True
    assert assess_external_processing(tmp_project).verdict == "ALLOWED"


def test_public_authorized_local_only_blocked(tmp_project, candidate_gov_public_local_only):
    assert update_governance(tmp_project, candidate_gov_public_local_only).kind == ResearchProjectOperationKind.WRITTEN
    assert assess_external_processing(tmp_project).verdict == "BLOCKED"


def test_update_governance_gov_replace_keeps_aic(tmp_project, candidate_aic, candidate_gov_public_verified):
    assert update_governance(tmp_project, candidate_aic).kind == ResearchProjectOperationKind.WRITTEN
    before_aic_count = (tmp_project / "governance.md").read_text(encoding="utf-8").count("type=AI_CONTRIBUTION")
    assert update_governance(tmp_project, candidate_gov_public_verified).kind == ResearchProjectOperationKind.WRITTEN
    text = (tmp_project / "governance.md").read_text(encoding="utf-8")
    assert text.count("type=AI_CONTRIBUTION") == before_aic_count
    assert "ref=GOV-0001" in text


def test_update_governance_same_gov_is_noop(tmp_project, candidate_gov_identical):
    assert update_governance(tmp_project, candidate_gov_identical).kind == ResearchProjectOperationKind.NO_OP


def test_ai_contribution_same_ref_different_rejected(tmp_project, candidate_aic, candidate_aic_conflict):
    assert update_governance(tmp_project, candidate_aic).kind == ResearchProjectOperationKind.WRITTEN
    before = (tmp_project / "governance.md").read_bytes()
    result = update_governance(tmp_project, candidate_aic_conflict)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert (tmp_project / "governance.md").read_bytes() == before
