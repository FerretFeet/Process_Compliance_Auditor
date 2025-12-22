"""Builder class for Rule objects.

Usage:

# 1. Simple rule_builder + negation
rule1 = RuleBuilder.define("adult_check", "User must be an adult")\
    .when(~adult)\
    .then(block_access)  # shows basic condition and NotCondition

# 2. Compound and nested conditions
rule2 = RuleBuilder.define("special_access", "Adult users with premium or VIP")\
    .when(all_of(adult, any_of(premium, vip)))\
    .then(grant_access)  # shows and/or chaining and nested groups

# 3. Inline lambda / complex chaining
rule3 = RuleBuilder.define("flagged_or_vip", "Flagged users or VIP in allowed regions")\
    .when(not_(flagged))\
    .or_(all_of(adult, any_of(vip, premium), region_allowed))\
    .then(lambda facts: print(f"Action for {facts['user_id']}"))  # inline action + complex group

"""

from src.rules_engine.rule_builder.condition import Expression
from src.rules_engine.rule_builder.rule import Action, Rule, ActionType


class RuleBuilder:
    """Builder class for Rule objects.

    Usage:
    rule_builder = (
        RuleBuilder()
        .define("adult_rule", "User must be adult")
        .when(condition)
        .and_(condition)
        .or_(condition)
        .then(action)
    )
    """
    def __init__(self):
        self._name = None
        self._description = None
        self._condition = None
        self._action = None
        self._group = None
        self._mutually_exclusive_group = None

    def define(self, name: str, description: str) -> "RuleBuilder":
        self._name = name
        self._description = description
        return self

    def when(self, condition: Expression) -> "RuleBuilder":
        if self._condition is not None:
            raise ValueError("when() already called")
        self._condition = condition
        return self

    def and_(self, condition: Expression) -> "RuleBuilder":
        if self._condition is None:
            raise ValueError("and_() called before when()")
        self._condition = self._condition & condition
        return self

    def or_(self, condition: Expression) -> "RuleBuilder":
        if self._condition is None:
            raise ValueError("or_() called before when()")
        self._condition = self._condition | condition
        return self

    def group(self, name: str) -> "RuleBuilder":
        """Assign the rule to a named group"""
        self._group = name
        return self

    def mutually_exclusive_group(self, name: str) -> "RuleBuilder":
        """Assign the rule to a mutually exclusive group"""
        self._mutually_exclusive_group = name
        return self

    def then(self, action: Action | ActionType) -> Rule:
        if self._condition is None:
            raise ValueError("Rule has no condition")
        if self._name is None:
            raise ValueError("Rule has no name")
        if callable(action):
            action = Action(name='Inline', execute=action)
        return Rule(
            name=self._name,
            description=self._description,
            condition=self._condition,
            action=action,
            group=self._group,
            mutually_exclusive_group=self._mutually_exclusive_group,
        )
