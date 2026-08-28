"""Load the v1.1 research project contract."""

from __future__ import annotations

from .constants import CONTRACT_VERSION, REQUIRED_DIRS, REQUIRED_FILES, TEMPLATE_ROOT
from .models import ProjectContract


def load_contract() -> ProjectContract:
    return ProjectContract(
        contract_version=CONTRACT_VERSION,
        required_files=REQUIRED_FILES,
        required_dirs=REQUIRED_DIRS,
        template_root=TEMPLATE_ROOT,
    )
