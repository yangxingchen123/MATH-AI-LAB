"""v2.1 controlled multi-agent research (Candidate outputs only)."""

from .gate import evaluate_gate
from .orchestrator import ROLES, run_task

__all__ = ["ROLES", "evaluate_gate", "run_task"]
