"""FieldRef class."""

from dataclasses import dataclass
from typing import TypeVar

from shared.utils.resolve_path import resolve_path

T = TypeVar("T")


@dataclass(frozen=True)
class FieldRef[T]:
    """Field Reference in a fact sheet to resolve."""

    path: str
    type: type[T]

    def evaluate(self, facts: dict) -> T | None:
        """
        Resolve the value from facts specified by self.path.

        Args:
            facts (dict): a dict of facts, can traverse nested items with
                dot notation.

        """
        value = resolve_path(facts, self.path)
        if value is None:
            return None
        if not isinstance(value, self.type):
            try:
                value = self.type(value)
            except ValueError as err:
                msg = (
                    f"Expected {self.path} to be {self.type}, got {type(value)}. "
                    "Attempted Cast Failed."
                )
                raise TypeError(msg) from err
        return value
