import pytest
from unittest.mock import MagicMock
import psutil
from core.probes.snapshot.process_snapshot.collectors import (
    collect_identity,
    collect_cpu,
    collect_memory,
    collect_relationships,
)
from core.probes.snapshot.process_snapshot.process_snapshot import (
    ProcessSnapshot,
    CpuSnapshot,
    MemorySnapshot,
)


class TestCollectors:

    def test_collect_identity(self, mock_proc, empty_snap):
        mock_proc.ppid.return_value = 1
        mock_proc.exe.return_value = "/usr/bin/python"
        mock_proc.username.return_value = "root"
        mock_proc.cmdline.return_value = ["python", "app.py"]

        collect_identity(mock_proc, empty_snap)

        id_data = empty_snap.identity
        assert id_data["ppid"] == 1
        assert id_data["exe"] == "/usr/bin/python"
        assert id_data["username"] == "root"
        assert id_data["cmdline"] == ["python", "app.py"]

    def test_collect_cpu(self, mock_proc, empty_snap):
        mock_proc.cpu_percent.return_value = 15.5
        mock_proc.cpu_num.return_value = 2

        collect_cpu(mock_proc, empty_snap)

        assert isinstance(empty_snap.cpu, CpuSnapshot)
        assert empty_snap.cpu.percent == 15.5
        assert empty_snap.cpu.cpu_num == 2

        # collection is instant
        mock_proc.cpu_percent.assert_called_with(interval=0.0)

    def test_collect_memory(self, mock_proc, empty_snap):
        mock_proc.memory_percent.return_value = 5.0
        mock_proc.memory_info.return_value = "fake_info"

        collect_memory(mock_proc, empty_snap)

        assert isinstance(empty_snap.memory, MemorySnapshot)
        assert empty_snap.memory.percent == 5.0
        assert empty_snap.memory.info == "fake_info"

    def test_collect_relationships(self, mock_proc, empty_snap):
        parent = MagicMock(spec=psutil.Process)
        parent.pid = 1
        child = MagicMock(spec=psutil.Process)
        child.pid = 5678

        mock_proc.parents.return_value = [parent]
        mock_proc.children.return_value = [child]

        collect_relationships(mock_proc, empty_snap)

        assert empty_snap.relationships["parents"] == [1]
        assert empty_snap.relationships["children"] == [5678]

    def test_collectors_handle_exceptions(self, mock_proc, empty_snap):
        """Ensure that if a psutil call fails, the collector doesn't crash."""
        mock_proc.exe.side_effect = psutil.AccessDenied()
        mock_proc.cmdline.return_value = ["test"]

        collect_identity(mock_proc, empty_snap)

        assert empty_snap.identity["exe"] is None
        assert empty_snap.identity["cmdline"] == ["test"]
