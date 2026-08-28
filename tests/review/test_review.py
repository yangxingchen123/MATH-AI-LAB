from pathlib import Path

from tools.review.detect import ROLES, blocking_findings, scan_tree

FIXTURE_ROOT = Path(__file__).parent / "fixtures"


def test_each_role_finds_its_fixture():
    findings = scan_tree(FIXTURE_ROOT)
    found = {item.role for item in findings}
    assert found == set(ROLES)
    assert all(item.severity == "BLOCKING" for item in findings)


def test_blocking_prevents_formal_publish():
    findings = blocking_findings(scan_tree(FIXTURE_ROOT))
    assert findings
    formal_allowed = not findings
    assert formal_allowed is False
