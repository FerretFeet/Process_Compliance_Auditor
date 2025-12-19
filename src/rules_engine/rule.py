"""A Compliance Rule Object.

Contains:
    id,
    name: identifying string
    message: Message to print on failure
    info: Optional additional information

"""
import operator
from dataclasses import dataclass, field
from typing import Optional, Callable

from src.custom_exceptions.custom_exception import InvalidRuleDataError


@dataclass
class Rule:
    id: int
    name: str
    message: str
    info: str
    evaluator: Optional[Callable] = field(default=None)

    def parse_condition(self) -> Optional[Callable[[dict], bool]]:
        """
           Parse a simple string condition like "cpu_percent < 80", "status == "running"" into a function.
           Returns None if parsing fails.
           """
        info = self.info
        OPS = {
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "==": operator.eq,
            "!=": operator.ne
        }


        try:
            field, op_str, value = info.strip().split()
            op = OPS[op_str]
            # Try int first, fallback to float
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    value = str(value)
            return lambda facts: (
                op(facts.get(field, value), value) if facts.get(field) is not None else False
            )
        except Exception:
            return None

    def to_toml(self):
        pass
    @classmethod
    def from_toml(cls, data: dict) -> "Rule":
        """
        Create a Rule object from a TOML dictionary.

        Raises:
            InvalidRuleDataError: If required fields are missing or invalid.
        """
        try:
            rule_id = data["id"]
            name = data["name"]
            message = data["message"]
            info = data.get("info")  # Optional
        except KeyError as e:
            raise InvalidRuleDataError(f"Missing required field: {e}") from e

        if not isinstance(rule_id, int):
            raise InvalidRuleDataError(f"Rule 'id' must be int, got {type(rule_id).__name__}")
        if not isinstance(name, str):
            raise InvalidRuleDataError(f"Rule 'name' must be str, got {type(name).__name__}")
        if not isinstance(message, str):
            raise InvalidRuleDataError(f"Rule 'message' must be str, got {type(message).__name__}")
        if info is not None and not isinstance(info, str):
            raise InvalidRuleDataError(f"Rule 'info' must be str or None, got {type(info).__name__}")

        return cls(id=rule_id, name=name, message=message, info=info)