from dataclasses import dataclass

from shared.utils.resolve_path import resolve_path


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
                msg = f"Expected {self.path} to be {self.type}, got {type(value)}.  Attempted Cast Failed."
                raise TypeError(
                    msg,
                )
        return value
