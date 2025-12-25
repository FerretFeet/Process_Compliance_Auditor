import pytest

from core.fact_processor.fact_registry import FactRegistry


@pytest.fixture
def fake_fact_registry():
    # Setup
    FactRegistry.register('age', int)
    FactRegistry.register('membership', str)
    FactRegistry.register('nested.key', str)

    yield  # The test runs here

    # Teardown
    FactRegistry._clear()