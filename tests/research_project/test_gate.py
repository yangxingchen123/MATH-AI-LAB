import json

from tools.research_project.cli import main
from tools.research_project.constants import GATE_METRIC_NAMES


def test_gate_json_reports_nine_metrics(capsys):
    code = main(["gate", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    names = [m["name"] for m in payload["metrics"]]
    assert names == list(GATE_METRIC_NAMES)
    for m in payload["metrics"]:
        assert {"numerator", "denominator", "value", "threshold", "status", "evidence"} <= set(m)
        assert m["status"] in {"PASS", "FAIL"}
