# -*- coding: utf-8 -*-
from __future__ import annotations

from app.engines import docling_engine
from app.engines.docling_gpu_release import release_docling_gpu


def test_release_docling_gpu_can_keep_or_clear_converter():
    marker = object()
    docling_engine._converter_cache["test-keep"] = marker
    try:
        info = release_docling_gpu(empty_cache=False, clear_converter=False)
        assert info["clear_converter"] is False
        assert docling_engine._converter_cache.get("test-keep") is marker
        info2 = release_docling_gpu(empty_cache=False, clear_converter=True)
        assert info2["clear_converter"] is True
        assert "test-keep" not in docling_engine._converter_cache
        assert any(str(n).startswith("cleared_converter_cache:") for n in info2["notes"])
    finally:
        docling_engine._converter_cache.pop("test-keep", None)
