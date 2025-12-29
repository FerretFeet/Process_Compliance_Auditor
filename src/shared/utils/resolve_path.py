from typing import Any


def resolve_path(obj: Any, path: str) -> Any:
    """Resolve a dot-separated path across objects and dicts.

    Raises:
        ValueError: If the path cannot be resolved."""
    if not path:
        raise ValueError("Path cannot be empty")

    current = obj
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                raise ValueError(f"Cannot resolve {path}: missing key '{part}'")
            current = current[part]
        else:
            try:
                current = getattr(current, part)
            except AttributeError as e:
                raise ValueError(f"Cannot resolve {path}: missing attribute '{part}'") from e

    return current
