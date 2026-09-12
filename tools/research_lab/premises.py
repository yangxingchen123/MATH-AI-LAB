"""Accessible-premise retrieval. Hits are candidates, never answers."""

from __future__ import annotations

import yaml

from tools.retrieval.engine import Corpus, Document, cited_answer

from .constants import CORRESPONDENCE_PATH


def correspondence_corpus() -> Corpus:
    data = yaml.safe_load(CORRESPONDENCE_PATH.read_text(encoding="utf-8")) or {}
    documents: list[Document] = []
    for item in data.get("theorems") or []:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        documents.append(
            Document(
                doc_id=str(item["id"]),
                text=str(item.get("natural_language") or ""),
                object_type="theorem",
                trust_level="DERIVED",
            )
        )
    return Corpus(documents)


def retrieve_premises(query: str, *, principal_level: str = "PUBLIC") -> dict:
    result = cited_answer(query, correspondence_corpus(), principal_level)
    result["is_answer"] = False
    result["candidate"] = True
    result["writes_source"] = False
    result["note"] = "Retrieved premises are candidates. Reconstruction must precede retrieval."
    return result
