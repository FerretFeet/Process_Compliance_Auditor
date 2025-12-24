from dataclasses import dataclass, field
from typing import Protocol, Type, Any, Collection, Optional

from shared._common.operators import Operator


class FactSpecProtocol(Protocol):
    path: str                             # e.g., key, key.child
    type: Type
    allowed_operators: Collection[Any]        # e.g., ['==', '!=', '>', '<']
    allowed_values: Optional[Collection[Any]]   # optional restriction on values


@dataclass(frozen=True)
class FactSpec:
    path: str
    type: Type
    description: str = ""
    allowed_operators: list[Operator] = field(default_factory=list)
    allowed_values: Optional[list[str]] = field(default_factory=list)
