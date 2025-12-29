from unittest.mock import MagicMock

from collection.snapshot_manager.snapshot_manager import Probe


class TestSnapshotManager:

    def test_add_probe(self, real_snapshot_manager, mock_probe):
        """Verify a single probe can be added to the manager."""
        real_snapshot_manager.add_probe(mock_probe)
        assert len(real_snapshot_manager._probes) == 1
        assert real_snapshot_manager._probes[0] == mock_probe

    def test_add_probes_list(self, real_snapshot_manager):
        """Verify multiple probes can be added at once."""
        probes = [MagicMock(spec=Probe) for _ in range(3)]
        real_snapshot_manager.add_probes(probes)
        assert len(real_snapshot_manager._probes) == 3

    def test_get_all_snapshots_aggregation(self, real_snapshot_manager, mock_probe):
        """
        Verify get_all_snapshots aggregates results.
        Currently it only calls get_process_snapshots.
        """
        real_snapshot_manager.add_probe(mock_probe)

        all_snaps = real_snapshot_manager.get_all_snapshots()

        assert len(all_snaps) == 1
        assert all_snaps[mock_probe.name][0] == {"data": "snapshot_result"}

    def test_empty_manager_returns_empty_dict(self, real_snapshot_manager):
        """Ensure no errors occur when calling snapshots on an empty manager."""
        assert real_snapshot_manager.get_all_snapshots() == {}
