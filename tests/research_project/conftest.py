"""Shared fixtures for research project tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import init_project, reconcile_project

CANDIDATE_ROOT = Path("tests/research_project/fixtures/candidates")
GRAMMAR_ROOT = Path("tests/research_project/fixtures/grammar")
DAMAGE_FILES = (
    "orphan_end.md",
    "nested_begin.md",
    "duplicate_begin.md",
    "missing_end.md",
    "begin_end_mismatch.md",
)


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "07_项目").mkdir(parents=True)
    return repo


@pytest.fixture
def tmp_project(tmp_repo: Path) -> Path:
    project = tmp_repo / "07_项目" / "Demo"
    result = init_project(project, "Demo", repo_root=tmp_repo)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    reconcile_project(project)
    return project


@pytest.fixture
def fixture_duplicate_ref() -> Path:
    return Path("tests/research_project/fixtures/duplicate_ref")


@pytest.fixture
def fixture_gov_missing_level() -> Path:
    return Path("tests/research_project/fixtures/governance/missing_data_level")


@pytest.fixture(params=DAMAGE_FILES)
def parse_should_fail_fixture(request: pytest.FixtureRequest) -> str:
    path = GRAMMAR_ROOT / request.param
    return path.read_text(encoding="utf-8")


@pytest.fixture
def candidate_asm() -> Path:
    return CANDIDATE_ROOT / "asm_0001.md"


@pytest.fixture
def candidate_asm_conflict() -> Path:
    return CANDIDATE_ROOT / "asm_0001_conflict.md"


@pytest.fixture
def candidate_replacement() -> Path:
    return CANDIDATE_ROOT / "asm_0002.md"


@pytest.fixture
def candidate_clm_no_refs() -> Path:
    return CANDIDATE_ROOT / "clm_0001_no_refs.md"


@pytest.fixture
def candidate_evd() -> Path:
    return CANDIDATE_ROOT / "evd_0001.md"


@pytest.fixture
def candidate_evd_missing_kind() -> Path:
    return CANDIDATE_ROOT / "evd_missing_kind.md"


@pytest.fixture
def bad_candidate() -> Path:
    return CANDIDATE_ROOT / "bad.md"


@pytest.fixture
def candidate_neg_incomplete() -> Path:
    return CANDIDATE_ROOT / "neg_incomplete.md"


@pytest.fixture
def candidate_neg_ok() -> Path:
    return CANDIDATE_ROOT / "neg_0001.md"


@pytest.fixture
def candidate_gov_missing_level() -> Path:
    return CANDIDATE_ROOT / "gov_missing_level.md"


@pytest.fixture
def candidate_gov_public_verified() -> Path:
    return CANDIDATE_ROOT / "gov_public_verified.md"


@pytest.fixture
def candidate_gov_public_local_only() -> Path:
    return CANDIDATE_ROOT / "gov_public_local_only.md"


@pytest.fixture
def candidate_gov_identical() -> Path:
    return CANDIDATE_ROOT / "gov_identical.md"


@pytest.fixture
def candidate_aic() -> Path:
    return CANDIDATE_ROOT / "aic_0001.md"


@pytest.fixture
def candidate_aic_conflict() -> Path:
    return CANDIDATE_ROOT / "aic_0001_conflict.md"


@pytest.fixture
def candidate_dec() -> Path:
    return CANDIDATE_ROOT / "dec_0001.md"
