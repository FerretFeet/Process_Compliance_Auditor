from typing import TYPE_CHECKING, Any

from core.fact_processor.available_facts.process_facts import PROCESS_FACTS
from shared._common.facts import FactSpec

if TYPE_CHECKING:
    from core.rules_engine.model.rule import SourceEnum
    from shared._common.operators import Operator


class FactRegistry:
    _registry: dict[str, FactSpec] = {}

    @classmethod
    def register_raw(
        cls,
        path: str,
        type_: type,
        source: SourceEnum,
        allowed_operators: set[Operator],
        description: str = "",
        allowed_values: set[str] | None = None,
    ) -> None:
        if path in cls._registry:
            msg = f"Fact '{path}' is already registered"
            raise ValueError(msg)
        fact = FactSpec(
            path=path,
            type=type_,
            source=source,
            description=description,
            allowed_operators=allowed_operators or set(),
            allowed_values=allowed_values or set(),
        )

        cls._registry[path] = fact

    @classmethod
    def register_fact(cls, fact: FactSpec) -> None:
        if fact.path in cls._registry:
            msg = f"Fact '{fact.path}' is already registered"
            raise ValueError(msg)
        cls._registry[fact.path] = fact

    @classmethod
    def get_fact(cls, path: str) -> FactSpec:
        if path not in cls._registry:
            msg = f"Fact '{path}' is not registered"
            raise KeyError(msg)
        return cls._registry[path]

    @classmethod
    def all_facts(cls) -> dict[str, FactSpec]:
        return dict(cls._registry)

    @classmethod
    def validate(cls, path: str, value: Any) -> bool:
        spec = cls.get_fact(path)
        if value is None:
            return True  # optional: allow None
        if not isinstance(value, spec.type):
            msg = f"Expected {path} to be {spec.type}, got {type(value)}"
            raise TypeError(msg)
        return True

    @classmethod
    def _clear(cls) -> None:
        cls._registry = {}


def register_defaults() -> None:
    for fact in PROCESS_FACTS:
        FactRegistry.register_fact(fact)


register_defaults()
