from typing import Protocol, Any

from core.probes.snapshot.base import BaseSnapshot


class Probe(Protocol):
    name: str
    def collect(self) -> Any:
        ...


class SnapshotManager:
    def __init__(self):
        self._probes: list[Probe] = []

    def get_all_snapshots(self) -> dict[str, list[BaseSnapshot]]:
        returndict = {}
        for probe in self._probes:
            returndict.setdefault(probe.name, []).append(probe.collect())
        return returndict


    def add_probe(self, probe: Probe) -> None:
        self._probes.append(probe)

    def add_probes(self, probes: list[Probe]) -> None:
        for probe in probes:
            self.add_probe(probe)