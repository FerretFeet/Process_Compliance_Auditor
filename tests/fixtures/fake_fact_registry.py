import pytest

from core.fact_processor.fact_registry import FactRegistry
from core.rules_engine.model.rule import SourceEnum
from shared._common.operators import Operator


@pytest.fixture
def fake_fact_registry():
    # Setup
    FactRegistry.register('age', int, [SourceEnum.PROCESS], set(Operator))
    FactRegistry.register('membership', str, [SourceEnum.PROCESS], set(Operator))
    FactRegistry.register('nested.key', str, [SourceEnum.PROCESS], set(Operator))
    FactRegistry.register('cpu_count', int, [SourceEnum.PROCESS], set(Operator))


    yield  # The test runs here

    # Teardown
    FactRegistry._clear()