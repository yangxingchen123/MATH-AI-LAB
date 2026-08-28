"""v2.0 retrieval first rungs (metadata / FTS / BM25 / Hybrid RRF)."""

from .engine import Corpus, Document, cited_answer, unsupported_attribution
from .gate import evaluate_gate

__all__ = ["Corpus", "Document", "cited_answer", "evaluate_gate", "unsupported_attribution"]
