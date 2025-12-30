"""Data probes to collect data from sources."""

from enum import Enum

import psutil

from core.probes.base import GenericProbe
from core.probes.snapshot.process_snapshot.collectors import DEFAULT_COLLECTORS
from core.probes.snapshot.process_snapshot.process_snapshot import ProcessSnapshot
from core.probes.snapshot.snapshot_extractor import SnapshotExtractor


class SourceEnum(Enum):
    """Enum for sources of data probes."""

    PROCESS = "process"


class ProbeLibrary:
    """Namespace for creating configured probes."""

    @staticmethod
    def process_probe(proc: psutil.Process) -> GenericProbe:
        """Create a probe for a process."""
        extractor = SnapshotExtractor[ProcessSnapshot, psutil.Process]()
        for c in DEFAULT_COLLECTORS:
            extractor.register_collector(c)

        return GenericProbe(
            name=SourceEnum.PROCESS.value,
            source=proc,
            extractor=extractor,
            initializer=ProcessSnapshot.from_source,
        )
