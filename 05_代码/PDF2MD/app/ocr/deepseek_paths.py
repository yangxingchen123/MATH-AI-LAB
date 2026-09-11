"""DeepSeek-OCR 2 本地权重 / 专用 venv 路径（GUI 与脚本共用）。"""
from __future__ import annotations

import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_HUB_ID = "deepseek-ai/DeepSeek-OCR-2"


def _load_local_env() -> None:
    env_path = _PROJECT_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
        return
    except Exception:
        pass
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def hf_root() -> Path:
    raw = (os.environ.get("PDF2MD_HF_HOME") or os.environ.get("HF_HOME") or "").strip()
    if raw:
        return Path(raw)
    return _PROJECT_ROOT / ".cache" / "hf"


def deepseek_model_dir() -> Path:
    raw = (os.environ.get("PDF2MD_DEEPSEEK_MODEL_DIR") or "").strip()
    if raw:
        return Path(raw)
    return _PROJECT_ROOT / ".cache" / "models" / "DeepSeek-OCR-2"


def dsocr2_python_path() -> Path:
    raw = (os.environ.get("PDF2MD_DSOCR2_PYTHON") or "").strip()
    if raw:
        return Path(raw)
    win = _PROJECT_ROOT / ".venv-dsocr2" / "Scripts" / "python.exe"
    nix = _PROJECT_ROOT / ".venv-dsocr2" / "bin" / "python"
    if win.is_file():
        return win
    if nix.is_file():
        return nix
    return win


def _refresh_exports() -> None:
    global HF_ROOT, DEEPSEEK_MODEL_DIR, DSOCR2_PYTHON
    HF_ROOT = hf_root()
    DEEPSEEK_MODEL_DIR = deepseek_model_dir()
    DSOCR2_PYTHON = dsocr2_python_path()


def ensure_deepseek_hf_env() -> None:
    _load_local_env()
    _refresh_exports()
    HF_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(HF_ROOT))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(HF_ROOT / "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(HF_ROOT / "transformers"))
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
    os.environ.setdefault("USE_TF", "0")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def resolve_deepseek_model_name() -> str:
    _refresh_exports()
    model_dir = DEEPSEEK_MODEL_DIR
    if model_dir.is_dir() and (
        (model_dir / "config.json").is_file()
        or any(model_dir.glob("*.safetensors"))
        or any(model_dir.glob("*.bin"))
    ):
        return str(model_dir)
    return (os.environ.get("PDF2MD_DEEPSEEK_MODEL_ID") or _HUB_ID).strip() or _HUB_ID


def resolve_dsocr2_python() -> Path | None:
    _refresh_exports()
    if DSOCR2_PYTHON.is_file():
        return DSOCR2_PYTHON
    return None


_load_local_env()
HF_ROOT = hf_root()
DEEPSEEK_MODEL_DIR = deepseek_model_dir()
DSOCR2_PYTHON = dsocr2_python_path()
