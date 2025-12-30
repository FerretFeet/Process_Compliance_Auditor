"""
Builder class for Rule objects.

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

from typing import TYPE_CHECKING

from core.rules_engine.model.rule import Action, Rule, SourceEnum
from core.rules_engine.rule_builder.parsers import cond

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.rules_engine.model.condition import Expression


class RuleBuilder:
    """
    Builder class for Rule objects.

    Usage:
    rule_builder = (
        RuleBuilder()
        .define("adult_rule", "User must be adult")
        .from('process')
        .when(model)
        .and_(model)
        .or_(model)
        .then(action)
    )
    """

    def __init__(self) -> None:
        """Prepare state data containers."""
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

    def define(self, name: str, description: str) -> RuleBuilder:
        """Set the name and description of the rule."""
        self._name = name
        self._description = description
        return self

    def when(self, condition: Expression) -> RuleBuilder:
        """Begin defining the condition for the rule."""
        if self._condition is not None:
            msg = "when() already called"
            raise ValueError(msg)
        if isinstance(condition, str):
            condition = cond(condition)
        self._condition = condition
        return self

    def from_(self, source: str) -> RuleBuilder:
        """
        Define the source the rule will apply to.

        Raises:
            ValueError: If it has already been defined.

        """
        if isinstance(source, str):
            source = SourceEnum(source)
        if self._source is None:
            self._source = source
        else:
            msg = "source() already called."
            raise ValueError(msg)
        return self

    def and_(self, condition: Expression) -> RuleBuilder:
        """
        Connect the previous condition to this condition with And.

        Raises:
            ValueError: if not called with enough conditions.

        """
        if self._condition is None:
            msg = "and_() called before when()"
            raise ValueError(msg)
        if isinstance(condition, str):
            condition = cond(condition)
        self._condition = self._condition & condition
        return self

    def or_(self, condition: Expression) -> RuleBuilder:
        """
        Connect the previous condition to this condition with Or.

        Raises:
            ValueError: if not called with enough conditions.

        """
        if self._condition is None:
            msg = "or_() called before when()"
            raise ValueError(msg)
        if isinstance(condition, str):
            condition = cond(condition)
        self._condition = self._condition | condition
        return self

    def disable(self) -> RuleBuilder:
        """Disable rule."""
        self._enabled = False
        return self

    def priority(self, priority: int) -> RuleBuilder:
        """Assign the priority to rule."""
        self._priority = priority
        return self

    def metadata(self, **kwargs: str) -> RuleBuilder:
        """Set arbitrary key/value metadata on the rule."""
        self._metadata.update(kwargs)
        return self

    def set_metadata(self, data: dict) -> RuleBuilder:
        """Set rule metadata."""
        self._metadata = dict(data)
        return self

    def group(self, name: str) -> RuleBuilder:
        """Assign the rule to a named group."""
        self._group = name
        return self

    def mutually_exclusive_group(self, name: str) -> RuleBuilder:
        """Assign the rule to a mutually exclusive group."""
        self._mutually_exclusive_group = name
        return self

    def then(self, action: Callable) -> Rule:
        """
        Define the action to be executed when the rule is untrue, create the rule.

        Raises:
            ValueError: if rule is missing necessary assignments.

        """
        if self._condition is None:
            msg = "Rule has no model"
            raise ValueError(msg)
        if self._name is None:
            msg = "Rule has no name"
            raise ValueError(msg)
        if self._source is None:
            msg = "Rule has no source"
            raise ValueError(msg)
        if callable(action):
            action = Action(name="Inline", execute=action)
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
            metadata=self._metadata,
        )
