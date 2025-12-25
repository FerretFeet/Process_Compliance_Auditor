import pytest
from unittest.mock import MagicMock

from collection.snapshot_manager.snapshot_manager import SnapshotManager, Probe


class TestSnapshotManager:

    @pytest.fixture
    def manager(self):
        """Returns a fresh SnapshotManager instance for each test."""
        return SnapshotManager()

    @pytest.fixture
    def mock_probe(self):
        """Creates a mock that satisfies the Probe protocol."""
        probe = MagicMock(spec=Probe)
        probe.name = "TestProbe"
        # We define what collect() returns so we can verify it later
        probe.collect.return_value = {"data": "snapshot_result"}
        return probe

    def test_add_probe(self, manager, mock_probe):
        """Verify a single probe can be added to the manager."""
        manager.add_probe(mock_probe)
        assert len(manager._probes) == 1
        assert manager._probes[0] == mock_probe

    def test_add_probes_list(self, manager):
        """Verify multiple probes can be added at once."""
        probes = [MagicMock(spec=Probe) for _ in range(3)]
        manager.add_probes(probes)
        assert len(manager._probes) == 3


    def test_get_all_snapshots_aggregation(self, manager, mock_probe):
        """
        Verify get_all_snapshots aggregates results.
        Currently it only calls get_process_snapshots.
        """
        manager.add_probe(mock_probe)

        all_snaps = manager.get_all_snapshots()

        assert len(all_snaps) == 1
        assert all_snaps[mock_probe.name][0] == {"data": "snapshot_result"}

    def test_empty_manager_returns_empty_dict(self, manager):
        """Ensure no errors occur when calling snapshots on an empty manager."""
        assert manager.get_all_snapshots() == {}