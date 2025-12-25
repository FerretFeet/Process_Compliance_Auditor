import pytest
from unittest.mock import MagicMock, patch
import psutil
import time
from core.probes.snapshot.process_snapshot.process_snapshot import ProcessSnapshot, _safe, CpuSnapshot, MemorySnapshot


class TestSafeHelper:
    def test_safe_with_callable_success(self):
        """Should return the result of the callable."""
        assert _safe(lambda: "hello") == "hello"

    def test_safe_with_value_success(self):
        """Should return the value directly if not callable."""
        assert _safe(100) == 100

    def test_safe_on_exception_returns_default(self):
        """Should return the default value when an exception occurs."""

        def buggy():
            raise ValueError("Boom")

        assert _safe(buggy, default="fallback") == "fallback"


class TestProcessSnapshot:



    def test_from_source_creation(self, mock_proc):
        """Verify from_source correctly maps psutil attributes."""
        snapshot = ProcessSnapshot.from_source(mock_proc)

        assert snapshot.pid == 999
        assert snapshot.name == "test_proc"
        assert snapshot.create_time == 12345.67

    def test_from_source_handles_psutil_errors(self, mock_proc):
        """Ensure the class survives psutil AccessDenied or NoSuchProcess errors."""
        mock_proc.name.side_effect = psutil.AccessDenied()

        snapshot = ProcessSnapshot.from_source(mock_proc)
        assert snapshot.name == "unknown"  # Default value in from_source

    def test_add_and_extensions(self):
        """Verify add and add_many update the extensions dictionary."""
        snapshot = ProcessSnapshot(pid=1, name="init", create_time=0.0)

        snapshot.add("version", "1.2.3")
        snapshot.add_many({"tags": ["web"], "env": "prod"})

        assert snapshot.extensions["version"] == "1.2.3"
        assert snapshot.extensions["env"] == "prod"
        assert "tags" in snapshot.extensions

    def test_section_utility(self):
        """Verify section() can retrieve attributes by name."""
        snapshot = ProcessSnapshot(pid=1, name="init", create_time=0.0)
        snapshot.cpu = {"usage": 15.5}

        assert snapshot.section("cpu") == {"usage": 15.5}
        assert snapshot.section("pid") == 1

    def test_as_dict_merging(self):
        """Verify as_dict flattens extensions into the result."""
        snapshot = ProcessSnapshot(
            pid=500,
            name="app",
            create_time=0.0,
            snapshot_time=100.0
        )
        snapshot.add("custom_key", "custom_val")

        result = snapshot.as_dict()

        # Check standard fields
        assert result["pid"] == 500
        # Check flattened extension
        assert result["custom_key"] == "custom_val"
        # Ensure 'extensions' itself isn't a key in the output
        assert "extensions" not in result

    def test_default_factories_uniqueness(self):
        """Ensure dict fields are not shared between instances."""
        s1 = ProcessSnapshot(pid=1, name="a", create_time=0.0)
        s2 = ProcessSnapshot(pid=2, name="b", create_time=0.0)

        s1.identity["user"] = "admin"
        assert "user" not in s2.identity


class TestSnapshotDataclasses:
    def test_cpu_snapshot_instantiation(self):
        """Basic smoke test for CpuSnapshot structure."""
        snap = CpuSnapshot(percent=10.0, times=None, affinity=[0, 1], cpu_num=1)
        assert snap.percent == 10.0

    def test_memory_snapshot_instantiation(self):
        """Basic smoke test for MemorySnapshot structure."""
        snap = MemorySnapshot(percent=50.0, info=None, full_info=None, maps=[])
        assert snap.percent == 50.0