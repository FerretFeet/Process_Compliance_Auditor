from unittest.mock import MagicMock

import pytest

from core.compliance_engine import ComplianceEngine
from core.rules_engine.model.rule import Action, Rule, SourceEnum


@pytest.fixture
def factsheets():
    return {
        "process": {
            "age": 30,
            "cpu_count": 8,
        },
    }


@pytest.fixture
def evaluator():
    """
    Fake condition evaluator injected into ComplianceEngine.
    """
    evaluator = MagicMock()
    evaluator.evaluate = MagicMock()
    return evaluator


@pytest.fixture
def engine(evaluator):
    return ComplianceEngine(condition_evaluator=evaluator)


def make_rule(name="rule"):
    action = Action(
        name="noop",
        execute=MagicMock(),
    )

    return Rule(
        name=name,
        description="test rule",
        condition=MagicMock(),
        action=action,
        source=SourceEnum.PROCESS,
    )


class TestComplianceEnginePassFail:
    def test_rule_passes_when_condition_true(self, engine, evaluator, factsheets):
        rule = make_rule()

        evaluator.evaluate.return_value = True

        result = engine.run(
            rules={"r1": rule},
            factsheets=factsheets,
        )

        assert result["passed"] == [rule]
        assert result["failed"] == []

        evaluator.evaluate.assert_called_once_with(
            rule.condition,
            factsheets["process"],
        )
        rule.action.execute.assert_not_called()

    def test_rule_fails_when_condition_false(self, engine, evaluator, factsheets):
        rule = make_rule()

        evaluator.evaluate.return_value = False

        result = engine.run(
            rules={"r1": rule},
            factsheets=factsheets,
        )

        assert result["failed"] == [rule]
        assert result["passed"] == []

        evaluator.evaluate.assert_called_once_with(
            rule.condition,
            factsheets["process"],
        )
        rule.action.execute.assert_called_once_with(factsheets["process"])


class TestMultipleRules:
    def test_mixed_pass_and_fail(self, engine, evaluator, factsheets):
        passing = make_rule(name="pass")
        failing = make_rule(name="fail")

        def fake_evaluate(condition, facts):
            return condition is passing.condition

        evaluator.evaluate.side_effect = fake_evaluate

        result = engine.run(
            rules={
                "r1": passing,
                "r2": failing,
            },
            factsheets=factsheets,
        )

        assert result["passed"] == [passing]
        assert result["failed"] == [failing]

        passing.action.execute.assert_not_called()
        failing.action.execute.assert_called_once()


class TestFactRouting:
    def test_factsheet_selected_by_rule_source_value(self, engine, evaluator):
        rule = make_rule()

        factsheets = {
            "process": {"age": 99},
            "other": {"age": 0},
        }

        seen = {}

        def fake_evaluate(condition, facts) -> bool:
            seen["facts"] = facts
            return True

        evaluator.evaluate.side_effect = fake_evaluate

        engine.run(
            rules={"r1": rule},
            factsheets=factsheets,
        )

        assert seen["facts"] is factsheets["process"]


class TestExecutionContract:
    def test_action_called_only_on_failure(self, engine, evaluator, factsheets):
        rule = make_rule()

        evaluator.evaluate.return_value = False

        engine.run(
            rules={"r1": rule},
            factsheets=factsheets,
        )

        rule.action.execute.assert_called_once()

    def test_action_not_called_on_pass(self, engine, evaluator, factsheets):
        rule = make_rule()

        evaluator.evaluate.return_value = True

        engine.run(
            rules={"r1": rule},
            factsheets=factsheets,
        )

        rule.action.execute.assert_not_called()
