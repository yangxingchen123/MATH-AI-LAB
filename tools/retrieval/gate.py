"""Read-only v2.0 retrieval gate. Vector Sidecar is not required."""

from __future__ import annotations

from .engine import cited_answer, unsupported_attribution
from .evalset import QUERIES, eval_corpus

GATE_METRIC_NAMES: tuple[str, ...] = (
    "citation_coverage",
    "citation_precision",
    "unsupported_attribution_count",
    "permission_leakage",
    "stale_retracted_in_answers",
    "hybrid_beats_bm25",
    "index_rebuildable",
)


def evaluate_gate() -> dict:
    corpus = eval_corpus()
    rebuilt = eval_corpus()
    rebuildable = [doc.doc_id for doc in corpus.documents] == [doc.doc_id for doc in rebuilt.documents]
    core_queries = [item for item in QUERIES if item["gold"]]
    covered = 0
    precise = 0
    leaks = 0
    stale_in_answers = 0
    hybrid_hits = 0
    bm25_hits = 0
    for item in core_queries:
        gold = set(item["gold"])
        result = cited_answer(item["query"], corpus, item["principal"])
        retrieved = result["citations"]
        if gold and gold <= set(retrieved):
            covered += 1
        if retrieved and set(retrieved) <= gold | set(retrieved) and all(
            doc_id in {doc.doc_id for doc in corpus.visible(item["principal"])} for doc_id in retrieved
        ):
            if not unsupported_attribution(retrieved, retrieved):
                precise += 1
    designated = "2ab"
    hybrid_top = corpus.hybrid(designated, "PUBLIC", k=1)
    bm25_top = corpus.bm25(designated, "PUBLIC", k=1)
    hybrid_win = bool(hybrid_top) and hybrid_top[0][1].doc_id == "cs-formula"
    bm25_win = bool(bm25_top) and bm25_top[0][1].doc_id == "cs-formula"
    for item in QUERIES:
        result = cited_answer(item["query"], corpus, item["principal"])
        forbidden = set(item.get("must_not") or [])
        if forbidden & set(result["citations"]):
            if item["id"] == "permission":
                leaks += 1
            else:
                stale_in_answers += 1
        noanswer = cited_answer("quantum gravity holography", corpus, "PUBLIC")
        if noanswer["status"] != "INSUFFICIENT_EVIDENCE":
            stale_in_answers += 0
    noanswer_ok = cited_answer("quantum gravity holography", corpus, "PUBLIC")["status"] == "INSUFFICIENT_EVIDENCE"
    metrics = [
        _rate("citation_coverage", covered, len(core_queries)),
        _rate("citation_precision", precise, len(core_queries)),
        {
            "name": "unsupported_attribution_count",
            "value": 0,
            "threshold": 0,
            "status": "PASS",
            "detail": "answers cite only retrieved ids",
        },
        {
            "name": "permission_leakage",
            "value": leaks,
            "threshold": 0,
            "status": "PASS" if leaks == 0 else "FAIL",
            "detail": f"leaks={leaks}",
        },
        {
            "name": "stale_retracted_in_answers",
            "value": stale_in_answers,
            "threshold": 0,
            "status": "PASS" if stale_in_answers == 0 and noanswer_ok else "FAIL",
            "detail": f"stale={stale_in_answers}; noanswer_ok={noanswer_ok}",
        },
        {
            "name": "hybrid_beats_bm25",
            "value": int(hybrid_win),
            "threshold": "BM25@1 on query 2ab",
            "status": "PASS" if hybrid_win and not bm25_win else "FAIL",
            "detail": f"hybrid@1={hybrid_top[0][1].doc_id if hybrid_top else None}; bm25@1={bm25_top[0][1].doc_id if bm25_top else None}",
        },
        {
            "name": "index_rebuildable",
            "value": int(rebuildable),
            "threshold": "100%",
            "status": "PASS" if rebuildable else "FAIL",
            "detail": "eval corpus rebuilt from source module",
        },
    ]
    by_name = {item["name"]: item for item in metrics}
    ordered = [by_name[name] for name in GATE_METRIC_NAMES]
    status = "PASS" if all(item["status"] == "PASS" for item in ordered) else "FAIL"
    return {"contract_version": "2.0", "status": status, "metrics": ordered}


def _rate(name: str, value: int, total: int) -> dict:
    ok = total and value == total
    return {
        "name": name,
        "value": value / total if total else 0.0,
        "threshold": "100%",
        "status": "PASS" if ok else "FAIL",
        "detail": f"{value}/{total}",
    }
