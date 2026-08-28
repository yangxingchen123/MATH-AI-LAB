from pathlib import Path
import hashlib
import re

FIXTURE_ROOT = Path("tests/research_project/fixtures")
MANIFEST = FIXTURE_ROOT / "SHA256SUMS"
LINE_RE = re.compile(r"^([0-9a-f]{64})  (.+)$")


def _listed_entries():
    entries = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        assert m, f"bad manifest line: {line!r}"
        entries.append((m.group(1), m.group(2)))
    return entries


def test_sha256sums_excludes_self_and_covers_exact_set():
    entries = _listed_entries()
    listed = [rel for _, rel in entries]
    assert "SHA256SUMS" not in listed
    assert len(listed) == len(set(listed))
    for rel in listed:
        assert not rel.startswith("/") and "\\" not in rel and ".." not in Path(rel).parts
    actual = sorted(
        p.relative_to(FIXTURE_ROOT).as_posix()
        for p in FIXTURE_ROOT.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS"
    )
    assert sorted(listed) == actual
    for digest, rel in entries:
        assert hashlib.sha256((FIXTURE_ROOT / rel).read_bytes()).hexdigest() == digest


def test_text_fixtures_have_no_crlf():
    for p in FIXTURE_ROOT.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".txt"}:
            assert b"\r\n" not in p.read_bytes()
