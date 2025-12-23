"""A tool to audit the behavior of apps and their compliance with defined security rules."""
import time
from typing import cast, Mapping

from src.arg_parser.cli_arg_parser import CLI_ArgParser, CliContext
from src.compliance_engine import ComplianceEngine
from src.compliance_engine.fact_sheet import FactSheet
from src.fact_processor.fact_processor import FactProcessor
from src.fact_processor.fact_registry import FactSpec
from src.process_handler import ProcessSnapshot
from src.process_handler.process_handler import AuditedProcess, ProcessHandler
from src.rules_engine.rules_engine import RulesEngine, FactProvider, FactSpecProtocol
from src.services import logger
from src.utils.get_project_config import get_project_config


def main(*, rules_engine, compliance_engine, cli_context: CliContext, process_handler) -> int:
    """The main function.

    - Load and filter rules based on cli arguments
    - Attach to process
    - Periodically check compliance
    - Record output
    """
    active_rules = rules_engine.match_rules(rules_engine.get_rules(), cli_context.rules)

    process_handler.add_process(AuditedProcess(cli_context.process))

    try:
        start = time.monotonic()
        time_limit = cli_context.time_limit
        interval = cli_context.interval
        while (time_limit is None or time_limit > time.monotonic() - start)\
                and process_handler.num_active() > 0:
            loop_start = time.monotonic()

            ps_output: list[ProcessSnapshot] = process_handler.get_snapshot()
            facts = [FactSheet(o) for o in ps_output]

            output = compliance_engine.run(active_rules, facts)
            # do other things with the result besides logging
            print(output)

            elapsed = time.monotonic() - loop_start
            time.sleep(max(0, interval - int(elapsed)))

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
    project_config = get_project_config()
    fact_processor = FactProcessor()




    rules_engine = RulesEngine(fact_processor.get_possible_facts()) #type: ignore
    compliance_engine = ComplianceEngine()
    cli_arg_parser = CLI_ArgParser()
    process_handler = ProcessHandler()

    main(
        rules_engine=rules_engine,
        compliance_engine=compliance_engine,
        cli_context=cli_arg_parser.get_context(),
        process_handler=process_handler
    )


