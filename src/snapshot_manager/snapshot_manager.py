import os
from dataclasses import dataclass, field, fields
from typing import Optional

import psutil

from src.snapshot_manager.snapshot.snapshot_factory import SnapshotFactory


@dataclass
class SnapshotCategories:
    processes: Optional[list[psutil.Process]] = field(default_factory=list)


class SnapshotManager:
    def __init__(self):
        self._categories = SnapshotCategories()
        self._factory = SnapshotFactory()

    def get_all_snapshots(self) -> list:
        snapshots = []

        snapshots.extend(self.get_process_snapshots())

        return snapshots

    def get_process_snapshots(self) -> list:
        return [self._factory.create_process_snapshot(item) for item in self._categories.processes]

    def register_processes(self, processes: list[psutil.Process]) -> None:
        self._categories.processes.extend(processes)