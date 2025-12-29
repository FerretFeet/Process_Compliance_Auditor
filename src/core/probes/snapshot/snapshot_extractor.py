from typing import TYPE_CHECKING, TypeVar

from core.probes.snapshot.base import BaseSnapshot

if TYPE_CHECKING:
    from collections.abc import Callable

S = TypeVar("S", bound=BaseSnapshot)
R = TypeVar("R")


class SnapshotExtractor[S: BaseSnapshot, R]:
    """Class to extract S attrs from a mapping R."""

    def __init__(self) -> None:
        self.collectors: list[Callable[[R, S], None]] = []

    def register_collector(self, collector: Callable[[R, S], None]) -> SnapshotExtractor:
        """Add a collector to the collectors list."""
        self.collectors.append(collector)
        return self

    def apply(self, source: R, snapshot: S) -> S:
        """Applies the registered collectors to the snapshot."""
        for collector in self.collectors:
            collector(source, snapshot)
        return snapshot
