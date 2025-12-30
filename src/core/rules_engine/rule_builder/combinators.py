"""Helper functions for grouping conditions when building rules."""
from core.rules_engine.model.condition import ConditionSet, Expression, NotCondition


def all_of(*conditions: Expression) -> ConditionSet:
    """Create an AND group from multiple conditions."""
    return ConditionSet.all(*conditions)


def any_of(*conditions: Expression) -> ConditionSet:
    """Create an OR group from multiple conditions."""
    return ConditionSet.any(*conditions)


def not_(condition: Expression) -> NotCondition:
    """Return a negative condition."""
    return ~condition
