"""Utility function to find project root."""

from pathlib import Path


def find_project_root(start: Path) -> Path:
    """Return project root path."""
    root_markers = [".venv", "src", "pyproject.toml"]
    for marker in root_markers:
        for parent in [start, *start.parents]:
            if (parent / marker).exists():
                return parent
    msg = f"Project root not found, was searching for parent of one of {root_markers}"
    raise RuntimeError(msg)


project_root = find_project_root(Path(__file__))
