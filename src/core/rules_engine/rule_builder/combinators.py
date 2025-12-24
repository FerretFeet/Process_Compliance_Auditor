from core.rules_engine.model.condition import Expression, ConditionSet, NotCondition


def all_of(*conditions: Expression) -> ConditionSet:
    """Create an AND group from multiple conditions"""
    return ConditionSet.all(*conditions)


def any_of(*conditions: Expression) -> ConditionSet:
    """Create an OR group from multiple conditions"""
    return ConditionSet.any(*conditions)


def not_(condition: Expression) -> NotCondition:
    return ~condition
