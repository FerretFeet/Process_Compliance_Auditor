import sys

import pytest

from interface.arg_parser import CLI_ArgParser


class TestCLIArgParserInitialization:
    def test_parser_initializes_with_pid(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "1234"])
        parser = CLI_ArgParser()
        assert parser.get_process_args() == 1234
        assert parser.get_create_process_flag() is False

    def test_parser_initializes_with_create_process(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "--create-process", "python", "script.py"])
        parser = CLI_ArgParser()
        assert parser.get_process_args() == ["python", "script.py"]
        assert parser.get_create_process_flag() is True

    def test_parser_exits_systemexit_if_neither_provided(self, monkeypatch):
        """argparse should call sys.exit(2) if required mutually exclusive argument is missing"""
        monkeypatch.setattr(sys, "argv", ["program"])
        with pytest.raises(SystemExit) as e:
            CLI_ArgParser()
        assert e.type == SystemExit
        assert e.value.code == 2


class TestCLIArgParserArguments:
    def test_rules_argument(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "1234", "-r", "rule1", "rule2"])
        parser = CLI_ArgParser()
        assert parser.get_rules_args() == ["rule1", "rule2"]

    def test_time_limit_argument(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "1234", "-t", "100"])
        parser = CLI_ArgParser()
        assert parser.get_time_limit_arg() == 100

    def test_interval_argument(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "1234", "-i", "15"])
        parser = CLI_ArgParser()
        assert parser.get_interval_arg() == 15


class TestCLIArgParserFlags:
    def test_create_process_flag_true(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "--create-process", "python", "script.py"])
        parser = CLI_ArgParser()
        assert parser.get_create_process_flag() is True

    def test_create_process_flag_false(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "5678"])
        parser = CLI_ArgParser()
        assert parser.get_create_process_flag() is False


class TestCLIArgParserProcessArgs:
    def test_process_args_pid(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "5678"])
        parser = CLI_ArgParser()
        assert parser.get_process_args() == 5678

    def test_process_args_create_process(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["program", "--create-process", "python", "script.py"])
        parser = CLI_ArgParser()
        assert parser.get_process_args() == ["python", "script.py"]
