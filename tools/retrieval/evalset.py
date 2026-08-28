"""Fixed v2.0 retrieval evaluation corpus. Rebuildable from this module."""

from __future__ import annotations

from .engine import Corpus, Document


def eval_corpus() -> Corpus:
    return Corpus(
        [
            Document(
                "cs-en",
                "Cauchy-Schwarz 柯西施瓦茨 inequality: (a·b)^2 ≤ ||a||^2 ||b||^2",
                object_type="theorem",
                year=1821,
                trust_level="REVIEWED",
                polarity="supports",
                source_hash="a" * 64,
            ),
            Document(
                "cs-formula",
                "a^2 + b^2 \\geq 2ab holds for real a, b",
                object_type="theorem",
                year=1821,
                trust_level="REVIEWED",
                polarity="supports",
                source_hash="b" * 64,
            ),
            Document(
                "ab-spam",
                "2ab 2ab 2ab a a a b b b 2 2 2 2ab 2ab",
                object_type="note",
                polarity="neutral",
                source_hash="f" * 64,
            ),
            Document(
                "path-pro",
                "shortest path uniqueness holds on a tree",
                object_type="claim",
                polarity="supports",
                source_hash="c" * 64,
            ),
            Document(
                "path-con",
                "shortest path uniqueness fails on a cycle; opposing evidence",
                object_type="claim",
                polarity="opposes",
                source_hash="d" * 64,
            ),
            Document(
                "ret-1",
                "retracted uniqueness claim",
                retracted=True,
                object_type="claim",
            ),
            Document(
                "sec-1",
                "restricted personnel file",
                data_level="RESTRICTED",
                object_type="note",
            ),
            Document(
                "stale-1",
                "old Cauchy estimate",
                stale=True,
                object_type="note",
            ),
        ]
    )


QUERIES: tuple[dict, ...] = (
    {"id": "exact", "query": "Cauchy-Schwarz", "gold": ["cs-en"], "principal": "PUBLIC"},
    {"id": "synonym", "query": "柯西施瓦茨", "gold": ["cs-en"], "principal": "PUBLIC"},
    {"id": "formula", "query": "a^2 + b^2 \\geq 2ab", "gold": ["cs-formula"], "principal": "PUBLIC"},
    {
        "id": "conflict",
        "query": "shortest path uniqueness",
        "gold": ["path-pro", "path-con"],
        "principal": "PUBLIC",
    },
    {"id": "noanswer", "query": "quantum gravity holography", "gold": [], "principal": "PUBLIC"},
    {
        "id": "permission",
        "query": "personnel",
        "gold": [],
        "principal": "PUBLIC",
        "must_not": ["sec-1"],
    },
    {
        "id": "retracted",
        "query": "retracted uniqueness",
        "gold": [],
        "principal": "PUBLIC",
        "must_not": ["ret-1"],
    },
)
