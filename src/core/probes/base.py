from typing import Generic, TypeVar, Callable

from core.probes.snapshot.snapshot_extractor import SnapshotExtractor

S = TypeVar("S") # Snapshot Type
R = TypeVar("R") # Raw Source Type (e.g., psutil.Process)

class GenericProbe(Generic[S, R]):
    def __init__(self, name: str, source: R, extractor: SnapshotExtractor[S, R], initializer: Callable[[R], S]):
        self.name = name
        self._source = source
        self._extractor = extractor
        self._initializer = initializer
        self._initializer(self._source)
    def collect(self) -> S:
        """Return a dataclass of probed data"""
        base_snap = self._initializer(self._source)
        return self._extractor.apply(self._source, base_snap)