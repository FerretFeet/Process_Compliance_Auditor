"""Builder class for Rule objects.

Usage:

# 1. Simple rule_builder + negation
rule1 = RuleBuilder.define("adult_check", "User must be an adult")\
    .when(~adult)\
    .then(block_access)  # shows basic model and NotCondition

# 2. Compound and nested conditions
rule2 = RuleBuilder.define("special_access", "Adult users with premium or VIP")\
    .when(all_of(adult, any_of(premium, vip)))\
    .then(grant_access)  # shows and/or chaining and nested groups

# 3. Inline lambda / complex chaining
rule3 = RuleBuilder.define("flagged_or_vip", "Flagged users or VIP in allowed regions")\
    .when(not_(flagged))\
    .or_(all_of(adult, any_of(vip, cond(premium == 15)), region_allowed))\
    .then(lambda facts: print(f"Action for {facts['user_id']}"))  # inline action + complex group

"""
from typing import Callable

from core.rules_engine.model.condition import Expression
from core.rules_engine.model.rule import Action, Rule, ActionType, SourceEnum
from core.rules_engine.rule_builder.parsers import cond


class RuleBuilder:
    """Builder class for Rule objects.

    Usage:
    rule_builder = (
        RuleBuilder()
        .define("adult_rule", "User must be adult")
        .source('process')
        .when(model)
        .and_(model)
        .or_(model)
        .then(action)
    )
    """
    def __init__(self):
        self._priority = 0
        self._name = None
        self._description = None
        self._condition = None
        self._source = None
        self._action = None
        self._group = None
        self._mutually_exclusive_group = None
        self._enabled = True
        self._metadata = {}

    def define(self, name: str, description: str) -> "RuleBuilder":
        self._name = name
        self._description = description
        return self

    def when(self, condition: Expression) -> "RuleBuilder":
        if self._condition is not None:
            raise ValueError("when() already called")
        if isinstance(condition, str):
            condition = cond(condition)
        self._condition = condition
        return self

    def source(self, source: str) -> "RuleBuilder":
        if isinstance(source, str):
            source = SourceEnum(source)
        if self._source is None:
            self._source = source
        else:
            raise ValueError("source() already called.")
        return self

    def and_(self, condition: Expression) -> "RuleBuilder":
        if self._condition is None:
            raise ValueError("and_() called before when()")
        if isinstance(condition, str):
            condition = cond(condition)
        self._condition = self._condition & condition
        return self

    def or_(self, condition: Expression) -> "RuleBuilder":
        if self._condition is None:
            raise ValueError("or_() called before when()")
        if isinstance(condition, str):
            condition = cond(condition)
        self._condition = self._condition | condition
        return self

    def disable(self) -> "RuleBuilder":
        """Disable rule."""
        self._enabled = False
        return self

    def priority(self, priority: int) -> "RuleBuilder":
        """Assign the priority to rule"""
        self._priority = priority
        return self

    def metadata(self, **kwargs) -> "RuleBuilder":
        """Set arbitrary key/value metadata on the rule."""
        self._metadata.update(kwargs)
        return self

    def set_metadata(self, data: dict) -> "RuleBuilder":
        self._metadata = dict(data)
        return self

    def group(self, name: str) -> "RuleBuilder":
        """Assign the rule to a named group"""
        self._group = name
        return self

    def mutually_exclusive_group(self, name: str) -> "RuleBuilder":
        """Assign the rule to a mutually exclusive group"""
        self._mutually_exclusive_group = name
        return self

    def then(self, action: Callable) -> Rule:
        if self._condition is None:
            raise ValueError("Rule has no model")
        if self._name is None:
            raise ValueError("Rule has no name")
        if callable(action):
            action = Action(name='Inline', execute=action)
        return Rule(
            name=self._name,
            description=self._description,
            condition=self._condition,
            action=action,
            source=self._source,
            group=self._group,
            mutually_exclusive_group=self._mutually_exclusive_group,
            enabled=self._enabled,
            priority=self._priority,
            metadata=self._metadata
        )
