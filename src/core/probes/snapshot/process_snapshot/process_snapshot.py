# process_snapshot.py
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from core.probes.snapshot.base import BaseSnapshot

if TYPE_CHECKING:
    import psutil


def _safe(callable_attr, default=None):
    """Helper to safely call psutil attributes that may raise exceptions."""
    try:
        if callable(callable_attr):
            return callable_attr()
        return callable_attr
    except Exception:
        return default


@dataclass(kw_only=True)
class ProcessSnapshot(BaseSnapshot):
    pid: int
    name: str
    create_time: float
    snapshot_time: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)
    is_running: bool = False

    identity: dict[str, Any] = field(default_factory=dict)
    cpu: Any = field(default_factory=dict)
    memory: Any = field(default_factory=dict)
    io: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)

    def add(self, key: str, value: Any) -> None:
        self.extensions[key] = value

    def add_many(self, data: dict[str, Any]) -> None:
        self.extensions.update(data)

    def section(self, name: str) -> Any:
        return getattr(self, name)

    def as_dict(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "create_time": self.create_time,
            "snapshot_time": self.snapshot_time,
            "is_running": self.is_running,
            "identity": self.identity,
            "cpu": self.cpu,
            "memory": self.memory,
            "io": self.io,
            "relationships": self.relationships,
            "raw": self.raw,
            **self.extensions,
        }

    @classmethod
    def from_source(cls, proc: psutil.Process) -> ProcessSnapshot:
        # We use 'cls' so that if you subclass this,
        # it creates the correct child type.
        return cls(
            pid=proc.pid,
            name=_safe(proc.name, "unknown"),
            create_time=_safe(proc.create_time, 0.0),
        )


@dataclass
class CpuSnapshot:
    percent: float | None
    times: Any
    affinity: list[int] | None
    cpu_num: int | None


@dataclass
class MemorySnapshot:
    percent: float | None
    info: Any
    full_info: Any
    maps: list | None
