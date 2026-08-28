from tools.workbench.status import capability_status


def test_capability_status_never_blocks_core():
    report = capability_status()
    assert report["core_impact"] is False
    names = {item["name"] for item in report["capabilities"]}
    assert {"modeling", "figure", "lean", "research_project", "reference_library"} <= names
    assert report["status"] in {"PASS", "DEGRADED", "FAIL"}
    assert "gaps" in report
