from unittest.mock import MagicMock

import pytest

from core.probes.base import GenericProbe


class TestGenericProbe:
    @pytest.fixture
    def mock_source(self):
        """Mocked raw source (e.g., a psutil.Process)."""
        return MagicMock(name="Source")

    @pytest.fixture
    def mock_extractor(self):
        """Mocked SnapshotExtractor."""
        extractor = MagicMock()
        extractor.apply.side_effect = lambda source, snap: snap
        return extractor

    @pytest.fixture
    def mock_initializer(self):
        """Mocked initializer function/method."""
        return MagicMock()

    def test_initialization_calls_initializer(self, mock_source, mock_extractor, mock_initializer):
        """Verify that the source is initialized immediately upon probe creation."""
        GenericProbe(
            name="test-probe",
            source=mock_source,
            extractor=mock_extractor,
            initializer=mock_initializer,
        )

        mock_initializer.assert_called_once_with(mock_source)

    def test_collect_returns_populated_snapshot(self, mock_source, mock_extractor):
        """Verify collect() creates a base snapshot and applies the extractor."""
        fake_snapshot = {"data": "skeleton"}
        initializer = MagicMock(return_value=fake_snapshot)

        final_snapshot = {"data": "enriched"}

        mock_extractor.apply.side_effect = None
        mock_extractor.apply.return_value = final_snapshot

        probe = GenericProbe(
            name="test-probe", source=mock_source, extractor=mock_extractor, initializer=initializer,
        )

        result = probe.collect()

        assert initializer.call_count == 2

        mock_extractor.apply.assert_called_with(mock_source, fake_snapshot)

        assert result == final_snapshot

    def test_collect_is_repeatable(self, mock_source, mock_extractor):
        """Ensure calling collect multiple times works as expected."""

        def dummy_init(src):
            return {"id": src.id}

        mock_source.id = 1
        probe = GenericProbe("repeat", mock_source, mock_extractor, dummy_init)

        snap1 = probe.collect()
        snap2 = probe.collect()

        assert snap1 == snap2
        assert mock_extractor.apply.call_count == 2

    def test_type_integrity_smoke(self, mock_source, mock_extractor):
        """Basic check to ensure the probe stores its metadata correctly."""
        probe = GenericProbe("type-check", mock_source, mock_extractor, MagicMock())
        assert probe.name == "type-check"
        assert probe._source == mock_source
