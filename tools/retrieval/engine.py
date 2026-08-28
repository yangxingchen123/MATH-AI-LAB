"""v2.0 retrieval: metadata → FTS → BM25 → Hybrid RRF. Vector is not installed."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

LEVEL_RANK = {"PUBLIC": 0, "PERSONAL": 1, "RESTRICTED": 2}
TOKEN_RE = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]+")
LATEX_RE = re.compile(r"\\[a-zA-Z]+|[≥≤≠∈∀∃∞]|\\geq|\\leq")
RRF_K = 60


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    data_level: str = "PUBLIC"
    retracted: bool = False
    stale: bool = False
    object_type: str = "note"
    year: int | None = None
    trust_level: str = "DERIVED"
    polarity: str = "neutral"
    source_hash: str = ""
    superseded: bool = False


def tokenize(text: str) -> list[str]:
    lowered = text.lower().replace("\\geq", "≥").replace("\\leq", "≤")
    latex = [item.lower() for item in LATEX_RE.findall(lowered)]
    words = TOKEN_RE.findall(lowered)
    return latex + words


def permitted(doc: Document, principal_level: str) -> bool:
    return LEVEL_RANK.get(doc.data_level, 99) <= LEVEL_RANK.get(principal_level, 0)


class Corpus:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        self._tokens = {doc.doc_id: tokenize(doc.text) for doc in documents}

    def visible(self, principal_level: str, *, include_retracted: bool = False) -> list[Document]:
        out: list[Document] = []
        for doc in self.documents:
            if not permitted(doc, principal_level):
                continue
            if doc.retracted and not include_retracted:
                continue
            if doc.stale or doc.superseded:
                continue
            out.append(doc)
        return out

    def metadata(
        self,
        principal_level: str,
        *,
        object_type: str | None = None,
        year: int | None = None,
        trust_level: str | None = None,
    ) -> list[Document]:
        hits = []
        for doc in self.visible(principal_level):
            if object_type and doc.object_type != object_type:
                continue
            if year is not None and doc.year != year:
                continue
            if trust_level and doc.trust_level != trust_level:
                continue
            hits.append(doc)
        return hits

    def fts(self, query: str, principal_level: str, k: int = 5) -> list[Document]:
        terms = tokenize(query)
        if not terms:
            return []
        hits = []
        for doc in self.visible(principal_level):
            tokens = set(self._tokens[doc.doc_id])
            if all(term in tokens for term in terms):
                hits.append(doc)
        return hits[:k]

    def bm25(self, query: str, principal_level: str, k: int = 5) -> list[tuple[float, Document]]:
        docs = self.visible(principal_level)
        if not docs:
            return []
        tokenized = [self._tokens[doc.doc_id] for doc in docs]
        avgdl = sum(len(tokens) for tokens in tokenized) / len(docs)
        df: Counter[str] = Counter()
        tfs: list[Counter[str]] = []
        for tokens in tokenized:
            counts = Counter(tokens)
            tfs.append(counts)
            for term in counts:
                df[term] += 1
        q_terms = tokenize(query)
        scored: list[tuple[float, Document]] = []
        k1, b = 1.5, 0.75
        n = len(docs)
        for i, doc in enumerate(docs):
            dl = sum(tfs[i].values()) or 1
            score = 0.0
            for term in q_terms:
                freq = tfs[i].get(term, 0)
                if not freq:
                    continue
                idf = math.log((n - df[term] + 0.5) / (df[term] + 0.5) + 1)
                score += idf * (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * dl / avgdl))
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[:k]

    def vector(self, query: str, principal_level: str, k: int = 5) -> dict:
        del query, principal_level, k
        return {"status": "DEGRADED", "hits": [], "note": "vector Sidecar not installed"}

    def hybrid(self, query: str, principal_level: str, k: int = 5) -> list[tuple[float, Document]]:
        scores: dict[str, float] = defaultdict(float)
        by_id = {doc.doc_id: doc for doc in self.visible(principal_level)}
        for rank, doc in enumerate(self.fts(query, principal_level, k=k * 2), start=1):
            scores[doc.doc_id] += 1.0 / (RRF_K + rank)
        for rank, (_score, doc) in enumerate(self.bm25(query, principal_level, k=k * 2), start=1):
            scores[doc.doc_id] += 1.0 / (RRF_K + rank)
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [(score, by_id[doc_id]) for doc_id, score in ranked if doc_id in by_id][:k]


def cited_answer(query: str, corpus: Corpus, principal_level: str) -> dict:
    hybrid = corpus.hybrid(query, principal_level)
    hits = [doc for _, doc in hybrid]
    if not hits:
        hits = [doc for _, doc in corpus.bm25(query, principal_level)]
    if not hits:
        hits = corpus.fts(query, principal_level)
    if not hits:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "answer": None,
            "citations": [],
            "kind": "inference",
            "candidate": True,
            "writes_source": False,
            "conflicts": [],
        }
    conflicts = [doc.doc_id for doc in hits if doc.polarity == "opposes"]
    supports = [doc.doc_id for doc in hits if doc.polarity != "opposes"]
    status = "CONFLICT" if conflicts and supports else "OK"
    return {
        "status": status,
        "answer": hits[0].text,
        "citations": [doc.doc_id for doc in hits],
        "kind": "paraphrase",
        "candidate": True,
        "writes_source": False,
        "conflicts": conflicts,
    }


def unsupported_attribution(answer_citations: list[str], retrieved_ids: list[str]) -> bool:
    retrieved = set(retrieved_ids)
    return any(item not in retrieved for item in answer_citations)
