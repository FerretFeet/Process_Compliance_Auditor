import psutil

from core.probes.base import GenericProbe
from core.probes.snapshot.process_snapshot.collectors import DEFAULT_COLLECTORS
from core.probes.snapshot.process_snapshot.process_snapshot import ProcessSnapshot, _safe
from core.probes.snapshot.snapshot_extractor import SnapshotExtractor


class ProbeLibrary:
    """Namespace for creating configured probes."""

    @staticmethod
    def process_probe(proc: psutil.Process) -> GenericProbe:
        extractor = SnapshotExtractor[ProcessSnapshot, psutil.Process]()
        for c in DEFAULT_COLLECTORS:
            extractor.register_collector(c)

        return GenericProbe(
            name="process",
            source=None,
            extractor=extractor,
            initializer=ProcessSnapshot.from_source
        )

    # @staticmethod
    # def system_probe() -> GenericProbe:
    #     extractor = SnapshotExtractor[SystemSnapshot, Any]()
    #     extractor.register_collector(collect_cpu_load)  # New system collector
    #
    #     def init_sys(_): return SystemSnapshot()
    #
    #     return GenericProbe("system_info", None, extractor, init_sys)