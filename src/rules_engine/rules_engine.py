import pathlib

from src import rules_engine
from src.custom_exceptions.custom_exception import InvalidRuleException


class RulesEngine():
    """Control Access and Understanding of Rules."""
    def __init__(self):
        pass

    def get_rules(self):
        pass

    def filter_rules(self, rules: dict[int, rules_engine.Rule], filters: list['str']):
        for rule_id in rules:
            try:

                pass
            except Exception as err:
                raise InvalidRuleException(err, rule_id)
                pass

    def check_complaince(self, process, active_rules: dict[int, rules_engine.Rule]):
        pass

    def load_rules_from_toml(self, rules_path: pathlib.Path):
        pass



if __name__ == "__main__":
    rules_engine = RulesEngine()