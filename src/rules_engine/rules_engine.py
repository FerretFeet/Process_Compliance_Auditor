import pathlib
import tomllib
from typing import Dict

from src import rules_engine
from src.custom_exceptions.custom_exception import InvalidRuleException, InvalidRuleDataError
from src.main import get_project_config
from src.rules_engine import Rule
from src.services import logger
from src.utils import project_root


class RulesEngine:
    """Control Access and Understanding of Rules."""
    def __init__(self, *,
                 rules_path: pathlib.Path = project_root / get_project_config()['rules_path']
                 ) -> None:
        self.rules_path = rules_path
        self.rules = self.get_rules()
        self.rules_name_lookup = {rule.name: rule for rule in self.rules.values()}

    def get_rules(self) -> Dict[int, rules_engine.Rule]:
        """Return all rules defined in project.toml.

        Loads rules if not already loaded.
        """
        if self.rules is not None:
            return self.rules
        rules = self._load_rules_from_toml(self.rules_path)
        return {rule.id: rule for rule in rules}

    def _load_rules_from_toml(self, rules_path: pathlib.Path) -> list[rules_engine.Rule]:
        """Load rules from project.toml.

        Returns all rules defined in project.toml.
        """
        with rules_path.open('rb') as f:
            uf_rules = tomllib.load(f).get('rules', [])
        if not isinstance(uf_rules, list):
            raise InvalidRuleDataError("Expected 'rules' to be a list of tables in TOML")
        rules = []
        for rule_data in uf_rules:
            try:
                rules.append(rules_engine.Rule.from_toml(rule_data))
            except InvalidRuleDataError as e:
                logger.warning(f"Skipping invalid rule: {e}")
        return rules



    def filter_rules(self, rules: dict[int, rules_engine.Rule], filters: list[str | int] | None)\
            -> dict[int, rules_engine.Rule]:
        """Return only the rules matching the given filters.

        Args:
            rules: rules to filter
            filters: filters to apply. Can be rule.id or rule.name
                If filter is None, return all rules.
        """
        if filters is None:
            return rules
        active_rules = dict[int, rules_engine.Rule]()
        for _filter in filters:
            try:
                if isinstance(_filter, int): # is rule id
                    active_rules[_filter] = rules[_filter]
                elif isinstance(_filter, str):
                    rule = self.rules_name_lookup[_filter]
                    active_rules[rule.id] = rule
            except Exception as err:
                raise InvalidRuleException(err, _filter)
        return active_rules

    def check_complaince(self, process, active_rules: dict[int, rules_engine.Rule]):
        pass


if __name__ == "__main__":
    rules_engine = RulesEngine()