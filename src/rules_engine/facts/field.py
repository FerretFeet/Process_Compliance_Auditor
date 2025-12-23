from dataclasses import dataclass



def resolve_path(facts: dict, path: str):
    """Resolve a dot-separated path in nested dictionaries."""
    current = facts
    for part in path.split("."):
        if not isinstance(current, dict):
            raise ValueError(f"Cannot resolve {path}: {part} is not a dict")
        current = current.get(part)
    return current


@dataclass(frozen=True)
class FieldRef:
    """Available model for conditions."""
    path: str
    type: type

    def evaluate(self, facts: dict):
        value = resolve_path(facts, self.path)
        if value is None:
            return None
        if not isinstance(value, self.type):
            try:
                value = self.type(value)
            except ValueError:
                raise TypeError(f"Expected {self.path} to be {self.type}, got {type(value)}.  Attempted Cast Failed.")
        return value
