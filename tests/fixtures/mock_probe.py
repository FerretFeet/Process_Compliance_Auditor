from unittest.mock import MagicMock

import pytest

from collection.snapshot_manager.snapshot_manager import Probe


@pytest.fixture
def mock_probe():
    """Creates a mock that satisfies the Probe protocol."""
    probe = MagicMock(spec=Probe)
    probe.name = "TestProbe"
    # We define what collect() returns so we can verify it later
    probe.collect.return_value = {"data": "snapshot_result"}
    return probe
