"""Read-only HTTP mapping. No Source mutation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import unquote

from .catalog import build_catalog, get_document
from .constants import STATIC_DIR, STATIC_FILES, VENDOR_DIR, VENDOR_TYPES


@dataclass(frozen=True)
class Response:
    status: int
    content_type: str
    body: bytes


def handle_request(
    method: str,
    path: str,
    query: Mapping[str, str],
    *,
    root: Path,
) -> Response:
    method = method.upper()
    if method not in {"GET", "HEAD"}:
        return Response(405, "text/plain; charset=utf-8", b"method not allowed\n")
    raw_path = unquote(path or "/")
    if ".." in raw_path.split("/"):
        return Response(404, "text/plain; charset=utf-8", b"not found\n")
    if raw_path in {"/", "/index.html"}:
        return _static("index.html")
    if raw_path.startswith("/vendor/"):
        return _vendor(raw_path[len("/vendor/") :])
    if raw_path.lstrip("/") in STATIC_FILES:
        return _static(raw_path.lstrip("/"))
    if raw_path == "/api/catalog":
        payload = build_catalog(root)
        return _json(200, payload)
    if raw_path == "/api/doc":
        kind = str(query.get("kind") or "")
        doc_id = str(query.get("id") or "")
        doc = get_document(root, kind, doc_id)
        if doc is None:
            return _json(404, {"error": "not found"})
        return _json(200, doc)
    return Response(404, "text/plain; charset=utf-8", b"not found\n")


def _static(name: str) -> Response:
    path = (STATIC_DIR / name).resolve()
    if name not in STATIC_FILES or not path.is_file() or path.parent != STATIC_DIR.resolve():
        return Response(404, "text/plain; charset=utf-8", b"not found\n")
    data = path.read_bytes()
    types = {
        "index.html": "text/html; charset=utf-8",
        "styles.css": "text/css; charset=utf-8",
        "app.js": "text/javascript; charset=utf-8",
    }
    return Response(200, types[name], data)


def _vendor(rel: str) -> Response:
    rel = rel.replace("\\", "/").lstrip("/")
    if not rel or ".." in Path(rel).parts:
        return Response(404, "text/plain; charset=utf-8", b"not found\n")
    path = (VENDOR_DIR / rel).resolve()
    try:
        path.relative_to(VENDOR_DIR.resolve())
    except ValueError:
        return Response(404, "text/plain; charset=utf-8", b"not found\n")
    types = VENDOR_TYPES.get(path.suffix.lower())
    if types is None or not path.is_file():
        return Response(404, "text/plain; charset=utf-8", b"not found\n")
    return Response(200, types, path.read_bytes())


def _json(status: int, payload: object) -> Response:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return Response(status, "application/json; charset=utf-8", body)
