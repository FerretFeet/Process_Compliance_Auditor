"""Helper function to resolve a nested dot path in an object."""

from typing import Any


def resolve_path(obj: Any, path: str) -> Any:  # noqa: ANN401
    """
    Resolve a dot-separated path across objects and dicts.

    Args:
        obj (Any): Object with nested dict or additional object attributes.
        path (str): dot seperated path to resolve.

    Returns:
        Any: Value of resolved object nested attribute.

    Raises:
        ValueError: If the path cannot be resolved.

    """
    if not path:
        msg = "Path cannot be empty."
        raise ValueError(msg)

    current = obj
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                msg = f"Cannot resolve {path}: missing key '{part}'."
                raise ValueError(msg)
            current = current[part]
        else:
            try:
                current = getattr(current, part)
            except AttributeError as e:
                msg = f"Cannot resolve {path}: missing attribute '{part}'."
                raise ValueError(msg) from e

    return current
