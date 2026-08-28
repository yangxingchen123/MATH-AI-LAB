"""Invoke `lake build` when the Sidecar exists. Never fail Core by itself."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .constants import LEAN_ROOT


@dataclass(frozen=True)
class BuildResult:
    status: str
    command: list[str]
    log: str
    core_impact: bool = False
    returncode: int | None = None


def elan_bin() -> Path:
    return Path.home() / ".elan" / "bin"


def lake_executable() -> str | None:
    found = shutil.which("lake")
    if found:
        return found
    name = "lake.exe" if os.name == "nt" else "lake"
    candidate = elan_bin() / name
    if candidate.is_file():
        return str(candidate)
    return None


def lake_available() -> bool:
    return lake_executable() is not None


def toolchain_present() -> bool:
    root = Path.home() / ".elan" / "toolchains"
    if not root.is_dir():
        return False
    lean_name = "lean.exe" if os.name == "nt" else "lean"
    for child in root.iterdir():
        if child.is_dir() and (child / "bin" / lean_name).is_file():
            return True
    return False


def _env_with_elan() -> dict[str, str]:
    env = os.environ.copy()
    bin_dir = str(elan_bin())
    path = env.get("PATH", "")
    if bin_dir not in path.split(os.pathsep):
        env["PATH"] = bin_dir + os.pathsep + path
    return env


def _is_toolchain_unavailable(log: str) -> bool:
    markers = (
        "could not download",
        "error during download",
        "no such toolchain",
        "unknown toolchain",
        "failed to install",
        "SSL connect error",
        "toolchain not found",
    )
    lowered = log.lower()
    return any(marker.lower() in lowered for marker in markers)


def run_lake_build(
    project_root: Path | None = None,
    *,
    timeout: int = 600,
    allow_install: bool = False,
) -> BuildResult:
    root = Path(project_root or LEAN_ROOT)
    lake = lake_executable()
    command = ["lake", "build"]
    if lake is None:
        return BuildResult(
            status="DEGRADED",
            command=command,
            log="lake missing; Lean Sidecar unavailable. Ordinary mathematics paths must continue.",
            core_impact=False,
        )
    if not toolchain_present() and not allow_install:
        return BuildResult(
            status="DEGRADED",
            command=command,
            log=(
                "elan is installed (VS Code Lean 4 default: ~/.elan/bin) but no compiler "
                "toolchain is present under ~/.elan/toolchains. doctor/gate skip the download. "
                "Run `python -m tools.lean_formalization build` or `lake build` in 06_LEAN形式化 "
                "to install the version in lean-toolchain. Sidecar must not fail Core."
            ),
            core_impact=False,
        )
    try:
        completed = subprocess.run(
            [lake, "build"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=_env_with_elan(),
        )
    except subprocess.TimeoutExpired as exc:
        log = (exc.stdout or "") + (exc.stderr or "")
        return BuildResult(
            status="CANCELLED",
            command=command,
            log=log or "lake build timed out",
            core_impact=False,
            returncode=None,
        )
    log = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode == 0:
        status = "SUCCEEDED"
    elif _is_toolchain_unavailable(log):
        status = "DEGRADED"
    else:
        status = "FAILED"
    return BuildResult(
        status=status,
        command=command,
        log=log,
        core_impact=False,
        returncode=completed.returncode,
    )
