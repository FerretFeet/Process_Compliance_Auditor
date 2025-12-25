import pytest
import time
from unittest.mock import patch
from dataclasses import dataclass

from core.probes.snapshot.base import BaseSnapshot


# --- Concrete Implementation for Testing ---

@dataclass
class MockSnapshot(BaseSnapshot):
    data: str = ""

    @classmethod
    def from_source(cls, source: str) -> "MockSnapshot":
        return cls(data=source)


# --- Tests ---

class TestBaseSnapshot:

    def test_cannot_instantiate_abstract_base(self):
        """Ensure BaseSnapshot cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseSnapshot()

    def test_default_values(self):
        """Verify snapshot_time and metadata initialize with expected defaults."""
        fixed_time = 123456789.0
        with patch("src.core.probes.snapshot.base.time.time", return_value=fixed_time):
            snapshot = MockSnapshot(data="test")

            assert snapshot.snapshot_time == fixed_time
            assert snapshot.metadata == {}
            assert snapshot.data == "test"

    def test_metadata_is_unique_instance(self):
        """Ensure metadata dict is not shared across instances (default_factory check)."""
        s1 = MockSnapshot(data="one")
        s2 = MockSnapshot(data="two")

        s1.metadata["key"] = "value"

        assert "key" not in s2.metadata
        assert s1.metadata is not s2.metadata

    def test_from_source_implementation(self):
        """Verify the factory method works in the concrete subclass."""
        source_data = "raw_input_string"
        snapshot = MockSnapshot.from_source(source_data)

        assert isinstance(snapshot, MockSnapshot)
        assert snapshot.data == source_data
        assert isinstance(snapshot.snapshot_time, float)

    def test_subclass_must_implement_from_source(self):
        """Verify that a subclass without from_source cannot be instantiated."""
        with pytest.raises(TypeError):
            @dataclass
            class IncompleteSnapshot(BaseSnapshot):
                pass

            IncompleteSnapshot()