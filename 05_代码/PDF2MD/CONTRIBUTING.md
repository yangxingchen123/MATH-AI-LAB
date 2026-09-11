# Contributing to PDF2MD

Thanks for your interest in contributing.

中文日常说明见 [README.zh-CN.md](README.zh-CN.md)。下面是给 PR 用的开发约定。

## Development setup

1. Fork and clone the repository
2. Create a virtualenv and install `requirements.txt`
3. Install Docling / MinerU according to upstream docs (not required for EPUB or most unit tests)
4. Run lightweight checks (no model download):
   ```bash
   python -m compileall -q app tests
   pip install pytest
   pytest
   ```
5. Run `python run_gui.py` or `run_gui.bat` (`pythonw`, no console)

## Guidelines

- Keep the UI responsive: never run Docling / MinerU / EPUB parse / vision Playwright on the Qt main thread
- Prefer small, focused PRs
- Do not commit model weights, caches, personal PDFs/EPUBs, local absolute paths, or `data/task_history.json` / `data/task_trash.json`
- EPUB engine tests (`tests/test_epub_*.py`) need no Docling/GPU; keep it that way
- After task-table, drop-zone, or help-dialog changes, run `pytest tests/test_ui_layout_smoke.py tests/test_task_table.py`
- Resume / checkpoint changes: `tests/test_parse_checkpoint.py` `tests/test_resume_detect.py` `tests/test_task_history.py`
- Match existing code style; avoid unrelated refactors
- Update `README.zh-CN.md` / `README.md` / in-app 使用说明 when user-facing behavior changes

## Pull requests

Please include:

- What changed and why
- How you tested (OS / Python / GPU if relevant)
- Screenshots for UI changes when useful

## License

By contributing, you agree that your contributions are licensed under the
Apache License 2.0 (see `LICENSE`).
