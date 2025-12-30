"""Union Type for Rule Conditions."""

from __future__ import annotations

from core.rules_engine.model.condition import Condition, ConditionSet, NotCondition

Expression = Condition | NotCondition | ConditionSet
