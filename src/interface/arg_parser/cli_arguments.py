"""Cli argument definitions and methods."""

import argparse
import typing
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from shared.custom_exceptions.custom_exception import InvalidCliParserConfigurationError
from shared.utils import cfg

if TYPE_CHECKING:
    from collections.abc import Callable

default_interval = cfg.get("default_process_check_interval")
default_time_limit = cfg.get("default_process_time_limit")


@dataclass
class _CliArgument:
    """Cli argument dataclass."""

    name_or_flags: str | tuple[str, ...]
    type: Callable[[str], Any]
    help: str
    nargs: str | None = None
    default: str = None

    def get_flags(self) -> tuple[str, ...]:
        """Get the flags for this argument as a tuple."""
        return (self.name_or_flags,) if isinstance(self.name_or_flags, str) else self.name_or_flags

    def to_kwargs(self) -> dict[str, Any]:
        """For use in argparser."""
        kwargs = {
            "type": self.type,
            "help": self.help,
        }

        if self.nargs is not None:
            kwargs["nargs"] = self.nargs

        if self.default is not None:
            kwargs["default"] = self.default

        return kwargs


@dataclass
class MutExGroup:
    """Grouping of mutually exclusive arguments."""

    name_or_flags: list[str]
    required: bool = False


class CliArguments:
    """Static class for Cli Argument Groupings and Methods."""

    cli_arguments: tuple[_CliArgument] = (
        _CliArgument(
            name_or_flags="pid",
            nargs="?",
            type=int,
            help="Process ID to attach to. If omitted, use -c to create a process.",
        ),
        _CliArgument(
            name_or_flags=("-c", "--create-process"),
            type=str,
            help="Executable and arguments to create a new process.",
        ),
        _CliArgument(
            name_or_flags=("-t", "--time_limit"),
            type=int,
            nargs="?",
            default=default_time_limit,
            help="Time limit in seconds. Default to infinity.",
        ),
        _CliArgument(
            name_or_flags=("-i", "--interval"),
            nargs="?",
            type=int,
            default=default_interval,
            help=f"Time interval in seconds between test checks."
            f" Default is {default_interval}.",
        ),
        _CliArgument(
            name_or_flags=("-r", "--rules"),
            nargs="+",
            type=str,
            help="Rule names or ids to test. Defaults to all available rules.",
        ),
    )

    mutually_exclusive_groups: typing.ClassVar[list[MutExGroup]] = [
        MutExGroup(["pid", "--create-process"], required=True),
    ]

    @staticmethod
    def get_arg_by_name_or_flag(flag: str) -> _CliArgument:
        """
        Return an argument matching the flag passed in.

        Args:
            flag (str): The flag passed in

        Returns:
            _CliArgument: The argument matching the flag

        Raises:
            InvalidCliParserConfigurationError: If the flag is not valid.

        """
        for arg in CliArguments.cli_arguments:
            if isinstance(arg.name_or_flags, str):
                if flag == arg.name_or_flags:
                    return arg
            elif isinstance(arg.name_or_flags, (tuple, list, set)):
                if flag in arg.name_or_flags:
                    return arg
            else:
                msg = "Expected arg.name_or_flags to be str or tuple/list/set"
                raise InvalidCliParserConfigurationError(msg)
        msg = f"flag not found in cli arguments: {flag}"
        raise InvalidCliParserConfigurationError(msg)
