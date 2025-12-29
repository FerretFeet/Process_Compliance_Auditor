from typing import Any

from core.rules_engine.model.condition import Condition, ConditionSet, Expression, NotCondition
from core.rules_engine.model.operators import Operator
from shared._common.operators import GroupOperator


class ConditionEvaluator:
    @staticmethod
    def evaluate(expression: Expression, facts: dict) -> bool:
        """
        Entry point for evaluation. Routes to the specific evaluator
        based on the expression type.
        """
        if isinstance(expression, Condition):
            return ConditionEvaluator._evaluate_single(expression, facts)

        if isinstance(expression, NotCondition):
            # Recursively evaluate the inner condition and invert it
            return not ConditionEvaluator.evaluate(expression.condition, facts)

        if isinstance(expression, ConditionSet):
            return ConditionEvaluator._evaluate_set(expression, facts)

        msg = f"Unknown expression type: {type(expression)}"
        raise TypeError(msg)

    @staticmethod
    def _evaluate_single(condition: Condition, facts: dict) -> bool:
        """Handles a standard leaf-node Condition."""
        field_value = condition.field.evaluate(facts)
        return ConditionEvaluator.apply_operator(condition.operator, field_value, condition.value)

    @staticmethod
    def _evaluate_set(condition_set: ConditionSet, facts: dict) -> bool:
        """Handles AND (ALL) and OR (ANY) logic."""
        results = (ConditionEvaluator.evaluate(c, facts) for c in condition_set.conditions)

        if condition_set.group_operator == GroupOperator.ALL:
            return all(results)
        if condition_set.group_operator == GroupOperator.ANY:
            return any(results)

        msg = f"Unsupported GroupOperator: {condition_set.group_operator}"
        raise ValueError(msg)

    @staticmethod
    def apply_operator(operator: Operator, left: Any, right: Any) -> bool:
        """Map your Operator enum to actual Python operations."""
        if operator == Operator.GT:
            return left > right
        if operator == Operator.GTE:
            return left >= right
        if operator == Operator.LT:
            return left < right
        if operator == Operator.LTE:
            return left <= right
        if operator == Operator.EQ:
            return left == right
        if operator == Operator.NE:
            return left != right
        msg = f"Unsupported operator {operator}"
        raise ValueError(msg)
