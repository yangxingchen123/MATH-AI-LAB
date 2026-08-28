from pathlib import Path

from tools.research_project.constants import (
    CONTRACT_VERSION,
    DOSSIER_BEGIN,
    DOSSIER_END,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    TEMPLATE_ROOT,
)
from tools.research_project.contract import load_contract


def test_contract_lists_six_canonical_files_and_four_dirs():
    c = load_contract()
    assert c.contract_version == "1.1"
    assert set(c.required_files) == {
        "research_dossier.md",
        "assumptions.md",
        "evidence.md",
        "decisions.md",
        "negative_results.md",
        "governance.md",
    }
    assert set(c.required_dirs) == {"documents", "runs", "artifacts", "reviews"}
    assert c.contract_version == CONTRACT_VERSION
    assert set(REQUIRED_FILES) == set(c.required_files)
    assert set(REQUIRED_DIRS) == set(c.required_dirs)


def test_template_files_exist_and_contain_dossier_markers():
    text = (TEMPLATE_ROOT / "research_dossier.md").read_text(encoding="utf-8")
    assert DOSSIER_BEGIN in text and DOSSIER_END in text


def test_template_governance_defaults_and_lf():
    raw = (TEMPLATE_ROOT / "governance.md").read_bytes()
    assert b"type=GOVERNANCE ref=GOV-0001 BEGIN" in raw
    assert b"license_status: LOCAL_ONLY" in raw or b"- license_status: LOCAL_ONLY" in raw
    assert b"\r\n" not in raw


def test_seven_legal_type_fixtures_exist_and_contain_separator():
    root = Path("tests/research_project/fixtures/grammar")
    for name in [
        "legal_assumption.md",
        "legal_claim.md",
        "legal_evidence.md",
        "legal_decision.md",
        "legal_negative_result.md",
        "legal_governance.md",
        "legal_ai_contribution.md",
    ]:
        text = (root / name).read_text(encoding="utf-8")
        assert "\n---\n" in text
        assert "BEGIN -->" in text and "END -->" in text
