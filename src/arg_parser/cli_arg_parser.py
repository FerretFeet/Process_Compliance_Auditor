import argparse

import src

default_check_interval = "default_process_check_interval"

def _rule_type(x):
    return int(x) if x.isdigit() else x

class CLI_ArgParser():
    def __init__(self):

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument(
            "pid", nargs="?", type=int,
            help="Process ID to attach to. If omitted, use -c to create a process."
        )

        self.parser.add_argument(
            "-c", "--create-process", nargs=argparse.REMAINDER,
            help="Executable and arguments to create a new process."
        )

        self.parser.add_argument("-t", "--time_limit", type=int,
                            help="Time limit in seconds. Default to infinity.")

        self.parser.add_argument("-i", "--interval", type=int,
                            help=f"Time interval in seconds between test checks."
                                 f" Default is {src.PROJECT_CONFIG.get(default_check_interval)}.")

        self.parser.add_argument("-r", "--rule", nargs="+", type=_rule_type,
                            help="Rule names or ids to test.")




        self.args = self.parser.parse_args()

    def get_create_process_flag(self):
        pass

    def get_process_args(self):
        pass

    def get_rules_args(self):
        pass

    def get_time_limit_arg(self):
        pass
    def get_interval_arg(self):
        pass

