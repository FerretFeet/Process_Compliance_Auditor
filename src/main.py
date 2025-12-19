"""A tool to audit the behavior of apps and their compliance with defined security rules."""
import os
import platform
import time
import tomllib
from pathlib import Path

from src import utils
from src.custom_exceptions.custom_exception import InvalidProjectConfigurationError
from src.process_handler import ProcessSnapshot
from src.process_handler.process_handler import AuditedProcess
from src.rules_engine import FactSheet


def get_project_config(fp: Path = utils.project_root / 'config' / 'project_config.toml'):
    """Get the global config object."""
    with Path.open(fp, 'rb') as f:
        config = tomllib.load(f).get('project_config', {})
    if not config:
        raise InvalidProjectConfigurationError()
    for key, val in config.items():
        if val == "None":
            config[key] = None

    config.setdefault('os', platform.system())
    return config

def main(rules_engine, cli_arg_parser, process_handler) -> int:
    """The main function.

    - Load and filter rules based on cli arguments
    - Attach to process
    - Periodically check compliance
    - Record output
    """
    process_args = cli_arg_parser.get_process_args()
    process_interval = cli_arg_parser.get_interval_arg()
    time_limit = cli_arg_parser.get_time_limit_arg()

    active_rules = rules_engine.filter_rules(rules_engine.get_rules(), cli_arg_parser.get_rules_args())

    process_handler.add_process(AuditedProcess(process_args))

    try:
        start = time.monotonic()
        while (time_limit is None or time_limit > time.monotonic() - start)\
                and process_handler.num_active() > 0:
            loop_start = time.monotonic()

            ps_output: list[ProcessSnapshot] = process_handler.get_snapshot()
            facts = [FactSheet(o) for o in ps_output]

            output = rules_engine.check_compliance(facts, active_rules)
            # do other things with the result besides logging
            print(output)

            elapsed = time.monotonic() - loop_start
            time.sleep(max(0, process_interval - elapsed))

    except KeyboardInterrupt:
        #Do whatever i need to safely handle this
        # allow multiple interrupts? Daemon mode?
    finally:
        if cli_arg_parser.get_create_process_flag():
            # python created the process
            process_handler.shutdown_all()
        else:
            # continue process, end python.
            process_handler.detach_all()

    return 0


if __name__ == "__main__":
    project_config = get_project_config()

    rules_engine = RulesEngine()
    cli_arg_parser = CLI_ArgParser()
    process_handler = ProcessHandler(

    main(rules_engine, cli_arg_parser, process_handler)


