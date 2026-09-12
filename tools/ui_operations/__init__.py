"""Thin Web → Python operation gateway. Not a second Schema."""

from .constants import CONTRACT_VERSION, OPERATIONS
from .gateway import run_operation
from .models import OperationResult

__all__ = [
    "CONTRACT_VERSION",
    "OPERATIONS",
    "OperationResult",
    "run_operation",
]
