from tools.research_project.operations import add_claim, add_evidence
from tools.research_project.parser import serialize_record, split_preamble_and_records
from tools.research_project.validator import validate_project


def test_validator_detects_duplicate_asm_ref(fixture_duplicate_ref):
    result = validate_project(fixture_duplicate_ref)
    assert result.ok is False
    assert any("ASM-0001" in e and "duplicate" in e.lower() for e in result.errors)


def test_validator_rejects_missing_evd_in_claim_refs(tmp_project):
    result = validate_project(
        __import__("pathlib").Path("tests/research_project/fixtures/claim_evidence_inconsistent")
    )
    assert result.ok is False


def test_validator_rejects_evd_not_listed_on_claim(tmp_project, candidate_clm_no_refs, candidate_evd):
    assert add_claim(tmp_project, candidate_clm_no_refs).kind.value == "WRITTEN"
    evidence = tmp_project / "evidence.md"
    preamble, records = split_preamble_and_records(evidence.read_text(encoding="utf-8"))
    from tools.research_project.parser import parse_records

    evd = parse_records(candidate_evd.read_text(encoding="utf-8"))[0]
    records.append(evd)
    text = preamble
    if not text.endswith("\n"):
        text += "\n"
    for record in records:
        raw = record.raw if record.raw else serialize_record(record)
        text += raw if raw.endswith("\n") else raw + "\n"
    evidence.write_text(text, encoding="utf-8", newline="\n")
    result = validate_project(tmp_project)
    assert result.ok is False


def test_validator_flags_dossier_full_block_copy(tmp_project):
    result = validate_project(
        __import__("pathlib").Path("tests/research_project/fixtures/dossier_full_copy")
    )
    assert result.ok is False


def test_validator_fails_when_project_data_level_missing(fixture_gov_missing_level):
    result = validate_project(fixture_gov_missing_level)
    assert result.ok is False


def test_validator_passes_restricted_unauthorized():
    from pathlib import Path

    project = Path("tests/research_project/fixtures/governance/restricted_unauthorized")
    result = validate_project(project)
    assert result.ok is True
