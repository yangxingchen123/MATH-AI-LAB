"""Problem Candidate Gate v0.1 — temporary pre-freeze quality gate."""

from .constants import GATE_VERSION
from .discovery import DiscoveryError, resolve_project_root
from .models import GateIssue, GateResult, GateSummary
from .readiness import check_file, check_project, status_project

__all__ = [
    "GATE_VERSION",
    "DiscoveryError",
    "GateIssue",
    "GateResult",
    "GateSummary",
    "check_file",
    "check_project",
    "resolve_project_root",
    "status_project",
]
__version__ = GATE_VERSION
