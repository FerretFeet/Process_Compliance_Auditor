"""Argument Parser for Cli Arguments."""

import argparse
from dataclasses import dataclass
from typing import Any

from interface.arg_parser.cli_arguments import CliArguments, _CliArgument
from shared.custom_exceptions import InvalidCLI_ParserConfigurationError

default_check_interval = "default_process_check_interval"

defl_cli_args: tuple[_CliArgument] = CliArguments.cli_arguments


class CLI_ArgParser:
    """Argument parser for the application's CLI arguments."""

    def __init__(self, cli_arguments: tuple[_CliArgument] = defl_cli_args) -> None:
        """Initialize the CLI argument parser with parsed CLI arguments."""
        cli_arguments = list(cli_arguments)
        self.parser = argparse.ArgumentParser()

        for group in CliArguments.mutually_exclusive_groups:
            mutually_exclusive_group = self.parser.add_mutually_exclusive_group(
                required=group.required,
            )
            for item in group.name_or_flags:
                arg = CliArguments.get_arg_by_name_or_flag(item)
                mutually_exclusive_group.add_argument(*arg.get_flags(), **arg.to_kwargs())
                cli_arguments.remove(arg)

        for argument in cli_arguments:
            self.parser.add_argument(*argument.get_flags(), **argument.to_kwargs())

        self.args = self.parser.parse_args()

    def _get_argument(self, name_or_flag: str) -> Any | None:
        """
        Return the argument for the given CLI argument.

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
        """
        Check if the create process argument was passed.

        If True, this application is responsible for the audited process.
        If False, this application attached to an independent process.
        """
        if self._get_argument("pid"):
            return False
        if self._get_argument("create-process"):
            return True
        # FIXME
        # This line should be unnecessary due to mut-ex group
        # Dec 21
        msg = (
            "Expected either a process ID as first positional argument"
            ' or "create-process" argument.'
        )
        raise InvalidCLI_ParserConfigurationError(msg)

    def get_process_args(self) -> list[str] | int:
        """Return either the process ID or the commands to begin the process."""
        return (
            self._get_argument("pid")
            if self._get_argument("pid")
            else self._get_argument("create-process")
        )

    def get_rules_args(self) -> list[str | int] | None:
        """Return a list of rule_builder names or rule_builder ids, potentially intermingled."""
        return self._get_argument("rules")

    def get_time_limit_arg(self) -> int | None:
        """Return the time limit for this application, in seconds."""
        return self._get_argument("time-limit")

    def get_interval_arg(self) -> int | None:
        """Return the time interval between audits for this application, in seconds."""
        return self._get_argument("interval")

    def get_context(self):
        return CliContext(
            process=self.get_process_args(),
            create_process_flag=self.get_create_process_flag(),
            interval=self.get_interval_arg(),
            time_limit=self.get_time_limit_arg(),
            rules=self.get_rules_args(),
        )


@dataclass
class CliContext:
    process: list[str] | int
    create_process_flag: bool
    interval: int
    time_limit: int
    rules: list[str]


if __name__ == "__main__":
    cli_arg_parser = CLI_ArgParser()
