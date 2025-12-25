import re
from typing import Type, Optional

from core.fact_processor.fact_registry import FactRegistry
from core.rules_engine.model.condition import Condition
from core.rules_engine.model.field import FieldRef
from shared._common.operators import Operator
from shared.services import logger
from shared.utils import get_project_config, cfg

_strict = cfg.get("strict")


TYPE_MAP = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
}


def cast_value(value_str: str, expected_type: Type) -> object:
    """Cast a string to expected_type according to current mode."""
    try:
        return expected_type(value_str)
    except Exception:
        if _strict is True:
            raise ValueError(f"Cannot cast '{value_str}' to {expected_type.__name__}")
        else:
            return value_str


def cond(expr: str) -> Condition:
    """
    Parse a string like "cpu.percent > 80" or "process.running == true:bool"
    into a Condition object using FieldRef and Operator enum.
    Explicit type hints are optional and validated against the registry type.
    """
    expr = expr.strip()
    sorted_ops = sorted(Operator, key=lambda op: -len(op.value))  # <=, >= first

    for op_enum in sorted_ops:
        pattern = rf"\s{re.escape(op_enum.value)}\s"
        match = re.search(pattern, f" {expr} ")
        if match:
            field_str, value_str = map(str.strip, re.split(pattern, expr, maxsplit=1))

            declared_type: Optional[Type] = None
            if ":" in value_str:
                raw_value, type_name = value_str.rsplit(":", 1)
                value_str = raw_value.strip()
                declared_type = TYPE_MAP.get(type_name.strip())
                if declared_type is None:
                    raise ValueError(f"Unknown explicit type '{type_name}' in expression '{expr}'.")

            try:
                field_fact = FactRegistry.get(field_str)
                fact_type = field_fact.type
            except KeyError:
                msg = f"Could not find field '{field_str}' for expression '{expr}' in fact registry."
                logger.warning(msg)
                if _strict is True:
                    raise ValueError(msg)
                fact_type = str  # fallback for unknown fields

            if declared_type and declared_type != fact_type:
                raise ValueError(
                    f"Declared type '{declared_type.__name__}' does not match "
                    f"fact registry type '{fact_type.__name__}' for '{field_str}'."
                )

            value = cast_value(value_str, fact_type)

            field_ref = FieldRef(field_str, fact_type)
            return Condition(field=field_ref, operator=op_enum, value=value)

    raise ValueError(f"Could not parse expression: {expr}")