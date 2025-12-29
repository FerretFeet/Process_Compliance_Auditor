from dataclasses import MISSING, fields

import pytest

from core.rules_engine.model import GroupOperator, Operator
from core.rules_engine.model.condition import Condition, ConditionSet, NotCondition
from core.rules_engine.model.field import FieldRef
from core.rules_engine.model.rule import Action, Rule
from core.rules_engine.rule_builder.combinators import all_of, any_of, not_
from core.rules_engine.rule_builder.parsers import cond
from core.rules_engine.rule_builder.rule_builder import RuleBuilder


class TestRuleBuilderBase:
    def setup_method(self):
        self.adult = Condition("age", Operator.GTE, "18")
        self.premium = Condition("membership", Operator.EQ, "premium")
        self.vip = Condition("membership", Operator.EQ, "vip")
        self.region_allowed = Condition("region", Operator.IN, "['US', 'EU']")

        self.grant_access = Action("grant_access", lambda : None)
        self.block_access = Action("block_access", lambda : None)


class TestCondParsing(TestRuleBuilderBase):

    def test_cond_parsing_basic(self, fake_fact_registry):
        c = cond("age < 18")
        assert isinstance(c, Condition)
        assert c.field == FieldRef(path="age", type=int)
        assert c.operator == Operator.LT
        assert c.value == 18

    def test_cond_parsing_gte(self, fake_fact_registry):
        c = cond("age >= 100")
        assert c.operator == Operator.GTE
        assert c.value == 100

    def test_inline_nested_condition(self, fake_fact_registry):
        rule = (
            RuleBuilder()
            .define("test", "test_check")
            .when(cond("nested.key > 1"))
            .then(self.grant_access)
        )
        facts = {"nested": {"key": 2}}
        assert isinstance(rule.condition.field, FieldRef)
        assert rule.condition.field.evaluate(facts) == "2"

    def test_cond_parsing_invalid_raises(self):
        with pytest.raises(ValueError):
            cond("invalid expression")


class TestRuleBuilderChaining(TestRuleBuilderBase):

    def test_simple_rule(self):
        rule = (
            RuleBuilder()
            .define("adult_check", "User must be adult")
            .when(self.adult)
            .then(self.block_access)
        )
        assert isinstance(rule, Rule)
        assert rule.name == "adult_check"
        assert rule.condition == self.adult
        facts = {}
        rule.action()

    def test_and_or_chaining(self):
        rule = (
            RuleBuilder()
            .define("special_access", "Adult users with premium or VIP")
            .when(self.adult)
            .and_(self.premium)
            .or_(self.vip)
            .then(self.grant_access)
        )
        assert isinstance(rule.condition, ConditionSet)
        assert rule.condition.group_operator == GroupOperator.ANY
        top_level_conditions = rule.condition.conditions

        nested_all = next(c for c in top_level_conditions if isinstance(c, ConditionSet))
        assert nested_all.group_operator == GroupOperator.ALL
        assert self.adult in nested_all.conditions
        assert self.premium in nested_all.conditions

        top_level_others = [c for c in top_level_conditions if c is not nested_all]
        assert self.vip in top_level_others

    def test_nested_conditions_all_of_any_of(self):
        rule = (
            RuleBuilder()
            .define("nested_rule", "Adult AND (premium OR VIP)")
            .when(all_of(self.adult, any_of(self.premium, self.vip)))
            .then(self.grant_access)
        )
        assert isinstance(rule.condition, ConditionSet)
        assert (
            rule.condition.group_operator
            == ConditionSet.all(self.adult, any_of(self.premium, self.vip)).group_operator
        )
        facts = {}
        rule.action()

    def test_inline_lambda_action(self):
        captured = {}

        rule = (
            RuleBuilder()
            .define("flagged_user", "Inline lambda")
            .when(self.adult)
            .then(lambda : captured.update({"executed": True}))
        )
        assert isinstance(rule.action, Action)
        facts = {}
        rule.action()
        assert captured.get("executed") is True

    def test_multiple_chaining_with_any_of(self):
        rule = (
            RuleBuilder()
            .define("vip_region_access", "Adult VIP/Premium in allowed regions")
            .when(self.adult)
            .and_(any_of(self.vip, self.premium))
            .and_(self.region_allowed)
            .then(self.grant_access)
        )
        assert rule.condition.group_operator == GroupOperator.ALL

        flat_conditions = rule.condition.conditions
        assert self.adult in flat_conditions
        assert self.region_allowed in flat_conditions

        nested_any = next(c for c in flat_conditions if isinstance(c, ConditionSet))
        assert nested_any.group_operator == GroupOperator.ANY
        assert self.vip in nested_any.conditions
        assert self.premium in nested_any.conditions

    def test_errors_for_invalid_chaining(self):
        builder = RuleBuilder().define("name", "desc")
        with pytest.raises(ValueError):
            builder.and_(self.adult)
        with pytest.raises(ValueError):
            builder.or_(self.adult)
        with pytest.raises(ValueError):
            RuleBuilder().then(self.grant_access)  # no model

    def test_when_called_twice_raises(self):
        builder = RuleBuilder().define("name", "desc").when(self.adult)
        with pytest.raises(ValueError):
            builder.when(self.premium)

    def test_not_condition_in_rulebuilder(self):
        """Ensure that RuleBuilder can accept NotCondition via not_() helper."""
        rule = (
            RuleBuilder()
            .define("negate_age", "User must NOT be adult")
            .when(not_(self.adult))
            .then(self.grant_access)
        )

        # The model should be a NotCondition wrapping the original Condition
        from core.rules_engine.model.condition import Condition, NotCondition

        assert isinstance(rule.condition, NotCondition)
        assert isinstance(rule.condition.condition, Condition)
        assert rule.condition.condition == self.adult

        # Description should reflect the negation
        assert rule.condition.describe() == f"NOT ({self.adult.describe()})"

    def test_complex_not_chaining(self):
        """Test RuleBuilder with complex combinations of NotCondition, AND/OR, and nested groups."""
        rule = (
            RuleBuilder()
            .define("complex_not_rule", "Adult NOT VIP in allowed regions")
            .when(self.adult)
            .and_(not_(self.vip))
            .and_(self.region_allowed)
            .then(self.grant_access)
        )

        # Top-level model should be a ConditionSet with ALL
        assert isinstance(rule.condition, ConditionSet)
        assert rule.condition.group_operator.name == "ALL"

        flat_conditions = rule.condition.conditions

        # Should contain the original adult Condition
        assert self.adult in flat_conditions

        # Should contain the region_allowed Condition
        assert self.region_allowed in flat_conditions

        # Should contain a NotCondition wrapping vip
        not_conditions = [c for c in flat_conditions if isinstance(c, NotCondition)]
        assert len(not_conditions) == 1
        assert not_conditions[0].condition == self.vip

        # Description should reflect the NOT
        expected_describe = f"({self.adult.describe()} AND NOT ({self.vip.describe()}) AND {self.region_allowed.describe()})"
        assert rule.condition.describe() == expected_describe


