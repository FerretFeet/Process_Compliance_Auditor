import pytest

from collection.snapshot_manager.snapshot_manager import SnapshotManager


@pytest.fixture
def real_snapshot_manager():
    """Returns a fresh SnapshotManager instance for each test."""
    return SnapshotManager()
