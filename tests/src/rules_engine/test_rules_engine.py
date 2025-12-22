import pathlib
import pytest
from unittest.mock import patch, mock_open, MagicMock

from src.rules_engine.rule_builder.rule import Action, Rule
from src.rules_engine.rules_engine import RulesEngine, InvalidRuleFilterException



@pytest.fixture
def sample_rule():
    return Rule(
        name="adult_check",
        description="Ensure adult users",
        condition=MagicMock(),  # Condition or ConditionSet
        action=Action(name="block_access", execute=lambda facts: facts.update({"blocked": True})),
        group="user"
    )


@pytest.fixture
def toml_data(sample_rule):
    return {
        "rules": [
            {
                "name": sample_rule.name,
                "description": sample_rule.description,
                "group": sample_rule.group,
                "condition": "age >= 18",
                "action": lambda facts: facts.update({"access_granted": True})
            }
        ]
    }



def test_builtin_rules_loaded(sample_rule):
    engine = RulesEngine(builtin_rules=[sample_rule], toml_rules_path=pathlib.Path("/dev/null"))
    assert sample_rule.id in engine.rules
    assert engine.rules[sample_rule.id] == sample_rule



def test_toml_rules_loaded():
    toml_content = """
[[rules]]
name = "adult_check"
description = "Ensure adult users"
group = "user"
condition = "age >= 18"
action = "example"
"""

    # Convert to bytes for tomllib.load (binary mode)
    toml_bytes = toml_content.encode("utf-8")

    # mock_open with read_data in binary mode
    m = mock_open(read_data=toml_bytes)
    # Ensure open is in 'rb' mode as expected by RulesEngine
    m.return_value.__enter__.return_value.read = lambda: toml_bytes

    with patch("pathlib.Path.open", m):
        engine = RulesEngine(builtin_rules=[], toml_rules_path=pathlib.Path("/fake/path"))
        loaded_rules = engine.get_rules()  # explicitly call to bypass caching issues

    # Validate that the rule is loaded
    assert len(loaded_rules) == 1
    rule = list(loaded_rules.values())[0]
    assert rule.name == "adult_check"
    assert rule.description == "Ensure adult users"
    assert rule.group == "user"


def test_filter_rules_by_id_and_name(sample_rule):
    engine = RulesEngine(builtin_rules=[sample_rule], toml_rules_path=pathlib.Path("/dev/null"))

    filtered = engine.filter_rules(engine.rules, [sample_rule.id])
    assert sample_rule.id in filtered

    filtered2 = engine.filter_rules(engine.rules, [sample_rule.name])
    assert sample_rule.id in filtered2

    with pytest.raises(InvalidRuleFilterException):
        engine.filter_rules(engine.rules, ["nonexistent-id"])

    with pytest.raises(InvalidRuleFilterException):
        engine.filter_rules(engine.rules, ["nonexistent-name"])


def test_filter_rules_no_filters_returns_all(sample_rule):
    engine = RulesEngine(builtin_rules=[sample_rule], toml_rules_path=pathlib.Path("/dev/null"))
    filtered = engine.filter_rules(engine.rules, None)
    assert filtered == engine.rules
