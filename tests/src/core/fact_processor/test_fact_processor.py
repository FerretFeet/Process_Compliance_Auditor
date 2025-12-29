import pytest
from unittest.mock import MagicMock

from core.fact_processor.fact_processor import FactProcessor
from shared.custom_exceptions import FactNotFoundException
from core.rules_engine.model.rule import SourceEnum


@pytest.fixture
def processor(fake_fact_registry):
    """
    FactProcessor with registry populated via fake_fact_registry.
    """
    return FactProcessor()


class TestGetAllFacts:
    def test_get_all_facts_cached(self, processor):
        facts1 = processor.get_all_facts()
        facts2 = processor.get_all_facts()

        assert facts1 is facts2


class TestGetFactsBySource:
    def test_get_facts_by_source(self, processor):
        processor.get_all_facts()  # ensure cache populated

        facts = processor.get_facts_by_source(SourceEnum.PROCESS.value)

        assert set(facts.keys()) == {
            "age",
            "membership",
            "nested.key",
            "cpu_count",
        }

    def test_get_facts_by_sources_filters_empty(self, processor):
        processor.get_all_facts()

        result = processor.get_facts_by_sources([SourceEnum.PROCESS.value, "missing"])

        assert SourceEnum.PROCESS.value in result
        assert "missing" not in result


class TestParseFacts:
    def test_parse_facts_success(self, processor, monkeypatch):
        processor.get_all_facts()

        snapshots = {
            SourceEnum.PROCESS.value: [
                {
                    "age": 30,
                    "membership": "gold",
                    "nested": {"key": "value"},
                    "cpu_count": 8,
                }
            ]
        }

        result = processor.parse_facts(snapshots)

        assert result[SourceEnum.PROCESS.value]["age"] == 30
        assert result[SourceEnum.PROCESS.value]["membership"] == "gold"
        assert result[SourceEnum.PROCESS.value]["nested.key"] == "value"
        assert result[SourceEnum.PROCESS.value]["cpu_count"] == 8

    def test_parse_facts_missing_path_non_strict(self, processor, monkeypatch):
        processor.get_all_facts()

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.strict",
            False,
        )

        snapshots = {SourceEnum.PROCESS.value: [{"missing": 25}]}

        result = processor.parse_facts(snapshots)

        # All resolutions fail → empty fact sheet
        assert result[SourceEnum.PROCESS.value] == {}

    def test_parse_facts_missing_path_strict_raises(self, processor, monkeypatch):
        processor.get_all_facts()

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.strict",
            True,
        )

        snapshots = {SourceEnum.PROCESS.value: [{"age": 25}]}

        with pytest.raises(FactNotFoundException):
            processor.parse_facts(snapshots)


class TestLogging:
    def test_warning_logged_on_invalid_path(self, processor, monkeypatch):
        processor.get_all_facts()

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.strict",
            False,
        )

        snapshots = {SourceEnum.PROCESS.value: [{"age": 40}]}

        processor.parse_facts(snapshots)
