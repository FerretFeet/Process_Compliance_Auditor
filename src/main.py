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
from interface.arg_parser.cli_arg_parser import CliArgParser, CliContext
from shared.custom_exceptions import FactNotFoundError
from shared.services import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.probes.snapshot.base import BaseSnapshot


@dataclass(slots=True)
class EngineBundle:
    """Collection of core engines responsible for rule evaluation and compliance."""

    rules: RulesEngine
    compliance: ComplianceEngine
    facts: FactProcessor


@dataclass(slots=True)
class RuntimeBundle:
    """Runtime services responsible for interacting with the operating system."""

    process_handler: ProcessHandler
    snapshot_manager: SnapshotManager


@dataclass(slots=True)
class AppContext:
    """Immutable application configuration derived from CLI arguments."""

    cli: CliContext


@dataclass(slots=True)
class RunCondition:
    """Condition for the main loop."""

    start: float
    time_limit: int
    interval: int
    process_num_active_caller: Callable[[], int]

    def is_active(self) -> bool:
        """
        Check if the timer is exceeded.

        Returns:
            bool: True if the timer is Not exceeded, False otherwise.

        """
        if self.process_num_active_caller() == 0:
            return False
        return bool(not self.time_limit or self.time_limit > time.monotonic() - self.start)


class Main:
    """Main project loop runner."""

    def __init__(
        self,
        *,
        engines: EngineBundle,
        runtime: RuntimeBundle,
        context: AppContext,
    ) -> None:
        """Initialize the main loop runner."""
        self.rules_engine = engines.rules
        self.compliance_engine = engines.compliance
        self.fact_processor = engines.facts

        self.process_handler = runtime.process_handler
        self.snapshot_manager = runtime.snapshot_manager

        self.cli_context = context.cli

        self.active_rules = None
        self.run_condition = None

    def setup(self) -> None:
        """
        Set up conditions for main loop.

        - Sets active rules based on cli arguments,
        - Creates or Finds and tracks process,
        - Sets the run condition based on cli arguments.
        """
        self.active_rules = self.rules_engine.match_rules(
            self.rules_engine.get_rules(),
            self.cli_context.rules,
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
        Run the main function.

        - Load and filter rules based on cli arguments
        - Create or find process
        - Periodically check compliance
        - Record output
        """
        self.setup()

        try:
            while self.run_condition.is_active():
                loop_start = time.monotonic()

                ps_output: dict[str, list[BaseSnapshot]] = self.snapshot_manager.get_all_snapshots()
                facts: dict[str, dict[str, Any]] = self.fact_processor.parse_facts(ps_output)

                # TODO: #noqa: FIX002, TD003, TD002
                # Fix code documentation: fully document all classes and functions to this point
                # Fix logging so only log errors if not also raising exception, instead of both
                # Test fact processor package - create a fake process snapshot and put it into
                # the expected format and try to parse

                output = self.compliance_engine.run(self.active_rules, facts)
                print("\n\t==============Compliance Report:\t==============\n\n")  # noqa: T201
                for k, v in output.items():
                    print(f"{k}:\n")  # noqa: T201
                    for _val in v:
                        print(f"\t{_val.name} : {_val.description}\n")  # noqa: T201

                elapsed = time.monotonic() - loop_start
                time.sleep(max(0, self.run_condition.interval - int(elapsed)))

        except KeyboardInterrupt:
            # Do whatever i need to safely handle this
            # allow multiple interrupts? Daemon mode?
            logger.info("Keyboard Interrupt, Shutting down")
        except FactNotFoundError as err:
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

    engines = EngineBundle(
        rules=RulesEngine(fact_processor.get_all_facts),
        compliance=ComplianceEngine(),
        facts=fact_processor,
    )

    runtime = RuntimeBundle(
        process_handler=ProcessHandler(),
        snapshot_manager=SnapshotManager(),
    )

    cli_arg_parser = CliArgParser()
    context = AppContext(
        cli=cli_arg_parser.get_context(),
    )

    main = Main(
        engines=engines,
        runtime=runtime,
        context=context,
    )
    main.main()
