import pathlib
from typing import TYPE_CHECKING
from unittest.mock import mock_open, patch

import pytest

from core.fact_processor.fact_registry import FactRegistry
from core.rules_engine.model import Operator
from core.rules_engine.model.rule import SourceEnum
from core.rules_engine.rules_engine import InvalidRuleFilterError, RulesEngine
from shared._common.facts import FactSpecProtocol
from shared.utils import cfg, project_root

if TYPE_CHECKING:
    from collections.abc import Mapping

FactRegistry.register_raw(
    "cpu_check",
    str,
    SourceEnum.PROCESS,
    set(Operator),
)


class MockFact(FactSpecProtocol):
    def __init__(self, typ, allowed_ops=None, allowed_vals=None):

        self.type = typ
        self.allowed_operators = allowed_ops or []
        self.allowed_values = allowed_vals


@pytest.fixture
def mock_fact_provider(fake_fact_registry):
    def provider() -> Mapping[str, FactSpecProtocol]:
        return FactRegistry.all_facts()

    return provider


def test_builtin_rules_loaded(sample_rule, mock_fact_provider):
    engine = RulesEngine(
        mock_fact_provider,
        builtin_rules=[sample_rule],
        toml_rules_path=pathlib.Path("/dev/null"),
    )
    assert sample_rule.id in engine.rules
    assert engine.rules[sample_rule.id] == sample_rule


def test_toml_rules_loaded(mock_fact_provider, fake_fact_registry):
    toml_content = """
[[rules]]
name = "cpu_check"
description = "Count cpus"
group = "cpu"
model = "cpu_count == 4:int"
action = "example"
source = "process"

"""

    # Convert to bytes for tomllib.load (binary mode)
    toml_bytes = toml_content.encode("utf-8")

    # mock_open with read_data in binary mode
    m = mock_open(read_data=toml_bytes)
    # Ensure open is in 'rb' mode as expected by RulesEngine
    m.return_value.__enter__.return_value.read = lambda: toml_bytes
    _path = project_root / cfg.get("rules_path")

    with (patch("pathlib.Path.open", m),):
        engine = RulesEngine(mock_fact_provider, builtin_rules=[], toml_rules_path=_path)
        loaded_rules = engine.get_rules()

    # Validate that the rule is loaded
    assert len(loaded_rules) == 1
    rule = next(iter(loaded_rules.values()))
    assert rule.name == "cpu_check"
    assert rule.description == "Count cpus"
    assert rule.group == "cpu"


def test_filter_rules_by_id_and_name(sample_rule, mock_fact_provider):
    engine = RulesEngine(
        mock_fact_provider,
        builtin_rules=[sample_rule],
        toml_rules_path=pathlib.Path("/dev/null"),
    )

    filtered = engine.match_rules(engine.rules, [sample_rule.id])
    assert sample_rule.id in filtered

    filtered2 = engine.match_rules(engine.rules, [sample_rule.name])
    assert sample_rule.id in filtered2

    with pytest.raises(InvalidRuleFilterError):
        engine.match_rules(engine.rules, ["nonexistent-id"])

    with pytest.raises(InvalidRuleFilterError):
        engine.match_rules(engine.rules, ["nonexistent-name"])


def test_filter_rules_no_filters_returns_all(sample_rule, mock_fact_provider):
    engine = RulesEngine(
        mock_fact_provider,
        builtin_rules=[sample_rule],
        toml_rules_path=pathlib.Path("/dev/null"),
    )
    filtered = engine.match_rules(engine.rules, None)
    assert filtered == engine.rules
