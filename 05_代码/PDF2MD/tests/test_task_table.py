# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMimeData, QUrl

from app.drop_widget import dropped_input_paths
from app.main_window import MainWindow


def test_dropped_input_paths_keeps_pdf_skips_txt(tmp_path: Path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    txt = tmp_path / "notes.txt"
    txt.write_text("no", encoding="utf-8")
    mime = QMimeData()
    mime.setUrls(
        [
            QUrl.fromLocalFile(str(pdf)),
            QUrl.fromLocalFile(str(txt)),
        ]
    )
    out = dropped_input_paths(mime)
    assert len(out) == 1
    assert Path(out[0]).name == "book.pdf"


def test_markdown_headers_skip_check_and_actions():
    assert MainWindow.COLS_MARKDOWN == [
        "文件",
        "页数",
        "方式",
        "阶段",
        "状态",
        "恢复覆盖",
        "成功写回",
        "耗时",
    ]
