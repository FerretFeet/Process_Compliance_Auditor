"""A tool to audit the behavior of apps and their compliance with defined security rules."""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from collection.process_handler.process_handler import AuditedProcess, ProcessHandler
from collection.snapshot_manager.snapshot_manager import SnapshotManager
from core.compliance_engine import ComplianceEngine
from core.fact_processor.fact_processor import FactProcessor
from core.probes.probes import ProbeLibrary
from core.rules_engine.rules_engine import RulesEngine
from interface.arg_parser.cli_arg_parser import CLI_ArgParser, CliContext
from shared.custom_exceptions import FactNotFoundException
from shared.services import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.probes.snapshot.base import BaseSnapshot


@dataclass(slots=True)
class RunCondition:
    start: float
    time_limit: int
    interval: int
    process_num_active_caller: Callable[[], int]

    def is_active(self) -> bool:
        if self.process_num_active_caller() == 0:
            return False
        return bool(not self.time_limit or self.time_limit > time.monotonic() - self.start)


class Main:

    def __init__(
        self,
        rules_engine: RulesEngine,
        compliance_engine: ComplianceEngine,
        cli_context: CliContext,
        process_handler: ProcessHandler,
        snapshot_manager: SnapshotManager,
        fact_processor: FactProcessor,
    ) -> None:
        self.rules_engine = rules_engine
        self.compliance_engine = compliance_engine
        self.cli_context = cli_context
        self.process_handler = process_handler
        self.snapshot_manager = snapshot_manager
        self.fact_processor = fact_processor

        self.active_rules = None
        self.run_condition = None

    def setup(self) -> None:
        self.active_rules = self.rules_engine.match_rules(
            self.rules_engine.get_rules(), self.cli_context.rules,
        )
        self.process_handler.add_process(AuditedProcess(self.cli_context.process))
        process_probes = [
            ProbeLibrary.process_probe(proc.process)
            for proc in self.process_handler.get_processes()
        ]
        self.snapshot_manager.add_probes(process_probes)

        self.run_condition = RunCondition(
            time.monotonic(),
            self.cli_context.time_limit,
            self.cli_context.interval,
            self.process_handler.num_active,
        )

    def main(self) -> int:
        """
        The main function.

        - Load and filter rules based on cli arguments
        - Attach to process
        - Periodically check compliance
        - Record output
        """
        self.setup()

        try:
            while self.run_condition.is_active():
                loop_start = time.monotonic()

                ps_output: dict[str, list[BaseSnapshot]] = self.snapshot_manager.get_all_snapshots()
                facts: dict[str, dict[str, Any]] = self.fact_processor.parse_facts(ps_output)

                # TODO:
                # Fix code documentation: fully document all classes and functions to this point
                # Remove Strict from config or make as parameter to functions that use it
                # Fix logging so only log errors if not also raising exception, instead of both
                # Test fact processor package - create a fake process snapshot and put it into the expected format and try to parse

                output = self.compliance_engine.run(self.active_rules, facts)
                print(f'\n\t==============Compliance Report:\t==============\n\n')
                for k, v in output.items():
                    print(f'{k}:\n')
                    for _val in v:
                        print(f'\t{_val.name} : {_val.description}\n')


                elapsed = time.monotonic() - loop_start
                time.sleep(max(0, self.run_condition.interval - int(elapsed)))

        except KeyboardInterrupt:
            # Do whatever i need to safely handle this
            # allow multiple interrupts? Daemon mode?
            logger.info("Keyboard Interrupt, Shutting down")
        except FactNotFoundException as err:
            logger.error(err)
        finally:
            if self.cli_context.create_process_flag:
                # python created the process
                self.process_handler.shutdown_all()
            else:
                # continue process, end python.
                self.process_handler.remove_all()

        return 0


if __name__ == "__main__":
    fact_processor = FactProcessor()

    rules_engine = RulesEngine(fact_processor.get_all_facts)
    compliance_engine = ComplianceEngine()
    cli_arg_parser = CLI_ArgParser()
    process_handler = ProcessHandler()
    snapshot_manager = SnapshotManager()

    main = Main(
        rules_engine=rules_engine,
        compliance_engine=compliance_engine,
        cli_context=cli_arg_parser.get_context(),
        process_handler=process_handler,
        snapshot_manager=snapshot_manager,
        fact_processor=fact_processor,
    )
    main.main()
