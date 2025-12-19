"""Argument Parser for Cli Arguments."""
import argparse
from typing import Callable, Any

from src.arg_parser.cli_arguments import CliArguments, _CliArgument
from src.custom_exceptions.custom_exception import InvalidCLI_ParserConfigurationError

default_check_interval = "default_process_check_interval"

defl_cli_args: list[_CliArgument] = CliArguments.cli_arguments.copy()

class CLI_ArgParser():
    """Argument parser for the application's CLI arguments."""


    def __init__(self, cli_arguments: list[_CliArgument] = defl_cli_args) -> None:
        """Initialize the CLI argument parser with parsed CLI arguments."""
        cli_arguments = CliArguments.cli_arguments.copy()
        self.parser = argparse.ArgumentParser()

        for group in CliArguments.mutually_exclusive_groups:
            mutually_exclusive_group = self.parser.add_mutually_exclusive_group(required=group.required)
            for item in group.name_or_flags:
                arg = CliArguments.get_arg_by_name_or_flag(item)
                mutually_exclusive_group.add_argument(*arg.get_flags(), **arg.to_kwargs())
                cli_arguments.remove(arg)

        for argument in cli_arguments:
            self.parser.add_argument(*argument.get_flags(), **argument.to_kwargs())

        self.args = self.parser.parse_args()


    def _get_argument(self, name_or_flag: str) -> Any | None:
        """Return the argument for the given CLI argument.

        Args:
            name_or_flag (str): CLI argument name or flag.
                can be passed as raw flag ('--create-process')
                or as Namespace key (create_process).
        Returns:
            argument value or None if no argument was found.
            """
        attr_name = name_or_flag.lstrip("-").replace("-", "_")
        return getattr(self.args, attr_name, None)


    def get_create_process_flag(self) -> bool:
        """Check if the create process argument was passed

        If True, this application is responsible for the audited process.
        If False, this application attached to an independent process.
        """
        if self._get_argument('pid'):
            return False
        elif self._get_argument('create-process'):
            return True
        msg = (f'Expected either a process ID as first positional argument'
               f' or "create-process" argument.')
        raise InvalidCLI_ParserConfigurationError(msg)

    def get_process_args(self) -> list[str] | int:
        """Return either the process ID or the commands to begin the process."""
        return self._get_argument('pid') if self._get_argument('pid')\
            else self._get_argument('create-process')


    def get_rules_args(self) -> list[str | int] | None:
        """Return a list of rule names or rule ids, potentially intermingled."""
        return self._get_argument('rules')

    def get_time_limit_arg(self) -> int | None:
        """Return the time limit for this application, in seconds."""
        return self._get_argument('time-limit')

    def get_interval_arg(self):
        """Return the time interval between audits for this application, in seconds."""
        return self._get_argument('interval')


if __name__ == '__main__':
    cli_arg_parser = CLI_ArgParser()
