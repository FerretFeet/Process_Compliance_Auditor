from typing import Type, Any, Dict, Set

from shared._common.facts import FactSpec


class FactRegistry:
    _registry: Dict[str, FactSpec] = {}

    @classmethod
    def register(
        cls,
        path: str,
        type_: Type,
        description: str = "",
        allowed_operators: Set[str] | None = None,
        allowed_values: Set[str] | None = None,
    ) -> None:
        if path in cls._registry:
            raise ValueError(f"Fact '{path}' is already registered")
        cls._registry[path] = FactSpec(
            path=path,
            type=type_,
            description=description,
            allowed_operators=allowed_operators or set(),
            allowed_values=allowed_values or set(),
        )

    @classmethod
    def get(cls, path: str) -> FactSpec:
        if path not in cls._registry:
            raise KeyError(f"Fact '{path}' is not registered")
        return cls._registry[path]

    @classmethod
    def all_facts(cls) -> dict[str, FactSpec]:
        return dict(cls._registry)

    @classmethod
    def validate(cls, path: str, value: Any) -> bool:
        spec = cls.get(path)
        if value is None:
            return True  # optional: allow None
        if not isinstance(value, spec.type):
            raise TypeError(f"Expected {path} to be {spec.type}, got {type(value)}")
        return True


# FactRegistry.register("cpu.percent", float, "CPU usage percent", {">", "<", ">=", "<=", "=="})