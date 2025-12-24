from typing import Callable, List, TypeVar, Generic

S = TypeVar("S")
R = TypeVar("R")

class SnapshotExtractor(Generic[S, R]):
    """Class to extract S attrs from a mapping R."""
    def __init__(self):
        self.collectors: List[Callable[[R, S], None]] = []

    def register_collector(self, collector: Callable[[R, S], None]) -> "SnapshotExtractor":
        """Add a collector to the collectors list."""
        self.collectors.append(collector)
        return self

    def apply(self, source: R, snapshot: S) -> S:
        """Applies the registered collectors to the snapshot."""
        for collector in self.collectors:
            collector(source, snapshot)
        return snapshot
