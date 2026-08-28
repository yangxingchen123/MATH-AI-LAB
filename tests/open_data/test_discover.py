from tools.open_data.discover import discover_open_data, write_candidates
from tools.open_data.licenses import classify_license


def test_classify_open_and_reject_nc():
    assert classify_license("cc-by-4.0") == "OPEN"
    assert classify_license("CC0-1.0") == "OPEN"
    assert classify_license("us-government-work") == "OPEN"
    assert classify_license("cc-by-nc-4.0") == "REJECTED"
    assert classify_license("") == "NEEDS_REVIEW"


def test_discover_uses_injected_catalog_and_filters(tmp_path):
    payload = {
        "hits": {
            "hits": [
                {
                    "doi": "10.5281/zenodo.1",
                    "metadata": {
                        "title": "Smartphone battery component power",
                        "license": {"id": "cc-by-4.0"},
                        "description": "screen CPU GPS power",
                    },
                    "links": {"html": "https://zenodo.org/records/1"},
                },
                {
                    "doi": "10.5281/zenodo.9",
                    "metadata": {
                        "title": "Lithium-ion battery voltage dump",
                        "license": {"id": "cc0-1.0"},
                    },
                    "links": {"self_html": "https://zenodo.org/records/9"},
                },
                {
                    "doi": "10.5281/zenodo.2",
                    "metadata": {
                        "title": "Secret drain logs",
                        "license": {"id": "cc-by-nc-4.0"},
                    },
                    "links": {"html": "https://zenodo.org/records/2"},
                },
            ]
        }
    }

    def fetcher(_url: str) -> dict:
        return payload

    report = discover_open_data(
        queries=("smartphone power",),
        fetcher=fetcher,
        include_seeds=False,
    )
    assert report["status"] == "PASS"
    assert report["core_impact"] is False
    titles = [item["title"] for item in report["hits"]]
    assert "Smartphone battery component power" in titles
    assert "Lithium-ion battery voltage dump" in titles
    assert "Secret drain logs" not in titles
    assert all(item["license_status"] == "OPEN" for item in report["hits"])


def test_discover_drops_household_false_positive():
    payload = {
        "hits": {
            "hits": [
                {
                    "doi": "10.5281/zenodo.3",
                    "metadata": {
                        "title": "Household Active Power Consumption Dataset",
                        "license": {"id": "cc-by-4.0"},
                        "description": "power consumption of houses",
                    },
                    "links": {"self_html": "https://zenodo.org/records/3"},
                }
            ]
        }
    }
    report = discover_open_data(
        queries=("smartphone power",),
        fetcher=lambda _url: payload,
        include_seeds=False,
    )
    assert report["hits"] == []


def test_network_failure_falls_back_to_seeds():
    def fetcher(_url: str) -> dict:
        raise OSError("offline")

    report = discover_open_data(queries=("lithium battery",), fetcher=fetcher)
    assert report["status"] == "DEGRADED"
    assert report["core_impact"] is False
    assert report["hits"]
    assert all(item["source"] == "seed" for item in report["hits"])


def test_write_candidates_does_not_touch_literature(tmp_path):
    project = tmp_path / "07_项目" / "美赛2026-A"
    (project / "documents").mkdir(parents=True)
    (project / "literature.md").write_text("# Literature\n", encoding="utf-8")
    report = {
        "status": "PASS",
        "hits": [
            {
                "title": "Demo",
                "url": "https://example.org/data",
                "doi": "",
                "license_id": "cc-by-4.0",
                "license_status": "OPEN",
                "catalog": "zenodo",
                "source": "api",
                "query": "battery",
                "why": "component power",
            }
        ],
    }
    path = write_candidates(project, report)
    assert path.is_file()
    assert "Demo" in path.read_text(encoding="utf-8")
    assert path.parent.name == "documents"
    assert (project / "literature.md").read_text(encoding="utf-8") == "# Literature\n"
