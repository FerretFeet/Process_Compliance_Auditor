from collections import defaultdict
from typing import Type, Any, Dict, Set

from core.fact_processor.available_facts.process_facts import PROCESS_FACTS
from core.rules_engine.model.rule import SourceEnum
from shared._common.facts import FactSpec
from shared._common.operators import Operator


class FactRegistry:
    _registry: Dict[str, FactSpec] = {}

    @classmethod
    def register_raw(
        cls,
        path: str,
        type_: Type,
        source: SourceEnum,
        allowed_operators: Set[Operator],
        description: str = "",
        allowed_values: Set[str] | None = None,
    ) -> None:
        if path in cls._registry:
            raise ValueError(f"Fact '{path}' is already registered")
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
            raise ValueError(f"Fact '{fact.path}' is already registered")
        cls._registry[fact.path] = fact

    @classmethod
    def get_fact(cls, path: str) -> FactSpec:
        if path not in cls._registry:
            raise KeyError(f"Fact '{path}' is not registered")
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
            raise TypeError(f"Expected {path} to be {spec.type}, got {type(value)}")
        return True

    @classmethod
    def _clear(cls):
        cls._registry = {}


def register_defaults():
    for fact in PROCESS_FACTS:
        FactRegistry.register_fact(fact)


register_defaults()
