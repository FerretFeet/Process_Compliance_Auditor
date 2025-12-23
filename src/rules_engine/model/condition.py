from dataclasses import dataclass
from typing import Union, Sequence, Iterable, Any

from src.rules_engine.facts.field import FieldRef
from src.rules_engine.model.operators import Operator, GroupOperator


@dataclass(frozen=True, slots=True)
class Condition:
    field: FieldRef
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


Expression = Union[Condition, ConditionSet, NotCondition]
