#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建 .venv-paddle-formula（与 GUI Torch 环境隔离）。

默认装 CPU paddle 以便先打通 worker；GPU 用 --gpu。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv-paddle-formula"


def _py() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", action="store_true", help="paddlepaddle-gpu cu126")
    args = ap.parse_args()

    if not VENV.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    py = _py()
    subprocess.check_call([str(py), "-m", "pip", "install", "-U", "pip"])
    if args.gpu:
        paddle = [
            str(py),
            "-m",
            "pip",
            "install",
            "paddlepaddle-gpu==3.2.0",
            "-i",
            "https://www.paddlepaddle.org.cn/packages/stable/cu126/",
        ]
    else:
        paddle = [str(py), "-m", "pip", "install", "paddlepaddle==3.2.0"]
    print("install", paddle)
    subprocess.check_call(paddle)
    # paddlex[ocr] 会把 pip 拖进 langchain/modelscope 回退；公式 worker 只需 ocr 运行时依赖。
    subprocess.check_call(
        [str(py), "-m", "pip", "install", "paddleocr==3.7.0", "paddlex==3.7.2", "--no-deps"]
    )
    subprocess.check_call(
        [
            str(py),
            "-m",
            "pip",
            "install",
            "numpy<2.4,>=1.24",
            "huggingface_hub>=0.23,<1",
            "PyYAML==6.0.2",
            "aistudio-sdk",
            "chardet",
            "colorlog",
            "filelock",
            "packaging",
            "pandas",
            "prettytable",
            "py-cpuinfo",
            "pydantic>=2",
            "requests",
            "ruamel.yaml",
            "ujson",
            "modelscope>=1.28.0",
            "aiohttp>=3.8.0",
            "imagesize",
            "opencv-contrib-python==4.10.0.84",
            "pyclipper",
            "pypdfium2>=4",
            "python-bidi",
            "shapely",
            "beautifulsoup4",
            "einops",
            "ftfy",
            "Jinja2",
            "latex2mathml",
            "lxml",
            "openpyxl",
            "premailer",
            "regex",
            "safetensors>=0.7.0",
            "scikit-learn",
            "scipy",
            "sentencepiece",
            "tiktoken",
            "tokenizers>=0.19",
            "pillow",
        ]
    )
    print({"ok": True, "python": str(py)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
