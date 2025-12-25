from unittest.mock import MagicMock

import psutil
import pytest

from core.probes.snapshot.process_snapshot.process_snapshot import ProcessSnapshot
from core.rules_engine.model import Rule, Action
from core.rules_engine.model.condition import Condition
from core.rules_engine.model.field import FieldRef
from core.rules_engine.model.rule import SourceEnum
from shared._common.operators import Operator


@pytest.fixture
def mock_proc():
    """Provides a mocked psutil.Process object."""
    proc = MagicMock(spec=psutil.Process)
    proc.pid = 999
    proc.name.return_value = "test_proc"
    proc.create_time.return_value = 12345.67
    return proc

@pytest.fixture
def empty_snap():
    """Standard ProcessSnapshot skeleton."""
    return ProcessSnapshot(
        pid=1234,
        name="test_proc",
        create_time=0.0
    )

@pytest.fixture
def toml_data(sample_rule):
    return {
        "rules": [
            {
                "name": sample_rule.name,
                "description": sample_rule.description,
                "group": sample_rule.group,
                "model": sample_rule.condition.describe(),
                "action": lambda facts: facts.update({"access_granted": True}),
                "source": 'process'
            }
        ]
    }

@pytest.fixture
def sample_rule():
    fake_condition = Condition(FieldRef("cpu_count", int), Operator.EQ, "4")

    return Rule(
        name="cpu_check",
        description="Count cpus",
        condition=fake_condition,  # Condition or ConditionSet
        action=Action(name="block_access", execute=lambda facts: facts.update({"blocked": True})),
        group="cpu",
        source=[SourceEnum.PROCESS]
    )
