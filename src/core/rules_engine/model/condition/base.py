"""Condition classes for rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from shared._common.operators import GroupOperator, Operator

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from core.rules_engine.model.condition import Expression
    from core.rules_engine.model.field import FieldRef


@dataclass(frozen=True, slots=True)
class Condition:
    """
    A condition for a rule.

    Field is a reference to a value using dot notation.
    Operator is the operation to perform between field and value (>, <, in, etc.)
    Value is the expected value for the field.
    """

    field: FieldRef
    operator: Operator
    value: Any

    def describe(self) -> str:
        """Create a human readable string describing the condition."""
        return f"{self.field} {self.operator.value} {self.value!r}"


@dataclass(frozen=True, slots=True)
class NotCondition:
    """A condition prepended by a Not clause."""

    condition: Expression

    def describe(self) -> str:
        """Create a human readable string describing the condition."""
        return f"NOT ({self.condition.describe()})"


@dataclass(frozen=True, slots=True)
class ConditionSet:
    """A set of 2 or more conditions."""

    group_operator: GroupOperator
    conditions: tuple[Expression, ...]

    @classmethod
    def all(cls, *conditions: Expression) -> ConditionSet:
        """Combine conditions with All."""
        cls._validate(conditions)
        return cls(GroupOperator.ALL, cls._flatten(GroupOperator.ALL, conditions))

    @classmethod
    def any(cls, *conditions: Expression) -> ConditionSet:
        """Combine conditions with Any."""
        cls._validate(conditions)
        return cls(GroupOperator.ANY, cls._flatten(GroupOperator.ANY, conditions))

    def describe(self) -> str:
        """Human readable string describing the condition set."""
        joiner = " AND " if self.group_operator is GroupOperator.ALL else " OR "
        return "(" + joiner.join(c.describe() for c in self.conditions) + ")"

    @staticmethod
    def _validate(conditions: Sequence[Expression]) -> None:
        """Ensure at least two conditions make up the condition set."""
        if not len(conditions) > 1:
            msg = "ConditionSet requires at least two conditions"
            raise ValueError(msg)

    @staticmethod
    def _flatten(
        operator: GroupOperator,
        conditions: Iterable[Expression],
    ) -> tuple[Expression, ...]:
        """
        Simplify grouped conditions.

        and(1, and(2, 3)) -> and(1, 2, 3)
        """
        flattened = []
        for c in conditions:
            if isinstance(c, ConditionSet) and c.group_operator is operator:
                flattened.extend(c.conditions)
            else:
                flattened.append(c)
        return tuple(flattened)


def _and(self: object, other: Expression) -> ConditionSet:
    """Combine conditions with And."""
    return ConditionSet.all(self, other)


def _or(self: object, other: Expression) -> ConditionSet:
    """Combine conditions with Or."""
    return ConditionSet.any(self, other)


def _invert(self: object) -> NotCondition:
    """
    Invert the condition.

    Not Condition -> Condition
    Condition -> NotCondition
    """
    return NotCondition(self)


for cls in [Condition, ConditionSet, NotCondition]:
    cls.__and__ = _and
    cls.__or__ = _or
    cls.__invert__ = _invert

NotCondition.__invert__ = lambda self: self.condition
