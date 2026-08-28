from tools.research_project.renderer import render_generated_dossier
from tools.research_project.parser import parse_project


def test_renderer_is_pure_and_omits_reconcile_required(tmp_project):
    docs = parse_project(tmp_project)
    text = render_generated_dossier(docs)
    again = render_generated_dossier(docs)
    assert text == again
    assert "RECONCILE_REQUIRED" not in text
    assert "canonical_fingerprint:" in text
