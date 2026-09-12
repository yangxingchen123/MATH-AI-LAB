from __future__ import annotations

from pathlib import Path

from tests.problem_validator.conftest import problem_md, write_project


def write_ui_project(root: Path) -> Path:
    write_project(root)
    (root / "12_方法库").mkdir(exist_ok=True)
    (root / "00_收件箱").mkdir(exist_ok=True)
    (root / "11_学习证据" / "尝试记录").mkdir(parents=True, exist_ok=True)
    (root / "02_题目库" / "未解决").mkdir(parents=True, exist_ok=True)
    (root / "02_题目库" / "研究中").mkdir(parents=True, exist_ok=True)
    (root / "02_题目库" / "已解决").mkdir(parents=True, exist_ok=True)
    return root


def write_draft_problem(root: Path, pid: str = "P0001") -> Path:
    dest = root / "02_题目库" / "未解决" / f"{pid}.md"
    dest.write_text(problem_md(pid=pid, title="夹具题", status="draft"), encoding="utf-8")
    return dest
