"""Preview-then-persist helper for Qt. Reuses tools.ui_operations."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from tools.ui_operations.gateway import run_operation
from tools.ui_operations.models import OperationResult


def preview_operation(root: Path, operation: str, payload: dict[str, Any]) -> OperationResult:
    return run_operation(
        root,
        {
            "version": 1,
            "operation": operation,
            "preview": True,
            "requestId": str(uuid.uuid4()),
            "payload": payload,
        },
    )


def persist_operation(root: Path, operation: str, payload: dict[str, Any]) -> OperationResult:
    return run_operation(
        root,
        {
            "version": 1,
            "operation": operation,
            "preview": False,
            "requestId": str(uuid.uuid4()),
            "payload": payload,
        },
    )


def format_result(result: OperationResult) -> str:
    lines = [
        f"operation: {result.operation}",
        f"{'preview' if result.preview else 'persist'} · success={result.success} · validation={result.validation}",
    ]
    if result.error:
        lines.append(f"error: {result.error}")
    if result.affected_objects:
        lines.append("objects: " + ", ".join(result.affected_objects))
    if result.changed_files:
        lines.append("changed files:")
        lines.extend(f"  {item}" for item in result.changed_files[:12])
    if result.warnings:
        lines.extend(result.warnings[:8])
    for issue in result.issues[:8]:
        lines.append(f"{issue.level}: {issue.message}")
    if result.planned:
        lines.append(json.dumps(result.planned, ensure_ascii=False, indent=2)[:2400])
    return "\n".join(lines)


def run_gated(parent: Any, root: Path, operation: str, payload: dict[str, Any]) -> OperationResult | None:
    from PySide6.QtWidgets import QMessageBox

    preview = preview_operation(root, operation, payload)
    if not preview.success or preview.validation == "FAIL":
        QMessageBox.warning(parent, "无法预览", format_result(preview))
        return preview
    box = QMessageBox(parent)
    box.setWindowTitle(f"确认 {operation}")
    box.setText("预览通过。确认后才会写入仓库。")
    box.setInformativeText(format_result(preview)[:4000])
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.No)
    if box.exec() != QMessageBox.StandardButton.Yes:
        return None
    persist = persist_operation(root, operation, payload)
    if persist.success:
        QMessageBox.information(parent, "已写入", format_result(persist)[:4000])
    else:
        QMessageBox.warning(parent, "写入失败", format_result(persist))
    return persist
