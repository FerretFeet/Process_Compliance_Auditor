import re
from dataclasses import dataclass
from enum import Enum
from typing import Union, Sequence, Iterable


class Operator(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    IN = "in"

@dataclass(frozen=True, slots=True)
class Condition:
    field: str
    operator: Operator
    value: str

    def __and__(self, other: "Expression") -> "ConditionSet":
        return ConditionSet.all(self, other)

    def __or__(self, other: "Expression") -> "ConditionSet":
        return ConditionSet.any(self, other)

    def describe(self) -> str:
        return f"{self.field} {self.operator.value} {self.value!r}"

    def __invert__(self) -> "NotCondition":
        return NotCondition(self)


@dataclass(frozen=True, slots=True)
class NotCondition:
    condition: Expression

    def describe(self) -> str:
        return f"NOT ({self.condition.describe()})"

    def __invert__(self):
        return self.condition




class GroupOperator(Enum):
    ALL = "all"
    ANY = "any"

Expression = Union[Condition, "ConditionSet", NotCondition]

@dataclass(frozen=True, slots=True)
class ConditionSet:
    """Create a set of conditions

    Usage:
        example = ConditionSet."""
    group_operator: GroupOperator
    conditions: tuple[Expression, ...]

    @classmethod
    def all(cls, *conditions: Expression) -> "ConditionSet":
        cls._validate(conditions)
        return cls(GroupOperator.ALL, cls._flatten(GroupOperator.ALL, conditions))

    @classmethod
    def any(cls, *conditions: Expression) -> "ConditionSet":
        cls._validate(conditions)
        return cls(GroupOperator.ANY, cls._flatten(GroupOperator.ANY, conditions))

    def __and__(self, other: Expression) -> "ConditionSet":
        return ConditionSet.all(self, other)

    def __or__(self, other: Expression) -> "ConditionSet":
        return ConditionSet.any(self, other)

    def describe(self) -> str:
        joiner = " AND " if self.group_operator is GroupOperator.ALL else " OR "
        return "(" + joiner.join(c.describe() for c in self.conditions) + ")"

    @staticmethod
    def _validate(conditions: Sequence[Expression]) -> None:
        if len(conditions) < 2:
            raise ValueError(f"ConditionSet requires at least two conditions: got {conditions}")

    @staticmethod
    def _flatten(
        operator: GroupOperator,
        conditions: Iterable[Expression],
    ) -> tuple[Expression, ...]:
        flattened = []
        for c in conditions:
            if isinstance(c, ConditionSet) and c.group_operator is operator:
                flattened.extend(c.conditions)
            else:
                flattened.append(c)
        return tuple(flattened)

    def __invert__(self) -> "NotCondition":
        return NotCondition(self)


def all_of(*conditions: Expression) -> ConditionSet:
    """Create an AND group from multiple conditions"""
    return ConditionSet.all(*conditions)

def any_of(*conditions: Expression) -> ConditionSet:
    """Create an OR group from multiple conditions"""
    return ConditionSet.any(*conditions)


def cond(expr: str) -> Condition:
    """
    Parse a string like "age < 18" into a Condition object
    using Operator enum values.
    """
    expr = expr.strip()
    # Sort by descending length to handle <=, >= before <, >
    sorted_ops = sorted(Operator, key=lambda op: -len(op.value))

    for op_enum in sorted_ops:
        pattern = rf"\s{re.escape(op_enum.value)}\s"
        match = re.search(pattern, f" {expr} ")
        if match:
            # Split on the operator
            field, value = map(str.strip, re.split(pattern, expr, maxsplit=1))
            return Condition(field=field, operator=op_enum, value=value)

    raise ValueError(f"Could not parse condition: {expr}")


def not_(condition: Expression) -> NotCondition:
    return ~condition
