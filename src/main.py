"""A tool to audit the behavior of apps and their compliance with defined security rules."""
import time
from dataclasses import dataclass
from typing import Callable

from interface.arg_parser import CLI_ArgParser, CliContext
from core.compliance_engine import ComplianceEngine
from core.fact_processor.fact_processor import FactProcessor
from collection.process_handler.process_handler import AuditedProcess, ProcessHandler
from core.rules_engine.rules_engine import RulesEngine
from shared.services import logger
from collection.snapshot_manager import SnapshotManager


class Main:

    def __init__(self, rules_engine: RulesEngine, compliance_engine: ComplianceEngine,
                 cli_context: CliContext, process_handler: ProcessHandler,
                 snapshot_manager):
        self.rules_engine = rules_engine
        self.compliance_engine = compliance_engine
        self.cli_context = cli_context
        self.process_handler = process_handler
        self.snapshot_manager = snapshot_manager

        self.active_rules = None
        self.run_condition = None

    def setup(self) -> None:
        self.active_rules = rules_engine.match_rules(rules_engine.get_rules(), self.cli_context.rules)
        self.process_handler.add_process(AuditedProcess(self.cli_context.process))

        self.snapshot_manager.add_probe(self.process_handler.get_processes())

        self.run_condition = self.RunCondition(time.monotonic(), self.cli_context.time_limit,
                                          self.cli_context.interval, self.process_handler.num_active)


    @dataclass(slots=True)
    class RunCondition:
        start: float
        time_limit: int
        interval: int
        process_num_active_caller: Callable[[], int]

        def is_active(self) -> bool:
            if self.process_num_active_caller() == 0: return False
            if not self.time_limit: return True
            elif self.time_limit > time.monotonic() - self.start: return True
            return False



    def main(self, *, rules_engine, compliance_engine, cli_context: CliContext, process_handler,
             snapshot_manager) -> int:
        """The main function.

        - Load and filter rules based on cli arguments
        - Attach to process
        - Periodically check compliance
        - Record output
        """
        self.setup()

        try:
            while self.run_condition.is_active():
                loop_start = time.monotonic()

                ps_output = snapshot_manager.get_all_snapshots()



                ### Unit Test Snapshot Manager and Probes, make sure package code is clean






                facts: list = fact_processor.parse_facts(ps_output)


                output = compliance_engine.run(self.active_rules, facts)

                print(output)

                elapsed = time.monotonic() - loop_start
                time.sleep(max(0, self.run_condition.interval - int(elapsed)))

        except KeyboardInterrupt:
            #Do whatever i need to safely handle this
            # allow multiple interrupts? Daemon mode?
            logger.info(f'Keyboard Interrupt, Shutting down')
        finally:
            if cli_context.create_process_flag:
                # python created the process
                process_handler.shutdown_all()
            else:
                # continue process, end python.
                process_handler.remove_all()

        return 0


if __name__ == "__main__":
    fact_processor = FactProcessor()

    rules_engine = RulesEngine(fact_processor.get_possible_facts)
    compliance_engine = ComplianceEngine()
    cli_arg_parser = CLI_ArgParser()
    process_handler = ProcessHandler()
    snapshot_manager = SnapshotManager()


    main(
        rules_engine=rules_engine,
        compliance_engine=compliance_engine,
        cli_context=cli_arg_parser.get_context(),
        process_handler=process_handler,
        snapshot_manager=snapshot_manager
    )


