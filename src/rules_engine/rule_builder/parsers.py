import re

from src.fact_processor.fact_registry import FactRegistry
from src.rules_engine.facts.field import FieldRef
from src.rules_engine.model.condition import Condition
from src.rules_engine.model.operators import Operator


def cond(expr: str) -> Condition:
    """
    Parse a string like "cpu.percent > 80" into a Condition object
    using FieldRef and Operator enum.
    """
    expr = expr.strip()
    sorted_ops = sorted(Operator, key=lambda op: -len(op.value))  # <=, >= first

    for op_enum in sorted_ops:
        pattern = rf"\s{re.escape(op_enum.value)}\s"
        match = re.search(pattern, f" {expr} ")
        if match:
            field_str, value_str = map(str.strip, re.split(pattern, expr, maxsplit=1))

            try:
                fact_type = FactRegistry.get(field_str).type
            except KeyError:
                fact_type = str  # fallback

            try:
                value = fact_type(value_str)
            except Exception:
                value = value_str  # fallback to string

            field_ref = FieldRef(field_str, fact_type)
            return Condition(field=field_ref, operator=op_enum, value=value)

    raise ValueError(f"Could not parse model: {expr}")
