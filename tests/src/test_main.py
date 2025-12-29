import pytest
from unittest.mock import MagicMock, patch

from core.fact_processor.fact_registry import FactRegistry
from core.rules_engine.model.rule import Rule, Action, SourceEnum
from main import Main
from shared._common.operators import Operator


class FakeSnapshot:
    def __init__(self, data):
        self.data = data


class TestMainE2E:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self):
        # Real Rule object
        self.rule = Rule(
            name="TestRule",
            description="desc",
            condition=MagicMock(),
            action=Action(name="noop", execute=MagicMock()),
            source=SourceEnum.PROCESS,
        )

        # SnapshotManager returns realistic snapshots
        self.fake_snapshot_manager = MagicMock()
        self.fake_snapshot_manager.get_all_snapshots.return_value = {
            "process": [FakeSnapshot({"age": 42})]
        }

        # FactProcessor converts snapshots into dicts
        self.fake_fact_processor = MagicMock()
        self.fake_fact_processor.parse_facts.return_value = {
            "process": {"age": 42}
        }

        # ComplianceEngine consumes factsheets and returns results
        self.fake_compliance_engine = MagicMock()
        self.fake_compliance_engine.run.return_value = {"passed": [self.rule], "failed": []}

        # RulesEngine returns active rules
        self.fake_rules_engine = MagicMock()
        self.fake_rules_engine.get_rules.return_value = {"r1": self.rule}
        self.fake_rules_engine.match_rules.return_value = {"r1": self.rule}

        self.fake_process_handler = MagicMock()
        # Simulate process count
        self.fake_process_handler.num_active.return_value = 1
        # Return a fake process object when asked
        self.fake_process_handler.get_processes.return_value = ["fake_proc"]
        # Track add/remove calls
        self.fake_process_handler.add_process.return_value = None
        self.fake_process_handler.remove_all.return_value = None
        self.fake_process_handler.shutdown_all.return_value = None

        # CLI context
        class FakeCLI:
            rules = []
            process = 123
            time_limit = 0.01
            interval = 0.01
            create_process_flag = False

        self.cli_context = FakeCLI()

    @patch("main.AuditedProcess")
    def test_main_e2e_pipeline(self, MockProcess):
        # Mock AuditedProcess so no real PID is used
        mock_proc = MagicMock()
        MockProcess.return_value = mock_proc

        main = Main(
            rules_engine=self.fake_rules_engine,
            compliance_engine=self.fake_compliance_engine,
            cli_context=self.cli_context,
            process_handler=self.fake_process_handler,
            snapshot_manager=self.fake_snapshot_manager,
            fact_processor=self.fake_fact_processor,  # inject fake processor
        )

        result = main.main()

        # Assertions
        assert result == 0
        self.fake_fact_processor.parse_facts.assert_called_once_with(
            self.fake_snapshot_manager.get_all_snapshots()
        )
        self.fake_compliance_engine.run.assert_called_once()
        self.fake_process_handler.add_process.assert_called_once_with(mock_proc)
        self.fake_process_handler.remove_all.assert_called_once()



    @patch("main.AuditedProcess")
    @patch("time.sleep", return_value=None)  # prevent actual sleeping
    def test_main_e2e_minimal_realistic(self, mock_sleep, MockProcess):
        # Mock AuditedProcess so no real PID is used
        mock_proc = MagicMock()
        MockProcess.return_value = mock_proc

        from core.fact_processor.fact_processor import FactProcessor
        from core.compliance_engine import ComplianceEngine

        # Real FactProcessor
        fact_registry = FactRegistry()
        fact_registry.register(
            path="age",
            type_= int,
            source=SourceEnum.PROCESS,
            allowed_operators=set(Operator)
        )
        print(f'debug test'
              f'\n'
              f'{fact_registry.all_facts()}')

        fact_processor = FactProcessor(fact_registry)

        # Real ComplianceEngine
        compliance_engine = ComplianceEngine()

        # Minimal realistic snapshot
        snapshot_data = {"age": 42}

        class SimpleSnapshot:
            def __init__(self, data: dict):
                for key, value in data.items():
                    setattr(self, key, value)

        fake_snapshot_manager = MagicMock()
        fake_snapshot_manager.get_all_snapshots.return_value = {
            "process": [SimpleSnapshot(snapshot_data)]
        }

        # Create a simple Rule that matches the snapshot
        from core.rules_engine.rule_builder.parsers import cond
        rule = Rule(
            name="AgeRule",
            description="Checks age",
            condition=cond("age == 42"),
            action=Action(name="noop", execute=lambda facts: None),
            source=SourceEnum.PROCESS,
        )

        rule2 = Rule(
            name="AgeRule",
            description="Checks age",
            condition=cond("age == 50"),
            action=Action(name="noop", execute=lambda facts: None),
            source=SourceEnum.PROCESS,
        )

        # Patch RulesEngine to return our rule
        fake_rules_engine = MagicMock()
        fake_rules_engine.get_rules.return_value = {"r1": rule, "r2": rule2}
        fake_rules_engine.match_rules.return_value = {"r1": rule, "r2": rule2}

        # Fake ProcessHandler
        fake_process_handler = MagicMock()
        fake_process_handler.num_active.return_value = 1
        fake_process_handler.get_processes.return_value = ["fake_proc"]

        # CLI context
        class FakeCLI:
            rules = []
            process = 123
            time_limit = 0.01
            interval = 0.01
            create_process_flag = False

        cli_context = FakeCLI()

        main = Main(
            rules_engine=fake_rules_engine,
            compliance_engine=compliance_engine,
            cli_context=cli_context,
            process_handler=fake_process_handler,
            snapshot_manager=fake_snapshot_manager,
            fact_processor=fact_processor,
        )

        # Patch RunCondition to run the loop exactly once
        with patch.object(main, "run_condition", autospec=True) as mock_rc:
            mock_rc.is_active.side_effect = [True, False]

            result = main.main()

        # Assertions
        assert result == 0

        # FactProcessor should parse snapshots correctly
        parsed_facts = fact_processor.parse_facts(
            fake_snapshot_manager.get_all_snapshots()
        )
        assert parsed_facts["process"]["age"] == 42

        # ComplianceEngine run returns correct results
        output = compliance_engine.run({"r1": rule, "r2": rule2}, parsed_facts)
        assert output["passed"] == [rule]
        assert output["failed"] == [rule2]

        # ProcessHandler add/remove calls
        fake_process_handler.add_process.assert_called_once_with(mock_proc)
        fake_process_handler.remove_all.assert_called_once()


