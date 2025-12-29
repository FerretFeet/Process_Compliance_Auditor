import pytest

from core.rules_engine.rule_builder.combinators import all_of, any_of
from core.rules_engine.model.condition import Condition, ConditionSet, NotCondition
from core.rules_engine.model import Operator, GroupOperator


class TestConditionBase:
    def setup_method(self):
        self.cond_eq = Condition("age", Operator.EQ, "30")
        self.cond_gt = Condition("score", Operator.GT, "100")

    def test_describe(self):
        assert self.cond_eq.describe() == "age == '30'"
        assert self.cond_gt.describe() == "score > '100'"

    def test_and_or_operators_return_conditionset(self):
        combined_and = self.cond_eq & self.cond_gt
        combined_or = self.cond_eq | self.cond_gt
        assert isinstance(combined_and, ConditionSet)
        assert combined_and.group_operator == GroupOperator.ALL
        assert isinstance(combined_or, ConditionSet)
        assert combined_or.group_operator == GroupOperator.ANY


class TestConditionSet(TestConditionBase):

    def setup_method(self):
        super().setup_method()
        self.cond1 = Condition("x", Operator.LT, "5")
        self.cond2 = Condition("y", Operator.GTE, "10")
        self.cond3 = Condition("z", Operator.NE, "0")

    def test_all_factory(self):
        cs = ConditionSet.all(self.cond1, self.cond2)
        assert isinstance(cs, ConditionSet)
        assert cs.group_operator == GroupOperator.ALL
        assert cs.conditions == (self.cond1, self.cond2)

    def test_any_factory(self):
        cs = ConditionSet.any(self.cond1, self.cond2)
        assert isinstance(cs, ConditionSet)
        assert cs.group_operator == GroupOperator.ANY
        assert cs.conditions == (self.cond1, self.cond2)

    def test_and_or_methods_flatten_nested_sets(self):
        nested1 = ConditionSet.all(self.cond1, self.cond2)
        nested2 = ConditionSet.all(nested1, self.cond3)
        assert nested2.conditions == (self.cond1, self.cond2, self.cond3)

        nested_or = ConditionSet.any(self.cond1, ConditionSet.any(self.cond2, self.cond3))
        assert nested_or.conditions == (self.cond1, self.cond2, self.cond3)

    def test_describe_and_or(self):
        cs_all = ConditionSet.all(self.cond1, self.cond2)
        cs_any = ConditionSet.any(self.cond1, self.cond2)
        assert cs_all.describe() == "(x < '5' AND y >= '10')"
        assert cs_any.describe() == "(x < '5' OR y >= '10')"

    def test_validation_raises(self):
        with pytest.raises(ValueError):
            ConditionSet.all(self.cond1)  # less than 2 conditions
        with pytest.raises(ValueError):
            ConditionSet.any(self.cond1)

    def test_all_of_any_of_helpers(self):
        cs_all = all_of(self.cond1, self.cond2)
        cs_any = any_of(self.cond1, self.cond2)
        assert isinstance(cs_all, ConditionSet)
        assert cs_all.group_operator == GroupOperator.ALL
        assert isinstance(cs_any, ConditionSet)
        assert cs_any.group_operator == GroupOperator.ANY


class TestNotCondition:

    def setup_method(self):
        self.adult = Condition("age", Operator.GTE, "18")
        self.vip = Condition("membership", Operator.EQ, "vip")
        self.premium = Condition("membership", Operator.EQ, "premium")

    def test_simple_not_condition(self):
        not_adult = NotCondition(self.adult)
        assert isinstance(not_adult, NotCondition)
        assert not_adult.condition == self.adult
        assert not_adult.describe() == f"NOT ({self.adult.describe()})"

    def test_invert_operator_on_condition(self):
        not_adult = ~self.adult
        assert isinstance(not_adult, NotCondition)
        assert not_adult.condition == self.adult

    def test_not_condition_with_condition_set(self):
        cs = all_of(self.adult, self.vip)
        not_cs = NotCondition(cs)
        assert isinstance(not_cs, NotCondition)
        assert not_cs.describe() == f"NOT ({cs.describe()})"

    def test_invert_operator_on_condition_set(self):
        cs = any_of(self.vip, self.premium)
        not_cs = ~cs
        assert isinstance(not_cs, NotCondition)
        assert not_cs.condition == cs

    def test_double_negation_works(self):
        adult = Condition("age", Operator.GTE, "18")

        not_adult = ~adult
        double_not = ~not_adult  # should automatically simplify

        assert isinstance(double_not, Condition)
        assert double_not == adult
        assert double_not.describe() == adult.describe()
