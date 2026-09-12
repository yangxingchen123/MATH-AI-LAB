# -*- coding: utf-8 -*-
"""原子写入 JSON，避免 Windows 上写到一半损坏。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_atomic(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        tmp.replace(path)
    except OSError:
        if path.exists():
            path.unlink()
        tmp.replace(path)
