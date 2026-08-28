from tools.retrieval.engine import Corpus, Document, cited_answer, unsupported_attribution
from tools.retrieval.evalset import eval_corpus
from tools.retrieval.gate import GATE_METRIC_NAMES, evaluate_gate


def _corpus() -> Corpus:
    return Corpus(
        [
            Document("pub-1", "shortest path on a unit-weight path graph has length 2"),
            Document("ret-1", "retracted claim about uniqueness", retracted=True),
            Document("sec-1", "restricted personnel file", data_level="RESTRICTED"),
            Document("stale-1", "old estimate of the same path", stale=True),
        ]
    )


def test_permission_filter_before_recall():
    corpus = _corpus()
    ids = {doc.doc_id for _, doc in corpus.bm25("restricted personnel", "PUBLIC")}
    assert "sec-1" not in ids
    assert "sec-1" not in {doc.doc_id for doc in corpus.fts("restricted", "PUBLIC")}


def test_retracted_and_stale_are_dropped():
    corpus = _corpus()
    ids = {doc.doc_id for doc in corpus.visible("PUBLIC")}
    assert "ret-1" not in ids
    assert "stale-1" not in ids


def test_bm25_ranks_relevant_document_first():
    corpus = _corpus()
    ranked = corpus.bm25("shortest path length", "PUBLIC")
    assert ranked
    assert ranked[0][1].doc_id == "pub-1"


def test_fts_requires_all_query_terms():
    corpus = _corpus()
    assert [doc.doc_id for doc in corpus.fts("shortest path", "PUBLIC")] == ["pub-1"]
    assert corpus.fts("shortest gravity", "PUBLIC") == []


def test_cited_answer_refuses_without_evidence():
    corpus = _corpus()
    result = cited_answer("unrelated quantum gravity", corpus, "PUBLIC")
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["answer"] is None


def test_unsupported_attribution_detected():
    assert unsupported_attribution(["made-up"], ["pub-1"]) is True
    assert unsupported_attribution(["pub-1"], ["pub-1"]) is False


def test_metadata_filter_and_formula_tokens():
    corpus = eval_corpus()
    theorems = corpus.metadata("PUBLIC", object_type="theorem")
    assert {doc.doc_id for doc in theorems} >= {"cs-en", "cs-formula"}
    hits = corpus.fts(r"a^2 + b^2 \geq 2ab", "PUBLIC")
    assert any(doc.doc_id == "cs-formula" for doc in hits)


def test_hybrid_recalls_conflict_pair():
    corpus = eval_corpus()
    ids = {doc.doc_id for _, doc in corpus.hybrid("shortest path uniqueness", "PUBLIC")}
    assert {"path-pro", "path-con"} <= ids
    answer = cited_answer("shortest path uniqueness", corpus, "PUBLIC")
    assert answer["conflicts"]
    assert answer["candidate"] is True
    assert answer["writes_source"] is False


def test_vector_sidecar_is_degraded():
    corpus = eval_corpus()
    report = corpus.vector("Cauchy-Schwarz", "PUBLIC")
    assert report["status"] == "DEGRADED"
    assert report["hits"] == []


def test_retrieval_gate_passes_eval_set():
    report = evaluate_gate()
    names = [item["name"] for item in report["metrics"]]
    assert names == list(GATE_METRIC_NAMES)
    assert report["status"] == "PASS"
