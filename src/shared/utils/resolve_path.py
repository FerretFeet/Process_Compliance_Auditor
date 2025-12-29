from typing import Any


def resolve_path(obj: Any, path: str) -> Any:
    """
    Resolve a dot-separated path across objects and dicts.

    Raises:
        ValueError: If the path cannot be resolved.

    """
    if not path:
        msg = "Path cannot be empty"
        raise ValueError(msg)

    current = obj
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                msg = f"Cannot resolve {path}: missing key '{part}'"
                raise ValueError(msg)
            current = current[part]
        else:
            try:
                current = getattr(current, part)
            except AttributeError as e:
                msg = f"Cannot resolve {path}: missing attribute '{part}'"
                raise ValueError(msg) from e

    return current
