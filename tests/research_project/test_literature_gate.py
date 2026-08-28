import json

from tools.research_project.cli import main
from tools.research_project.constants import GATE_METRIC_NAMES, LITERATURE_GATE_METRIC_NAMES


def test_literature_gate_json_reports_metrics(capsys):
    code = main(["literature-gate", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    names = [m["name"] for m in payload["metrics"]]
    assert names == list(LITERATURE_GATE_METRIC_NAMES)
    assert payload["contract_version"] == "1.3"
    assert payload["status"] == "PASS"
    for m in payload["metrics"]:
        assert m["status"] == "PASS"


def test_v11_gate_metric_names_unchanged(capsys):
    code = main(["gate", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert [m["name"] for m in payload["metrics"]] == list(GATE_METRIC_NAMES)
