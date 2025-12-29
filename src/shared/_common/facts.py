from dataclasses import dataclass, field
from typing import Protocol, Type, Any, Collection, Optional

from core.rules_engine.model.rule import SourceEnum
from shared._common.operators import Operator


class FactSpecProtocol(Protocol):
    path: str  # e.g., key, key.child
    type: Type
    allowed_operators: Collection[Any]  # e.g., ['==', '!=', '>', '<']
    allowed_values: Optional[Collection[Any]]  # optional restriction on values


@dataclass(frozen=True)
class FactSpec:
    path: str
    type: Type
    source: SourceEnum
    description: str = ""
    allowed_operators: Collection[Operator] = field(default_factory=list)
    allowed_values: Optional[Collection[str]] = field(default_factory=list)


@dataclass(frozen=True)
class FactData:
    spec: FactSpec
    value: Any
