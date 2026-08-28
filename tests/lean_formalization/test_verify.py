from tools.lean_formalization.verify import verify


def test_verify_report_has_required_keys():
    report = verify()
    assert report["core_impact"] is False
    for key in ("scan_ok", "correspondence_ok", "undeclared", "build_status", "gate_status"):
        assert key in report
    assert report["status"] in {"PASS", "DEGRADED", "FAIL"}
