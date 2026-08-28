"""Known landing pages used when the live catalog is unreachable. Not an ingest list."""

from __future__ import annotations

SEED_HITS: tuple[dict[str, str], ...] = (
    {
        "title": "AndroWatts: Unpacking the Power Consumption of Mobile Device's Components",
        "url": "https://zenodo.org/records/14314943",
        "doi": "10.5281/zenodo.14314943",
        "license_id": "check-landing-page",
        "license_status": "NEEDS_REVIEW",
        "catalog": "zenodo",
        "why": "Android component-level power traces for screen/CPU-like contributors",
        "query": "seed:smartphone-power",
        "source": "seed",
    },
    {
        "title": "Battery Impact of Individual Hardware Sensors in Modern iPhone Devices",
        "url": "https://bonndata.uni-bonn.de/catalog/datasets/10.60507/FK2/LSJGWW/",
        "doi": "10.60507/FK2/LSJGWW",
        "license_id": "cc-by-4.0",
        "license_status": "OPEN",
        "catalog": "bonndata",
        "why": "CC BY 4.0 iPhone sensor battery-impact experiments",
        "query": "seed:smartphone-power",
        "source": "seed",
    },
    {
        "title": "NASA PCoE Li-ion Battery Data Set (Saha & Goebel 2007)",
        "url": "https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/",
        "doi": "",
        "license_id": "us-government-work",
        "license_status": "OPEN",
        "catalog": "nasa-pcoe",
        "why": "Cell-level voltage/current discharge for voltage and rate-capacity checks",
        "query": "seed:voltage-peukert",
        "source": "seed",
    },
)

DEFAULT_QUERIES: tuple[str, ...] = (
    "smartphone component power consumption dataset",
    "lithium-ion battery voltage discharge dataset",
    "battery capacity rate peukert lithium-ion",
)

ZENODO_SEARCH = "https://zenodo.org/api/records/?q={query}&type=dataset&size=5&sort=bestmatch"
