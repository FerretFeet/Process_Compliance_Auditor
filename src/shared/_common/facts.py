from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Collection

    from core.rules_engine.model.rule import SourceEnum
    from shared._common.operators import Operator


class FactSpecProtocol(Protocol):
    path: str  # e.g., key, key.child
    type: type
    allowed_operators: Collection[Any]  # e.g., ['==', '!=', '>', '<']
    allowed_values: Collection[Any] | None  # optional restriction on values


@dataclass(frozen=True)
class FactSpec:
    path: str
    type: type
    source: SourceEnum
    description: str = ""
    allowed_operators: Collection[Operator] = field(default_factory=list)
    allowed_values: Collection[str] | None = field(default_factory=list)


@dataclass(frozen=True)
class FactData:
    spec: FactSpec
    value: Any
