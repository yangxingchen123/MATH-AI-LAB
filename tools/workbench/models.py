from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BootstrapResult:
    status: str
    message: str
    project: Path | None = None
    code: Path | None = None
    latex: Path | None = None


@dataclass(frozen=True)
class AttachResult:
    status: str
    message: str
    path: Path | None = None
    derived_sha256: str = ""


@dataclass(frozen=True)
class ExperimentResult:
    status: str
    message: str
    run_id: str = ""
    output_dir: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
