from typing import Any

from src.rules_engine.model.operators import Operator
from src.rules_engine.model.condition import Condition


class ConditionEvaluator:
    @staticmethod
    def evaluate_field(condition: Condition, facts: dict) -> Any:
        """
        Resolve the model value from facts using the Condition's FieldRef.
        """
        return condition.field.evaluate(facts)

    @staticmethod
    def evaluate(condition: Condition, facts: dict) -> bool:
        """
        Evaluate the model: compare the model value with the model value using the operator.
        """
        field_value = ConditionEvaluator.evaluate_field(condition, facts)
        return ConditionEvaluator.apply_operator(condition.operator, field_value, condition.value)

    @staticmethod
    def apply_operator(operator: Operator, left: Any, right: Any) -> bool:
        """
        Map your Operator enum to actual Python operations.
        """
        if operator == Operator.GT:
            return left > right
        elif operator == Operator.GTE:
            return left >= right
        elif operator == Operator.LT:
            return left < right
        elif operator == Operator.LTE:
            return left <= right
        elif operator == Operator.EQ:
            return left == right
        elif operator == Operator.NE:
            return left != right
        else:
            raise ValueError(f"Unsupported operator {operator}")
