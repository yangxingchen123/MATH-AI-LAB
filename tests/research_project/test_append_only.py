import shutil
import subprocess
from pathlib import Path

from tools.research_project.append_only import (
    assert_decisions_append_only,
    check_append_only_all,
)

DEC1 = (
    "<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0001 BEGIN -->\n"
    "- date: 2026-08-20\n"
    "- question: q\n"
    "- options: a|b\n"
    "- choice: a\n"
    "- basis: b\n"
    "- cost: c\n"
    "- reversible: false\n"
    "- revisit_when: never\n"
    "---\n"
    "body1\n"
    "<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0001 END -->\n"
)

DEC2 = (
    "\n<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0002 BEGIN -->\n"
    "- date: 2026-08-21\n"
    "- question: q2\n"
    "- options: a|b\n"
    "- choice: b\n"
    "- basis: b\n"
    "- cost: c\n"
    "- reversible: true\n"
    "- revisit_when: later\n"
    "---\n"
    "body2\n"
    "<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0002 END -->\n"
)


def test_append_only_accepts_tail_append():
    assert_decisions_append_only(DEC1, DEC1 + DEC2)


def test_append_only_rejects_edit_delete_reorder_insert_whitespace():
    base = DEC1
    for bad in [
        base.replace("body1", "body1-edited"),
        "",
        base.replace("body1\n", "body1 \n"),
        DEC2 + base,
        DEC1.replace("DEC-0001", "DEC-0002") + DEC1,
    ]:
        raised = False
        try:
            assert_decisions_append_only(base, bad)
        except ValueError:
            raised = True
        assert raised


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)


def _seed_decisions_repo(tmp_path: Path) -> tuple[Path, str, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    proj = repo / "07_项目" / "Demo"
    proj.mkdir(parents=True)
    decisions = proj / "decisions.md"
    decisions.write_text(DEC1, encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    return repo, base, decisions


def test_check_append_only_all_disposable_matrix(tmp_path):
    repo, base, decisions = _seed_decisions_repo(tmp_path)
    decisions.write_text(decisions.read_text(encoding="utf-8") + DEC2, encoding="utf-8", newline="\n")
    assert check_append_only_all(repo, base).ok is True


def test_check_append_only_all_edit_historical_fails(tmp_path):
    repo, base, decisions = _seed_decisions_repo(tmp_path)
    text = decisions.read_text(encoding="utf-8")
    decisions.write_text(text.replace("body1", "body1-edited"), encoding="utf-8", newline="\n")
    assert check_append_only_all(repo, base).ok is False


def test_check_append_only_all_delete_file_fails(tmp_path):
    repo, base, decisions = _seed_decisions_repo(tmp_path)
    decisions.unlink()
    assert check_append_only_all(repo, base).ok is False


def test_check_append_only_all_delete_project_fails(tmp_path):
    repo, base, decisions = _seed_decisions_repo(tmp_path)
    shutil.rmtree(decisions.parent)
    assert check_append_only_all(repo, base).ok is False


def test_check_append_only_all_rename_disappear_fails(tmp_path):
    repo, base, decisions = _seed_decisions_repo(tmp_path)
    new_proj = repo / "07_项目" / "Renamed"
    new_proj.mkdir()
    decisions.rename(new_proj / "decisions.md")
    assert check_append_only_all(repo, base).ok is False


def test_check_append_only_all_new_project_ok(tmp_path):
    repo, base, _ = _seed_decisions_repo(tmp_path)
    new_proj = repo / "07_项目" / "Brand_New"
    new_proj.mkdir()
    (new_proj / "decisions.md").write_text(DEC1.replace("2026-08-20", "2026-08-22").replace("body1", "new"), encoding="utf-8", newline="\n")
    assert check_append_only_all(repo, base).ok is True


def test_check_append_only_all_spaces_and_windows_normalization(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    proj = repo / "07_项目" / "My Project"
    proj.mkdir(parents=True)
    decisions = proj / "decisions.md"
    decisions.write_text(DEC1, encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    assert check_append_only_all(Path(str(repo).replace("/", "\\")), base).ok is True


def test_check_append_only_all_invalid_base_ref_fails(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    result = check_append_only_all(repo, "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
    assert result.ok is False


def test_check_append_only_all_valid_base_path_absent_ok_as_empty(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    (repo / "README.md").write_text("x\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    proj = repo / "07_项目" / "Later"
    proj.mkdir(parents=True)
    (proj / "decisions.md").write_text(DEC1, encoding="utf-8", newline="\n")
    assert check_append_only_all(repo, base).ok is True


def test_template_excluded_from_all(tmp_path):
    repo, base, _ = _seed_decisions_repo(tmp_path)
    tmpl = repo / "07_项目" / "_模板" / "研究项目_v1.1"
    tmpl.mkdir(parents=True)
    (tmpl / "decisions.md").write_text("mutated template decisions\n", encoding="utf-8", newline="\n")
    assert check_append_only_all(repo, base).ok is True
