"""Sidecar doctor. Missing PySide6 is DEGRADED, not Core FAIL."""

from __future__ import annotations

from typing import Any


def pyside_info() -> dict[str, Any]:
    try:
        import PySide6
        from PySide6 import QtCore
    except ImportError:
        return {"available": False, "version": None}
    version = getattr(PySide6, "__version__", None) or QtCore.qVersion()
    return {"available": True, "version": str(version)}


def webengine_available() -> bool:
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
    except Exception:
        return False
    return True


def doctor() -> dict[str, Any]:
    qt = pyside_info()
    engine = webengine_available() if qt["available"] else False
    return {
        "status": "PASS" if qt["available"] else "DEGRADED",
        "core_impact": False,
        "pyside": qt["available"],
        "pyside_version": qt["version"],
        "webengine": engine,
        "transport": "in-process",
        "http": False,
        "port": None,
        "writes": True,
        "note": (
            "Qt workbench reads and edits Markdown bodies in-process, and runs Domain Operations "
            "(RecordAttempt, MoveProblemWorkflow, Create*, PromoteInboxItem) from the 操作 tab. "
            "The reading tab renders Markdown and KaTeX; the source tab shows raw Markdown. "
            "It does not bind a localhost port. "
            "Saves use UpdateMarkdownBody (preview then persist). YAML is not edited in the source tab. "
            "Lab evaluate and exploration search are read-only and do not write Canonical. "
            "PySide6 is a sidecar; install tools/qt_workbench/requirements.txt. "
            "KaTeX needs Qt WebEngine; without it, headings still render and math stays as $...$."
        ),
    }
