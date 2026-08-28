"""v1.5 Figure & Visualization Framework (stdlib SVG/Mermaid pilots)."""

from .manifest import validate_manifest, validate_manifest_file
from .renderer import (
    render_architecture,
    render_exact_function,
    render_network,
    render_numerical,
)

__all__ = [
    "render_architecture",
    "render_exact_function",
    "render_network",
    "render_numerical",
    "validate_manifest",
    "validate_manifest_file",
]
