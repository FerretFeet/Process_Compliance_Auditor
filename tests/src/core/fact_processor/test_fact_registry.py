import pytest
from typing import Set

from core.fact_processor.fact_registry import FactRegistry
from core.rules_engine.model.rule import SourceEnum
from shared._common.operators import Operator
from shared._common.facts import FactSpec


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Ensure each test runs with a clean registry.
    """
    FactRegistry._clear()
    yield
    FactRegistry._clear()


class TestFactRegistryRegister:
    def test_register_fact_success(self):
        FactRegistry.register_raw(
            path="cpu.percent",
            type_=int,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.GT, Operator.LT},
            description="CPU usage percentage",
        )

        fact = FactRegistry.get_fact("cpu.percent")

        assert isinstance(fact, FactSpec)
        assert fact.path == "cpu.percent"
        assert fact.type is int
        assert fact.source == [SourceEnum.PROCESS]
        assert fact.allowed_operators == {Operator.GT, Operator.LT}
        assert fact.description == "CPU usage percentage"

    def test_register_duplicate_fact_raises(self):
        FactRegistry.register_raw(
            path="process.pid",
            type_=int,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.EQ},
        )

        with pytest.raises(ValueError, match="already registered"):
            FactRegistry.register_raw(
                path="process.pid",
                type_=int,
                source=[SourceEnum.PROCESS],
                allowed_operators={Operator.EQ},
            )


class TestFactRegistryGet:
    def test_get_fact_success(self):
        FactRegistry.register_raw(
            path="user.name",
            type_=str,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.EQ},
        )

        fact = FactRegistry.get_fact("user.name")
        assert fact.path == "user.name"

    def test_get_fact_missing_raises(self):
        with pytest.raises(KeyError, match="not registered"):
            FactRegistry.get_fact("missing.fact")


class TestFactRegistryAllFacts:
    def test_all_facts_returns_copy(self):
        FactRegistry.register_raw(
            path="system.uptime",
            type_=int,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.GT},
        )

        facts = FactRegistry.all_facts()

        assert "system.uptime" in facts
        assert isinstance(facts["system.uptime"], FactSpec)

        # ensure it's a copy, not the internal dict
        facts.clear()
        assert "system.uptime" in FactRegistry.all_facts()


class TestFactRegistryValidate:
    def test_validate_correct_type(self):
        FactRegistry.register_raw(
            path="system.load",
            type_=float,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.GT, Operator.LT},
        )

        assert FactRegistry.validate("system.load", 1.5) is True

    def test_validate_none_is_allowed(self):
        FactRegistry.register_raw(
            path="system.hostname",
            type_=str,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.EQ},
        )

        assert FactRegistry.validate("system.hostname", None) is True

    def test_validate_wrong_type_raises(self):
        FactRegistry.register_raw(
            path="process.threads",
            type_=int,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.GT},
        )

        with pytest.raises(TypeError, match="Expected process.threads"):
            FactRegistry.validate("process.threads", "not-an-int")


class TestFactRegistryClear:
    def test_clear_registry(self):
        FactRegistry.register_raw(
            path="system.arch",
            type_=str,
            source=[SourceEnum.PROCESS],
            allowed_operators={Operator.EQ},
        )

        assert FactRegistry.all_facts()

        FactRegistry._clear()

        assert FactRegistry.all_facts() == {}