# Dummy model and action for testing
adult = Condition("age", Operator.GTE, "18")
grant_access = Action(name="grant", execute=lambda : None)


class TestRuleBuilderGroups:
    def test_group_assignment(self):
        rule = (
            RuleBuilder()
            .define("test_rule_group", "Testing group")
            .when(adult)
            .group("membership")
            .then(grant_access)
        )
        assert rule.group == "membership"
        assert rule.mutually_exclusive_group is None

    def test_mutually_exclusive_group_assignment(self):
        rule = (
            RuleBuilder()
            .define("test_rule_me_group", "Testing mutually exclusive group")
            .when(adult)
            .mutually_exclusive_group("access_level")
            .then(grant_access)
        )
        assert rule.group is None
        assert rule.mutually_exclusive_group == "access_level"

    def test_group_and_mutually_exclusive_group_assignment(self):
        rule = (
            RuleBuilder()
            .define("test_rule_both", "Testing both group attributes")
            .when(adult)
            .group("membership")
            .mutually_exclusive_group("access_level")
            .then(grant_access)
        )
        assert rule.group == "membership"
        assert rule.mutually_exclusive_group == "access_level"


# Dummy objects for testing
adult = Condition("age", Operator.GTE, "18")
grant_access = Action(name="grant", execute=lambda : None)


class TestRuleBuilderAllAttributesDynamic:
    def test_all_rule_fields_exposed_in_builder(self):
        """
        Ensure all Rule attributes (except explicitly ignored) are set via the builder.
        Fails if a model is None or left at its default value.
        """
        ignored_fields = ["id"]

        rule = (
            RuleBuilder()
            .define("test_rule_dynamic", "Testing full attribute coverage")
            .source("process")
            .when(adult)
            .group("membership")
            .mutually_exclusive_group("access_level")
            .disable()
            .priority(4)
            .set_metadata({"ex": "val"})
            .then(grant_access)
        )

        for field_info in fields(Rule):
            if field_info.name in ignored_fields:
                continue  # skip ignored attributes

            value = getattr(rule, field_info.name)

            # Determine default for the model
            if field_info.default is not MISSING:
                default_value = field_info.default
            elif field_info.default_factory is not MISSING:
                default_value = field_info.default_factory()
            else:
                default_value = None  # no default

            # Fail if value is None or equal to default
            assert value is not None and value != default_value, (
                f"Rule model '{field_info.name}' is not set via builder: "
                f"value is {value}, default is {default_value}"
            )
