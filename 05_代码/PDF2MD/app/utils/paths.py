"""应用路径：项目根目录由 __file__ / 环境变量解析。"""
from __future__ import annotations

import os
from pathlib import Path

def _resolve_python() -> Path:
    raw = (os.environ.get("PDF2MD_PYTHON") or "").strip()
    if raw:
        return Path(raw)
    root = Path(__file__).resolve().parents[2]
    venv_py = root / ".venv" / "Scripts" / "python.exe"
    if venv_py.is_file():
        return venv_py
    import sys

    return Path(sys.executable)


PYTHON_EXE = _resolve_python()
DOCLING_EXE = Path(os.environ.get("PDF2MD_DOCLING_EXE", "docling"))
MINERU_EXE = Path(os.environ.get("PDF2MD_MINERU_EXE", "mineru"))

APP_ROOT = Path(__file__).resolve().parents[2]
DOCLING_ARTIFACTS_DIR = Path(
    os.environ.get(
        "PDF2MD_DOCLING_ARTIFACTS",
        str(APP_ROOT / ".cache" / "docling-artifacts"),
    )
)
INPUT_DIR = APP_ROOT / "input"
TESTSET_DIR = Path(os.environ.get("PDF2MD_TESTSET_DIR", str(APP_ROOT / "input")))
OULAD_PDF_DIR = Path(
    os.environ.get("PDF2MD_OULAD_PDF_DIR", str(INPUT_DIR / "oulad"))
)
OUTPUT_DIR = APP_ROOT / "output"
LOGS_DIR = APP_ROOT / "logs"

_DESKTOP_APP_NAMES = {"pdftomd", "pdf2md", "pdf-to-md", "pdf_to_md"}


def looks_like_foreign_desktop_output(path: Path | str) -> bool:
    """桌面上的 PDFTomd 等外置目录：会在桌面新建文件夹，不应再当导出根。"""
    try:
        p = Path(path)
        parts = [x.lower() for x in p.parts]
    except Exception:
        return True
    if "pdftomd" in parts:
        try:
            p.resolve().relative_to(APP_ROOT.resolve())
            return False
        except Exception:
            return True
    try:
        desktop = (Path.home() / "Desktop").resolve()
        parent = p.parent.resolve() if p.parent else None
        if parent == desktop and p.name.lower() in _DESKTOP_APP_NAMES:
            return True
        if p.resolve() == desktop:
            return True
    except Exception:
        pass
    return False


def sanitize_output_dir(raw: str | Path | None) -> Path:
    """把错误写到桌面 PDFTomd 的路径收回本项目 output/。"""
    if raw is None or str(raw).strip() == "":
        return OUTPUT_DIR
    p = Path(str(raw).strip()).expanduser()
    if not p.is_absolute():
        p = (APP_ROOT / p).resolve()
    if looks_like_foreign_desktop_output(p):
        return OUTPUT_DIR
    return p


# 实验结果诊断镜像（timings / formula_qa）；不进论文导出目录
EXPERIMENT_DIR = LOGS_DIR / "experiment"
ICONS_DIR = APP_ROOT / "icons"
SCRIPTS_DIR = APP_ROOT / "scripts"
BENCHMARK_DIR = APP_ROOT / "debug" / "formula_benchmark"
BENCHMARK_CORPUS = BENCHMARK_DIR / "corpus"
BENCHMARK_RUNS = BENCHMARK_DIR / "runs"
BENCHMARK_EXPECTED = BENCHMARK_DIR / "expected"
DEEPSEEK_BENCHMARK_RUNS = BENCHMARK_DIR / "deepseek_runs"
K5_BENCHMARK_DIR = APP_ROOT / "benchmarks"
K5_MANIFESTS_DIR = K5_BENCHMARK_DIR / "manifests"
K5_CROPS_DIR = K5_BENCHMARK_DIR / "crops"
K5_TIGHT_CROPS_DIR = K5_CROPS_DIR / "tight"
K5_GOLD_DIR = K5_BENCHMARK_DIR / "gold"
K5_RESULTS_DIR = K5_BENCHMARK_DIR / "results"
K5_HARD_CASES_DIR = K5_BENCHMARK_DIR / "hard_cases"


def ensure_dirs() -> None:
    for d in (
        INPUT_DIR,
        OUTPUT_DIR,
        LOGS_DIR,
        EXPERIMENT_DIR,
        ICONS_DIR,
        SCRIPTS_DIR,
        BENCHMARK_DIR,
        BENCHMARK_CORPUS,
        BENCHMARK_RUNS,
        BENCHMARK_EXPECTED,
        DEEPSEEK_BENCHMARK_RUNS,
        K5_BENCHMARK_DIR,
        K5_MANIFESTS_DIR,
        K5_CROPS_DIR,
        K5_TIGHT_CROPS_DIR,
        K5_GOLD_DIR,
        K5_RESULTS_DIR,
        K5_HARD_CASES_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)


def experiment_doc_dir(stem: str) -> Path:
    """单篇文档的实验结果镜像目录。"""
    d = EXPERIMENT_DIR / stem
    d.mkdir(parents=True, exist_ok=True)
    return d


def task_output_dir(output_root: Path, pdf_path: Path, per_folder: bool) -> Path:
    stem = pdf_path.stem
    if per_folder:
        return output_root / stem
    return output_root


def vision_task_output_dir(output_root: Path, pdf_path: Path) -> Path:
    """高保真模式：在选定输出目录下创建「Pdf名_高保真」文件夹。"""
    return Path(output_root) / f"{pdf_path.stem}_高保真"
