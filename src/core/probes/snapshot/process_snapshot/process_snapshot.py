"""Process Snapshot."""

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from core.probes.snapshot.base import BaseSnapshot

if TYPE_CHECKING:
    from collections.abc import Callable

    import psutil


def _safe(callable_attr: Callable, default: Any = None) -> Any:  # noqa: ANN401
    """Safely call psutil attributes that are functions."""
    try:
        return callable_attr() if callable(callable_attr) else callable_attr
    except Exception:  # noqa: BLE001
        return default


@dataclass(kw_only=True)
class ProcessSnapshot(BaseSnapshot):
    """Data container for a psutil Process data snapshot."""

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

    def add(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Add a key and value to the snapshot. Added to snapshot.extensions."""
        self.extensions[key] = value

    def add_many(self, data: dict[str, Any]) -> None:
        """Add multiple key/value pairs. Held to snapshot.extensions."""
        self.extensions.update(data)

    def section(self, name: str) -> Any:  # noqa: ANN401
        """Get the value of a section."""
        return getattr(self, name)

    def as_dict(self) -> dict[str, Any]:
        """Return the snapshot as a dictionary."""
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
        """Initialize the snapshot data from its source."""
        return cls(
            pid=proc.pid,
            name=_safe(proc.name, "unknown"),
            create_time=_safe(proc.create_time, 0.0),
        )


@dataclass
class CpuSnapshot:
    """Sub-group for cpu related data."""

    percent: float | None
    times: Any
    affinity: list[int] | None
    cpu_num: int | None


@dataclass
class MemorySnapshot:
    """Sub-group for memory related data."""

    percent: float | None
    info: Any
    full_info: Any
    maps: list | None
