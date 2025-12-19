import datetime
import pathlib
import tomllib
from dataclasses import dataclass
from typing import Dict, Callable

from src import rules_engine
from src.custom_exceptions.custom_exception import InvalidRuleException, InvalidRuleDataError, InvalidRuleExc
from src.utils.get_project_config import get_project_config
from src.process_handler import ProcessSnapshot
from src.rules_engine import Rule
from src.rules_engine.fact_sheet import FactSheet
from src.services import logger
from src.utils import project_root

FactCheck = Callable[[dict], bool]

@dataclass
class FailEvent:
    pid: int
    proc_name: str
    rule_id: int
    rule_name: str
    rule_message: str
    time_registered: datetime.datetime
    time_occured: datetime.datetime
    failed_condition: FactCheck





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

    def _resolve_condition(self, rule: rules_engine.Rule) -> FactCheck:
        """Resolve a rule condition."""
        if rule.evaluator:
            return rule.evaluator
        elif rule.parse_condition():
            return rule.parse_condition()
        else:
            msg = f'Expected evaluator or parse condition, got {type(rule)}'
            raise InvalidRuleExc(msg)

    def _process_rule_violation(self, facts: FactSheet, rule: rules_engine.Rule, condition: FactCheck) -> FailEvent:
        """Perform actions for a rule violation detection."""
        result = FailEvent(
            pid=facts.get('pid'),
            proc_name=facts.get('name'),
            rule_id=rule.id,
            rule_name=rule.name,
            rule_message=rule.message,
            time_registered=datetime.datetime.now(),
            time_occured=facts.get('snapshot_time'),
            failed_condition=condition
        )
        msg = (f'Process Failed Compliance [PID: {facts.get('pid')}, NAME: {facts.get('name')}]'
               f'\n\tRule violated: [ID: {rule.id}], NAME: {rule.name}]:'
               f'\n\t\tCondition: {str(condition)}'
               f'\n\t\tResult: {str(result)}')
        logger.info(msg)
        return result

    def check_compliance(self, fact_sheets: list[FactSheet], active_rules: dict[int, rules_engine.Rule])\
            -> list[dict[int, list[FailEvent]]]:
        """Compare facts to rules."""
        final_result = []
        for facts in fact_sheets:
            result_set = []
            for rule in active_rules.values():
                # Rule is derived from info or from evaluator
                condition = self._resolve_condition(rule)

                result = condition(facts.as_dict())
                if result: continue
                result_set.append(self._process_rule_violation(facts, rule, condition))

            final_result.append({facts.get('pid'): result_set})
        return final_result


if __name__ == "__main__":
    rules_engine = RulesEngine()