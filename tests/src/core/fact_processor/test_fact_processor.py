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
        assert set(facts1.keys()) == {
            "age",
            "membership",
            "nested.key",
            "cpu_count",
        }


class TestGetFactsBySource:
    def test_get_facts_by_source(self, processor):
        processor.get_all_facts()  # ensure cache populated

        facts = processor.get_facts_by_source(SourceEnum.PROCESS)

        assert set(facts.keys()) == {
            "age",
            "membership",
            "nested.key",
            "cpu_count",
        }

    def test_get_facts_by_sources_filters_empty(self, processor):
        processor.get_all_facts()

        result = processor.get_facts_by_sources(
            [SourceEnum.PROCESS, "missing"]
        )

        assert SourceEnum.PROCESS in result
        assert "missing" not in result


class TestParseFacts:
    def test_parse_facts_success(self, processor, monkeypatch):
        processor.get_all_facts()

        snapshots = {
            SourceEnum.PROCESS: [
                {
                    "age": 30,
                    "membership": "gold",
                    "nested": {"key": "value"},
                    "cpu_count": 8,
                }
            ]
        }

        result = processor.parse_facts(snapshots)

        assert result[SourceEnum.PROCESS]["age"] == 30
        assert result[SourceEnum.PROCESS]["membership"] == "gold"
        assert result[SourceEnum.PROCESS]["nested.key"] == "value"
        assert result[SourceEnum.PROCESS]["cpu_count"] == 8

    def test_parse_facts_missing_path_non_strict(self, processor, monkeypatch):
        processor.get_all_facts()

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.resolve_path",
            lambda *_: (_ for _ in ()).throw(ValueError("invalid path")),
        )

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.strict",
            False,
        )

        snapshots = {
            SourceEnum.PROCESS: [
                {"age": 25}
            ]
        }

        result = processor.parse_facts(snapshots)

        # All resolutions fail → empty fact sheet
        assert result[SourceEnum.PROCESS] == {}

    def test_parse_facts_missing_path_strict_raises(self, processor, monkeypatch):
        processor.get_all_facts()

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.resolve_path",
            lambda *_: (_ for _ in ()).throw(ValueError("invalid path")),
        )

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.strict",
            True,
        )

        snapshots = {
            SourceEnum.PROCESS: [
                {"age": 25}
            ]
        }

        with pytest.raises(FactNotFoundException):
            processor.parse_facts(snapshots)


class TestLogging:
    def test_warning_logged_on_invalid_path(self, processor, monkeypatch):
        processor.get_all_facts()

        fake_logger = MagicMock()

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.logger",
            fake_logger,
        )

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.strict",
            False,
        )

        monkeypatch.setattr(
            "core.fact_processor.fact_processor.resolve_path",
            lambda *_: (_ for _ in ()).throw(ValueError("bad path")),
        )

        snapshots = {
            SourceEnum.PROCESS: [
                {"age": 40}
            ]
        }

        processor.parse_facts(snapshots)

        fake_logger.warning.assert_called()
