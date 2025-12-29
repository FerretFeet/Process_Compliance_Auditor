from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Iterable, Type, Optional, Any

from core.rules_engine.model.condition import Expression
from core.rules_engine.model.field import FieldRef
from shared._common.operators import Operator, GroupOperator


@dataclass(frozen=True, slots=True)
class Condition:
    field: FieldRef
    operator: Operator
    value: Any

    def describe(self) -> str:
        # Use .value to match your test expectation ("==" instead of "Operator.EQ")
        return f"{self.field} {self.operator.value} {self.value!r}"


@dataclass(frozen=True, slots=True)
class NotCondition:
    condition: Expression

    def describe(self) -> str:
        return f"NOT ({self.condition.describe()})"

    def __invert__(self) -> Expression:
        return self.condition


@dataclass(frozen=True, slots=True)
class ConditionSet:
    group_operator: GroupOperator
    conditions: tuple[Expression, ...]

    @classmethod
    def all(cls, *conditions: Expression) -> ConditionSet:
        cls._validate(conditions)
        return cls(GroupOperator.ALL, cls._flatten(GroupOperator.ALL, conditions))

    @classmethod
    def any(cls, *conditions: Expression) -> ConditionSet:
        cls._validate(conditions)
        return cls(GroupOperator.ANY, cls._flatten(GroupOperator.ANY, conditions))

    def describe(self) -> str:
        joiner = " AND " if self.group_operator is GroupOperator.ALL else " OR "
        return "(" + joiner.join(c.describe() for c in self.conditions) + ")"

    @staticmethod
    def _validate(conditions: Sequence[Expression]) -> None:
        if len(conditions) < 2:
            raise ValueError(f"ConditionSet requires at least two conditions")

    @staticmethod
    def _flatten(
        operator: GroupOperator, conditions: Iterable[Expression]
    ) -> tuple[Expression, ...]:
        flattened = []
        for c in conditions:
            if isinstance(c, ConditionSet) and c.group_operator is operator:
                flattened.extend(c.conditions)
            else:
                flattened.append(c)
        return tuple(flattened)


def _and(self, other: Expression) -> ConditionSet:
    return ConditionSet.all(self, other)


def _or(self, other: Expression) -> ConditionSet:
    return ConditionSet.any(self, other)


def _invert(self) -> NotCondition:
    return NotCondition(self)


for cls in [Condition, ConditionSet]:
    cls.__and__ = _and
    cls.__or__ = _or
    cls.__invert__ = _invert

NotCondition.__invert__ = lambda self: self.condition
