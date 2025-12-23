# process_snapshot.py
from dataclasses import dataclass, field
from typing import Any, Dict
import time

def _safe(callable_attr, default=None):
    """Helper to safely call psutil attributes that may raise exceptions."""
    try:
        if callable(callable_attr):
            return callable_attr()
        return callable_attr
    except Exception:
        return default

@dataclass
class ProcessSnapshot:
    pid: int
    name: str
    create_time: float
    snapshot_time: float = field(default_factory=time.time)
    is_running: bool = False

    identity: Dict[str, Any] = field(default_factory=dict)
    cpu: Any = field(default_factory=dict)
    memory: Any = field(default_factory=dict)
    io: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)
    extensions: Dict[str, Any] = field(default_factory=dict)

    def add(self, key: str, value: Any) -> None:
        self.extensions[key] = value

    def add_many(self, data: Dict[str, Any]) -> None:
        self.extensions.update(data)

    def section(self, name: str) -> Any:
        return getattr(self, name)

    def as_dict(self) -> Dict[str, Any]:
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
