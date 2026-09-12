"""Docling GPU 资源释放：公式恢复前可清 converter，把显存让给 DeepSeek。"""
from __future__ import annotations

from typing import Any


def docling_gpu_snapshot() -> dict[str, Any]:
    try:
        import torch

        if not torch.cuda.is_available():
            return {"cuda": False}
        free_b, total_b = torch.cuda.mem_get_info(0)
        return {
            "cuda": True,
            "allocated_mb": round(torch.cuda.memory_allocated(0) / (1024**2), 1),
            "reserved_mb": round(torch.cuda.memory_reserved(0) / (1024**2), 1),
            "free_mb": round(free_b / (1024**2), 1),
            "total_mb": round(total_b / (1024**2), 1),
        }
    except Exception as e:
        return {"cuda": False, "error": str(e)}


def release_docling_gpu(
    *,
    empty_cache: bool = False,
    clear_converter: bool = True,
) -> dict[str, Any]:
    """释放本进程 Docling converter；可选 empty_cache。

    解析已经结束后再清 converter，下一本会重新加载（磁盘缓存仍在，通常几秒）。
    """
    before = docling_gpu_snapshot()
    notes: list[str] = []
    if clear_converter:
        try:
            from app.engines import docling_engine

            n = len(getattr(docling_engine, "_converter_cache", {}) or {})
            docling_engine._converter_cache.clear()  # noqa: SLF001
            notes.append(f"cleared_converter_cache:{n}")
        except Exception as e:
            notes.append(f"converter_clear_failed:{e}")

    try:
        import gc

        gc.collect()
        notes.append("gc_collect")
    except Exception:
        pass

    if empty_cache:
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                notes.append("torch.cuda.empty_cache")
        except Exception as e:
            notes.append(f"empty_cache_failed:{e}")

    after = docling_gpu_snapshot()
    return {
        "before": before,
        "after": after,
        "notes": notes,
        "empty_cache": empty_cache,
        "clear_converter": clear_converter,
    }
