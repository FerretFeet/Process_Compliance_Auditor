import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar

S = TypeVar("S", bound="BaseSnapshot")
R = TypeVar("R")


@dataclass
class BaseSnapshot(ABC):
    snapshot_time: float = field(default_factory=lambda: time.time())
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    @abstractmethod
    def from_source(cls: type[S], source: R) -> S:
        """Enforce that every snapshot knows how to build its skeleton."""
