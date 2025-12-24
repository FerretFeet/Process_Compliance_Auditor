import psutil

from collection.probes.base import GenericProbe
from collection.probes.snapshot.process_snapshot.collectors import DEFAULT_COLLECTORS
from collection.probes.snapshot.process_snapshot.process_snapshot import ProcessSnapshot, _safe
from collection.probes.snapshot.snapshot_extractor import SnapshotExtractor


class ProbeLibrary:
    """Namespace for creating configured probes."""

    @staticmethod
    def process_probe(proc: psutil.Process) -> GenericProbe:
        extractor = SnapshotExtractor[ProcessSnapshot, psutil.Process]()
        for c in DEFAULT_COLLECTORS:
            extractor.register_collector(c)

        def init_proc(p): return ProcessSnapshot(pid=p.pid, name=_safe(p.name, "unknown"),
                                                 create_time=_safe(p.create_time, 0.0))

        return GenericProbe(f"proc_{proc.pid}", proc, extractor, init_proc)

    # @staticmethod
    # def system_probe() -> GenericProbe:
    #     extractor = SnapshotExtractor[SystemSnapshot, Any]()
    #     extractor.register_collector(collect_cpu_load)  # New system collector
    #
    #     def init_sys(_): return SystemSnapshot()
    #
    #     return GenericProbe("system_info", None, extractor, init_sys)