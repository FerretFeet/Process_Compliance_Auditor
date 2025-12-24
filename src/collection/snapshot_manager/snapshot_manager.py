from typing import Protocol, Any


class Probe(Protocol):
    name: str
    def collect(self) -> Any:
        ...


class SnapshotManager:
    def __init__(self):
        self._probes: list[Probe] = []

    def get_all_snapshots(self) -> list:
        snapshots = []

        snapshots.extend(self.get_process_snapshots())

        return snapshots

    def get_process_snapshots(self) -> list:
        return [probe.collect() for probe in self._probes]

    def add_probe(self, probe: Probe) -> None:
        self._probes.append(probe)

    def add_probes(self, probes: list[Probe]) -> None:
        for probe in probes:
            self.add_probe(probe)