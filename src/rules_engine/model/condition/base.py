from __future__ import annotations

from dataclasses import dataclass

from _common.operators import Operator
from rules_engine.model.field import FieldRef


@dataclass(frozen=True, slots=True)
class Condition:
    field: FieldRef
    operator: Operator
    value: str

    def __and__(self, other: "Expression") -> "ConditionSet":
        from .condition import ConditionSet
        return ConditionSet.all(self, other)

    def __or__(self, other: "Expression") -> "ConditionSet":
        from .condition import ConditionSet
        return ConditionSet.any(self, other)

    def describe(self) -> str:
        return f"{self.field} {self.operator.value} {self.value!r}"

    def __invert__(self) -> "NotCondition":
        from .condition import NotCondition
        return NotCondition(self)
