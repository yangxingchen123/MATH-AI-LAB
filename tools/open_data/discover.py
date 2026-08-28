"""Discover open-license dataset candidates. Sidecar: never writes Knowledge or LIT records."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Callable
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .catalogs import DEFAULT_QUERIES, SEED_HITS, ZENODO_SEARCH
from .licenses import classify_license

_RELEVANCE_TOKENS = (
    "battery",
    "lithium",
    "smartphone",
    "android",
    "iphone",
    "discharge",
    "peukert",
    "state of charge",
    "power consumption",
    "energy consumption",
)


_BLOCK_TOKENS = (
    "household",
    "recycling",
    "market size",
    "extinguishing fires",
    "wearable sensor",
    "countermovement",
)


def _plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def _relevant(title: str, description: str) -> bool:
    blob = f"{title} {description}".lower()
    if any(token in blob for token in _BLOCK_TOKENS):
        return False
    return any(token in blob for token in _RELEVANCE_TOKENS)


Fetcher = Callable[[str], dict]
TIMEOUT_S = 12
USER_AGENT = "MATH-AI-LAB-open-data/0.1 (educational; metadata only; no bulk download)"


def default_fetcher(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=TIMEOUT_S) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8"))


def _hit(
    *,
    title: str,
    url: str,
    doi: str,
    license_id: str,
    catalog: str,
    why: str,
    query: str,
    source: str,
    license_status: str | None = None,
) -> dict[str, str]:
    status = license_status or classify_license(license_id)
    return {
        "title": title,
        "url": url,
        "doi": doi,
        "license_id": license_id,
        "license_status": status,
        "catalog": catalog,
        "why": why,
        "query": query,
        "source": source,
    }


def parse_zenodo_hits(payload: dict, query: str) -> list[dict[str, str]]:
    hits = (((payload or {}).get("hits") or {}).get("hits")) or []
    out: list[dict[str, str]] = []
    for raw in hits:
        if not isinstance(raw, dict):
            continue
        meta = raw.get("metadata") or {}
        license_raw = meta.get("license") or {}
        if isinstance(license_raw, dict):
            license_id = str(license_raw.get("id") or license_raw.get("title") or "")
        else:
            license_id = str(license_raw)
        links = raw.get("links") or {}
        title = str(meta.get("title") or raw.get("title") or "").strip()
        url = str(
            links.get("html")
            or links.get("self_html")
            or links.get("doi")
            or raw.get("doi_url")
            or ""
        ).strip()
        if not title or not url:
            continue
        description = _plain(str(meta.get("description") or ""))
        if not _relevant(title, description):
            continue
        why = "Zenodo dataset metadata matched the query"
        if description:
            why = description[:180]
        item = _hit(
            title=title,
            url=url,
            doi=str(raw.get("doi") or meta.get("doi") or ""),
            license_id=license_id,
            catalog="zenodo",
            why=why,
            query=query,
            source="api",
        )
        if item["license_status"] == "REJECTED":
            continue
        out.append(item)
    return out


def _dedupe(hits: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in hits:
        key = (item.get("doi") or item.get("url") or item.get("title") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def discover_open_data(
    *,
    queries: tuple[str, ...] | list[str] | None = None,
    fetcher: Fetcher | None = None,
    include_seeds: bool = True,
) -> dict:
    chosen = tuple(queries or DEFAULT_QUERIES)
    client = fetcher or default_fetcher
    hits: list[dict[str, str]] = []
    errors: list[str] = []
    if include_seeds:
        hits.extend(dict(item) for item in SEED_HITS)
    for query in chosen:
        url = ZENODO_SEARCH.format(query=quote_plus(query))
        try:
            payload = client(url)
            hits.extend(parse_zenodo_hits(payload, query))
        except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{query}: {exc}")
    hits = _dedupe(hits)
    open_hits = [item for item in hits if item["license_status"] == "OPEN"]
    review_hits = [item for item in hits if item["license_status"] == "NEEDS_REVIEW"]
    status = "PASS"
    if errors and not open_hits and not review_hits:
        status = "DEGRADED"
    elif errors:
        status = "DEGRADED"
    return {
        "status": status,
        "core_impact": False,
        "contract_version": "0.1",
        "queries": list(chosen),
        "errors": errors,
        "hits": hits,
        "open_count": len(open_hits),
        "needs_review_count": len(review_hits),
        "note": (
            "Candidates only. Does not download payloads, estimate parameters, "
            "write literature.md, or create Knowledge."
        ),
    }


def write_candidates(project: Path, report: dict) -> Path:
    dest_dir = Path(project) / "documents"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "open_data_candidates.md"
    lines = [
        "# Open data candidates",
        "",
        f"- generated: {date.today().isoformat()}",
        f"- status: {report.get('status')}",
        f"- open_count: {report.get('open_count', 0)}",
        f"- needs_review_count: {report.get('needs_review_count', 0)}",
        "",
        "这些是**候选**，不是已审核 Literature，也不是已用于估参的数据。",
        "下一步：核许可证 → `ingest-paper` / 人工写入 `literature.md` → 再估参。",
        "禁止把本文件当作 Claim 的事实源。",
        "",
    ]
    if report.get("errors"):
        lines.append("## Catalog errors")
        lines.extend(f"- {item}" for item in report["errors"])
        lines.append("")
    lines.append("## Hits")
    for item in report.get("hits") or []:
        lines.extend(
            [
                f"### {item.get('title') or '(untitled)'}",
                f"- license_status: {item.get('license_status')}",
                f"- license_id: {item.get('license_id')}",
                f"- catalog: {item.get('catalog')} / {item.get('source')}",
                f"- url: {item.get('url')}",
                f"- doi: {item.get('doi') or '(none)'}",
                f"- query: {item.get('query')}",
                f"- why: {item.get('why')}",
                "",
            ]
        )
    if not report.get("hits"):
        lines.append("(none)")
        lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return dest
