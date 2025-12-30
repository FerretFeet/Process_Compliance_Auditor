from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core.rules_engine.eval.condition_evaluator import ConditionEvaluator
from core.rules_engine.eval.condition_evaluator import ConditionEvaluator as ce

if TYPE_CHECKING:
    import datetime

    from core.rules_engine.model import Rule
    from core.rules_engine.rules_engine import FactCheck


@dataclass
class FailEvent:
    """Information about a rule failure."""

    pid: int
    proc_name: str
    rule_id: int
    rule_name: str
    rule_message: str
    time_registered: datetime.datetime
    time_occured: datetime.datetime
    failed_condition: FactCheck


class ComplianceEngine:
    def __init__(self, condition_evaluator: ConditionEvaluator = ce) -> None:
        self.condition_evaluator = condition_evaluator

    def run(self, rules: dict[str, Rule], factsheets: dict[str, dict[str, Any]]):
        """
        Check that facts are as defined in Rules.

        Args:
            rules: dict[rule.path, Rule]. container of all rules to check
            factsheets: dict[fact.source, dict[fact.path, Any]].

        """
        result = {
            "passed": [],
            "failed": [],
        }
        for rule in rules.values():
            factgroup = factsheets[rule.source.value]
            if not self.condition_evaluator.evaluate(rule.condition, factgroup):
                rule.action.execute()
                result["failed"].append(rule)
            else:
                result["passed"].append(rule)

        return result
