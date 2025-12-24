import pathlib
from typing import Mapping

import pytest
from unittest.mock import patch, mock_open

from core.rules_engine.model.field import FieldRef
from core.rules_engine.model.condition import Condition
from core.rules_engine.model import Operator
from core.rules_engine.model.rule import Action, Rule
from core.rules_engine.rules_engine import RulesEngine, InvalidRuleFilterException
from shared._common.facts import FactSpecProtocol


class MockFact(FactSpecProtocol):
    def __init__(self, typ, allowed_ops=None, allowed_vals=None):

        self.type = typ
        self.allowed_operators = allowed_ops or []
        self.allowed_values = allowed_vals


@pytest.fixture
def mock_fact_provider():
    def provider() -> Mapping[str, FactSpecProtocol]:
        return {
            "cpu_count": MockFact(int, allowed_ops=["==", ">=", "<="], allowed_vals=None),

        }
    return provider



@pytest.fixture
def sample_rule():
    fake_condition = Condition(FieldRef("cpu_count", int), Operator.EQ, "4")

    return Rule(
        name="cpu_check",
        description="Count cpus",
        condition=fake_condition,  # Condition or ConditionSet
        action=Action(name="block_access", execute=lambda facts: facts.update({"blocked": True})),
        group="cpu"
    )


@pytest.fixture
def toml_data(sample_rule):
    return {
        "rules": [
            {
                "name": sample_rule.name,
                "description": sample_rule.description,
                "group": sample_rule.group,
                "model": sample_rule.condition.describe(),
                "action": lambda facts: facts.update({"access_granted": True})
            }
        ]
    }



def test_builtin_rules_loaded(sample_rule, mock_fact_provider):
    engine = RulesEngine(mock_fact_provider, builtin_rules=[sample_rule], toml_rules_path=pathlib.Path("/dev/null"))
    assert sample_rule.id in engine.rules
    assert engine.rules[sample_rule.id] == sample_rule



def test_toml_rules_loaded(mock_fact_provider):
    toml_content = """
[[rules]]
name = "cpu_check"
description = "Count cpus"
group = "cpu"
model = "cpu_count == 4"
action = "example"
"""

    # Convert to bytes for tomllib.load (binary mode)
    toml_bytes = toml_content.encode("utf-8")

    # mock_open with read_data in binary mode
    m = mock_open(read_data=toml_bytes)
    # Ensure open is in 'rb' mode as expected by RulesEngine
    m.return_value.__enter__.return_value.read = lambda: toml_bytes

    with (patch("pathlib.Path.open", m),
          patch("core.rules_engine.rule_builder.parsers.FactRegistry") as mock_registry
          ):
        mock_registry.get.return_value = mock_fact_provider().get("cpu_count")
        engine = RulesEngine(mock_fact_provider, builtin_rules=[], toml_rules_path=pathlib.Path("/fake/path"))
        loaded_rules = engine.get_rules()

    # Validate that the rule is loaded
    assert len(loaded_rules) == 1
    rule = list(loaded_rules.values())[0]
    assert rule.name == "cpu_check"
    assert rule.description == "Count cpus"
    assert rule.group == "cpu"


def test_filter_rules_by_id_and_name(sample_rule, mock_fact_provider):
    engine = RulesEngine(mock_fact_provider, builtin_rules=[sample_rule], toml_rules_path=pathlib.Path("/dev/null"))

    filtered = engine.match_rules(engine.rules, [sample_rule.id])
    assert sample_rule.id in filtered

    filtered2 = engine.match_rules(engine.rules, [sample_rule.name])
    assert sample_rule.id in filtered2

    with pytest.raises(InvalidRuleFilterException):
        engine.match_rules(engine.rules, ["nonexistent-id"])

    with pytest.raises(InvalidRuleFilterException):
        engine.match_rules(engine.rules, ["nonexistent-name"])


def test_filter_rules_no_filters_returns_all(sample_rule, mock_fact_provider):
    engine = RulesEngine(mock_fact_provider, builtin_rules=[sample_rule], toml_rules_path=pathlib.Path("/dev/null"))
    filtered = engine.match_rules(engine.rules, None)
    assert filtered == engine.rules
