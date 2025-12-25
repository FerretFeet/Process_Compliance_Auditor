import datetime
import pathlib
import tomllib
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

from shared._common.facts import FactSpecProtocol
from shared.custom_exceptions import RuleWithNoAvailableFactException, InvalidRuleDataError, InvalidRuleFilterException
from core.rules_engine.builtin_rules import ALL_BUILTIN_RULES
from core.rules_engine.model import Rule
from shared.services import logger
from shared.utils import project_root, cfg

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


FactProvider = Callable[[], Mapping[str, FactSpecProtocol]]

_rules_file_path = project_root / cfg.get('rules_path')

_builtin_rules = ALL_BUILTIN_RULES

class RulesEngine:
    """Control Access and Understanding of Rules."""
    def __init__(self, fact_provider: FactProvider, *,
                 toml_rules_path: pathlib.Path = _rules_file_path,
                 builtin_rules: list[Rule] = _builtin_rules
                 ) -> None:
        self.fact_provider = fact_provider
        self.builtin_rules = builtin_rules
        self.toml_rules_path = toml_rules_path
        self.rules = None
        self.rules = self.get_rules()
        self.rules_name_lookup = {rule.name: rule for rule in self.rules.values()}

        self.validate_rules()


    def get_rules(self) -> dict[str, Rule]:
        """Return all rules defined in project.toml.

        Loads rules if not already loaded.
        """
        if self.rules is None:
            rules = self._load_rules_from_toml(self.toml_rules_path)
            self.rules = {rule.id: rule
                    for rule in rules + self.builtin_rules}
        return self.rules


    def validate_rules(self):
        """Check that rules correspond to available facts."""
        if self.fact_provider is None:
            logger.warning(f'No fact_provider defined for {type(self).__name__}. Validation skipped.')
            return
        available_facts = self.fact_provider()
        errors: list = []
        valids = {}
        for rule in self.rules.values():
            msg = f"Invalid rule: {rule.id}: {rule.name}\n\t"
            if rule.condition.field.path not in available_facts:
                msg += " Condition field not found "
                errors.append((msg, rule))
                continue
            fact: FactSpecProtocol = available_facts[rule.condition.field.path]
            flag = False
            if rule.condition.field.type != fact.type:
                flag = True
                msg += f" Condition type mismatch. Expected: {fact.type}. Actual: {rule.condition.field.type} "
            if fact.allowed_operators and rule.condition.operator.value not in fact.allowed_operators:
                flag = True
                msg += f" Condition operator mismatch. Expected: {fact.allowed_operators}. Actual: {rule.condition.operator} "
            if fact.allowed_values and rule.condition.value not in fact.allowed_values:
                flag = True
                msg += f" Condition operator mismatch. Expected: {fact.allowed_values}. Actual: {rule.condition.value} "
            if flag:
                errors.append((msg, rule))
                continue
            valids[rule.id] = rule
        if errors:
            for error in errors:
                logger.warning(error[0])
            raise RuleWithNoAvailableFactException("\n".join(error[1].name for error in errors))
        self.rules = valids

    def _load_rules_from_toml(self, rules_path: pathlib.Path) -> list[Rule]:
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
                rules.append(Rule.from_toml(rule_data))
            except InvalidRuleDataError as e:
                logger.warning(f"Skipping invalid rule_builder: {e}")
        return rules



    def match_rules(self, rules: dict[str, Rule], filters: Optional[list[str]])\
            -> dict[str, Rule]:
        """Return only the rules matching the given filters.

        Args:
            rules: rules to filter
            filters: filters to apply. Can be rule_builder.id or rule_builder.name
                If filter is None, return all rules.
        """
        if filters is None:
            return rules
        active_rules = dict[str, Rule]()
        for _filter in filters:
            try:
                active_rules[_filter] = rules[_filter]
            except KeyError:
                try:
                    rule = self.rules_name_lookup[_filter]
                    active_rules[rule.id] = rule
                except KeyError as err:
                    msg = f"Invalid rule_builder passed to filter: {"name" if isinstance(_filter, str) else "id"}: {_filter}"
                    raise InvalidRuleFilterException(msg) from err
        return active_rules

    # def _resolve_condition(self, rule: Rule) -> FactCheck:
    #     """Resolve a rule_builder model."""
    #     if rule.evaluator:
    #         return rule.evaluator
    #     elif rule.parse_condition():
    #         return rule.parse_condition()
    #     else:
    #         msg = f'Expected evaluator or parse model, got {type(rule)}'
    #         raise InvalidRuleExc(msg)
    # def _process_rule_violation(self, facts: FactSheet, rule: Rule, model: FactCheck) -> FailEvent:
    #     """Perform actions for a rule_builder violation detection."""
    #     result = FailEvent(
    #         pid=facts.get('pid'),
    #         proc_name=facts.get('name'),
    #         rule_id=rule.id,
    #         rule_name=rule.name,
    #         rule_message=rule.message,
    #         time_registered=datetime.datetime.now(),
    #         time_occured=facts.get('snapshot_time'),
    #         failed_condition=model
    #     )
    #     msg = (f'Process Failed Compliance [PID: {facts.get('pid')}, NAME: {facts.get('name')}]'
    #            f'\n\tRule violated: [ID: {rule.id}], NAME: {rule.name}]:'
    #            f'\n\t\tCondition: {str(model)}'
    #            f'\n\t\tResult: {str(result)}')
    #     logger.info(msg)
    #     return result
    #
    # def check_compliance(self, fact_sheets: list[FactSheet], active_rules: dict[int, Rule])\
    #         -> list[dict[int, list[FailEvent]]]:
    #     """Compare facts to rules."""
    #     final_result = []
    #     for facts in fact_sheets:
    #         result_set = []
    #         for rule in active_rules.values():
    #             # Rule is derived from info or from evaluator
    #             model = self._resolve_condition(rule)
    #
    #             result = model(facts.as_dict())
    #             if result: continue
    #             result_set.append(self._process_rule_violation(facts, rule, model))
    #
    #         final_result.append({facts.get('pid'): result_set})
    #     return final_result



if __name__ == "__main__":
    rules_engine = RulesEngine()