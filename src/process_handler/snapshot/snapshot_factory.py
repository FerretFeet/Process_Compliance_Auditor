from typing import Optional

import psutil

from src.process_handler.snapshot.process_snapshot.collectors import DEFAULT_COLLECTORS
from src.process_handler.snapshot.process_snapshot.process_snapshot import ProcessSnapshot, _safe
from src.process_handler.snapshot.snapshot_extractor import SnapshotExtractor


class SnapshotFactory:
    """
    General factory class for creating various snapshot types.
    """
    def __init__(self):
        # Prepare a default process snapshot extractor
        self.process_extractor = SnapshotExtractor[ProcessSnapshot, psutil.Process]()
        for collector in DEFAULT_COLLECTORS:
            self.process_extractor.register_collector(collector)

    def create_process_snapshot(self,
                                proc: Optional[psutil.Process] = None,
                                *,
                                use_current: bool = False,
                                ) -> ProcessSnapshot | None:
        """
        Create a fully populated ProcessSnapshot.
        """
        if proc is None and use_current:
            proc = psutil.Process()
        elif proc is None:
            return None

        snap = ProcessSnapshot(
            pid=proc.pid,
            name=_safe(proc.name, "unknown"),
            create_time=_safe(proc.create_time, 0.0)
        )

        self.process_extractor.apply(proc, snap)
        return snap