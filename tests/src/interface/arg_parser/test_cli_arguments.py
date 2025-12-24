import pytest

from interface.arg_parser.cli_arguments import _CliArgument, CliArguments, MutExGroup
from shared.custom_exceptions import InvalidCLI_ParserConfigurationError

class TestCliArgumentDataclass:
    def test_get_flags_with_str(self):
        arg = _CliArgument(name_or_flags="pid", type=int, help="Test PID")
        assert arg.get_flags() == ("pid",)

    def test_get_flags_with_tuple(self):
        arg = _CliArgument(name_or_flags=("-c", "--create-process"), type=str, help="Create process")
        assert arg.get_flags() == ("-c", "--create-process")

    def test_to_kwargs_with_optional_args(self):
        arg = _CliArgument(name_or_flags="pid", type=int, help="Test PID", nargs="?", default=5)
        kwargs = arg.to_kwargs()
        assert kwargs == {
            "type": int,
            "help": "Test PID",
            "nargs": "?",
            "default": 5
        }

    def test_to_kwargs_without_optional_args(self):
        arg = _CliArgument(name_or_flags="pid", type=int, help="Test PID")
        kwargs = arg.to_kwargs()
        assert kwargs == {
            "type": int,
            "help": "Test PID",
        }


class TestCliArguments:
    def test_get_arg_by_name_or_flag_with_string(self):
        arg = CliArguments.get_arg_by_name_or_flag("pid")
        assert arg.name_or_flags == "pid"

    def test_get_arg_by_name_or_flag_with_flag(self):
        arg = CliArguments.get_arg_by_name_or_flag("--create-process")
        assert "--create-process" in arg.name_or_flags

    def test_get_arg_by_name_or_flag_invalid_flag_raises(self):
        with pytest.raises(InvalidCLI_ParserConfigurationError):
            CliArguments.get_arg_by_name_or_flag("--not-a-flag")


class TestMutuallyExclusiveGroups:
    def test_mutually_exclusive_group_structure(self):
        group = CliArguments.mutually_exclusive_groups[0]
        assert isinstance(group, MutExGroup)
        assert set(group.name_or_flags) == {"pid", "--create-process"}
        assert group.required is True
