"""Snapshot Manager."""

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from core.probes.snapshot.base import BaseSnapshot


class Probe(Protocol):
    """Protocol for probe objects."""

    name: str

    def collect(self) -> Any:  # noqa: ANN401
        """Return all of the available data from the probe."""
        ...


class SnapshotManager:
    """Track probes and get snapshots of their data."""

    def __init__(self) -> None:
        """Initialize the manager."""
        self._probes: list[Probe] = []

    def get_all_snapshots(self) -> dict[str, list[BaseSnapshot]]:
        """
        Return a dict of snapshots from all tracked probes.

        Returns:
            dict[str, list[BaseSnapshot]]: source: list[snapshots from source]

        """
        returndict = {}
        for probe in self._probes:
            returndict.setdefault(probe.name, []).append(probe.collect())
        return returndict

    def add_probe(self, probe: Probe) -> None:
        """Add a probe to this manager."""
        self._probes.append(probe)

    def add_probes(self, probes: list[Probe]) -> None:
        """Add a list of probes to this manager."""
        for probe in probes:
            self.add_probe(probe)
