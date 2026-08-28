"""v1.6 Lean Formalization Framework (lake optional)."""

from .build import lake_available, run_lake_build
from .correspondence import load_table, undeclared_theorems, validate_table
from .doctor import doctor
from .scan import scan_lean_text, scan_lean_tree

__all__ = [
    "doctor",
    "lake_available",
    "load_table",
    "run_lake_build",
    "scan_lean_text",
    "scan_lean_tree",
    "undeclared_theorems",
    "validate_table",
]
