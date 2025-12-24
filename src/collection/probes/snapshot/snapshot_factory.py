from typing import Optional

import psutil

from collection.probes.snapshot.process_snapshot.collectors import DEFAULT_COLLECTORS as p_DEFAULT_COLLECTORS
from collection.probes.snapshot.process_snapshot.process_snapshot import ProcessSnapshot, _safe
from collection.probes.snapshot.snapshot_extractor import SnapshotExtractor


class SnapshotFactory:
    """
    General factory class for creating various snapshot types.
    """
    def __init__(self):
        # psutil Process Snapshot
        self.process_extractor = SnapshotExtractor[ProcessSnapshot, psutil.Process]()
        for collector in p_DEFAULT_COLLECTORS:
            self.process_extractor.register_collector(collector)
        # Others

    def create_process_snapshot(self,
                                proc: psutil.Process,
                                ) -> Optional[ProcessSnapshot]:
        """
        Create a fully populated ProcessSnapshot.
        """
        snap = ProcessSnapshot(
            pid=proc.pid,
            name=_safe(proc.name, "unknown"),
            create_time=_safe(proc.create_time, 0.0)
        )

        self.process_extractor.apply(proc, snap)
        return snap