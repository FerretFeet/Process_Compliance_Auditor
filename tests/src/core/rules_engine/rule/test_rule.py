
import pytest

from core.rules_engine.model.field import FieldRef
from core.rules_engine.model.rule import Action, Rule
from core.rules_engine.model.condition import Condition, ConditionSet
from core.rules_engine.model import Operator, GroupOperator


class TestActionBase:
    def setup_method(self):
        self.called = False

        def sample_execute(facts):
            self.called = True
            facts["executed"] = True

        self.action = Action(
            name="SampleAction",
            execute=sample_execute,
            description="A test action"
        )
        self.facts = {}

    def test_action_attributes(self):
        assert self.action.name == "SampleAction"
        assert self.action.description == "A test action"
        assert callable(self.action.execute)

    def test_call_executes_function(self):
        self.action(self.facts)
        assert self.called is True
        assert self.facts.get("executed") is True


class TestRule(TestActionBase):

    def setup_method(self):
        super().setup_method()
        self.cond1 = Condition("x", Operator.EQ, "10")
        self.cond2 = Condition("y", Operator.GT, "5")
        self.condition_set = ConditionSet.all(self.cond1, self.cond2)

        self.rule = Rule(
            name="TestRule",
            description="A sample rule_builder",
            condition=self.condition_set,
            action=self.action
        )

    def test_rule_attributes(self):
        assert self.rule.id == "RUL-007195", "Rule id is not equal to RUL-007195, Hash function has changed."
        assert self.rule.description == "A sample rule_builder"
        assert self.rule.name == "TestRule"
        assert self.rule.description == "A sample rule_builder"
        assert self.rule.condition == self.condition_set
        assert self.rule.action == self.action

    def test_rule_action_execution(self):
        self.rule.action(self.facts)
        assert self.called is True
        assert self.facts.get("executed") is True

    def test_rule_with_nested_condition_sets(self):
        nested_cond = ConditionSet.all(self.condition_set, Condition("z", Operator.NE, "0"))
        rule_nested = Rule(
            name="NestedRule",
            description="Rule with nested model sets",
            condition=nested_cond,
            action=self.action
        )
        assert isinstance(rule_nested.condition, ConditionSet)
        assert len(rule_nested.condition.conditions) == 3

    def test_from_toml_simple(self):
        toml_data = {
            "name": "adult_check",
            "description": "User must be an adult",
            "group": "builtin",
            "model": "age >= 18",
            "action": "Block access"
        }

        rule = Rule.from_toml(toml_data)

        # Basic attributes
        assert rule.name == "adult_check"
        assert rule.description == "User must be an adult"
        assert rule.group == "builtin"
        assert isinstance(rule.condition, Condition)
        assert isinstance(rule.action, Action)
        assert callable(rule.action.execute)

        # ID is deterministic and matches expected pattern
        assert rule.id.startswith("BUI-")
        assert len(rule.id) == 10  # 3-char prefix + '-' + 6 digits

    def test_from_toml_nested_conditions(self):
        toml_data = {
            "name": "special_access",
            "description": "Adult users with premium or VIP",
            "group": "user",
            "model": {
                "operator": "all",
                "conditions": [
                    "age >= 18",
                    {
                        "operator": "any",
                        "conditions": [
                            "membership == 'premium'",
                            "membership == 'vip'"
                        ]
                    }
                ]
            },
            "action": lambda facts: facts.update({"access_granted": True})
        }

        rule = Rule.from_toml(toml_data)

        # Top-level attributes
        assert rule.name == "special_access"
        assert rule.description == "Adult users with premium or VIP"
        assert rule.group == "user"
        assert callable(rule.action.execute)

        # Top-level model
        assert isinstance(rule.condition, ConditionSet)
        assert rule.condition.group_operator == GroupOperator.ALL

        # Flattened children
        children = rule.condition.conditions
        assert isinstance(children[0], Condition)
        assert children[0].field == FieldRef(path="age", type=str)
        assert children[0].operator == Operator.GTE
        assert children[0].value == "18"

        # Nested ANY group
        nested = children[1]
        assert isinstance(nested, ConditionSet)
        assert nested.group_operator == GroupOperator.ANY
        nested_fields = {c.field for c in nested.conditions}
        assert nested_fields == {FieldRef(path="membership", type=str)}
        nested_values = {c.value for c in nested.conditions}
        assert nested_values == {"'premium'", "'vip'"}

    def test_from_toml_invalid_condition_raises(self):
        toml_data = {
            "name": "invalid_rule",
            "description": "Missing model",
            "group": "user",
            # model is missing
            "action": "Log something"
        }

        with pytest.raises(Exception):
            Rule.from_toml(toml_data)
