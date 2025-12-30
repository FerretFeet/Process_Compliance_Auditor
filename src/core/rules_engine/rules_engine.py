"""Rules engine."""

import tomllib
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

from core.rules_engine.builtin_rules import ALL_BUILTIN_RULES
from core.rules_engine.model import Rule
from core.rules_engine.model.condition import Condition, ConditionSet, Expression, NotCondition
from shared._common.facts import FactSpecProtocol
from shared.custom_exceptions import (
    InvalidRuleDataError,
    InvalidRuleFilterError,
    RuleWithNoAvailableFactError,
)
from shared.services import logger
from shared.utils import cfg, project_root

if TYPE_CHECKING:
    import pathlib

FactCheck = Callable[[dict], bool]


FactProvider = Callable[[], Mapping[str, FactSpecProtocol]]

_rules_file_path = project_root / cfg.get("rules_path")

_builtin_rules = ALL_BUILTIN_RULES


class RulesEngine:
    """Control Access and Understanding of Rules."""

    def __init__(
        self,
        fact_provider: FactProvider,
        *,
        toml_rules_path: pathlib.Path = _rules_file_path,
        builtin_rules: list[Rule] = _builtin_rules,
    ) -> None:
        """Initialize a RulesEngine object."""
        self.fact_provider = fact_provider
        self.builtin_rules = builtin_rules or []
        self.toml_rules_path = toml_rules_path
        self.rules = None
        self.rules = self.get_rules()
        self.rules_name_lookup = {rule.name: rule for rule in self.rules.values()}

        self.validate_rules()

    def get_rules(self) -> dict[str, Rule]:
        """
        Return all rules defined in project.toml.

        Loads rules if not already loaded.
        """
        if self.rules is None:
            rules = self._load_rules_from_toml(self.toml_rules_path) or []
            self.rules = {rule.id: rule for rule in rules + self.builtin_rules}
        return self.rules

    def validate_rules(self) -> None:
        """
        Check that rules correspond to available facts.

        Raises:
            RuleWithNoAvailableFactError: if no fact is found for a rule's condition.

        """
        if self.fact_provider is None:
            logger.warning(
                f"No fact_provider defined for {type(self).__name__}. Validation skipped.",
            )
            return

        available_facts = self.fact_provider()
        errors: list = []
        valids = {}

        for rule in self.rules.values():
            self._validate_expression(
                rule.condition,
                available_facts,
                rule,
                errors,
            )

            if rule.id not in {r.id for _, r in errors}:
                valids[rule.id] = rule
            else:
                errors.append(rule.name)

        if errors:
            for msg, _ in errors:
                logger.warning(msg)

            raise RuleWithNoAvailableFactError("\n".join(rule.name for _, rule in errors))

        self.rules = valids

    def _validate_expression(
        self,
        expr: Expression,
        available_facts: dict[str, FactSpecProtocol],
        rule: Rule,
        errors: list,
    ) -> None:
        """Recursively validate a rule Expression, appends to `errors` on failure."""
        # ── Leaf ──────────────────────────────────────────────
        if isinstance(expr, Condition):
            path = expr.field.path
            msg = f"Invalid rule: {rule.id}: {rule.name}\n\t"

            if path not in available_facts:
                errors.append((msg + "Condition field not found", rule))
                return

            fact = available_facts[path]
            failed = False

            if expr.field.type != fact.type:
                failed = True
                msg += f"Condition type mismatch. Expected {fact.type}, got {expr.field.type}. "

            if fact.allowed_operators and expr.operator not in fact.allowed_operators:
                failed = True
                msg += (
                    f"Condition operator mismatch. Expected {fact.allowed_operators}, "
                    f"got {expr.operator}. "
                )

            if fact.allowed_values and expr.value not in fact.allowed_values:
                failed = True
                msg += (
                    f"Condition value mismatch. Expected {fact.allowed_values}, got {expr.value}. "
                )

            if failed:
                errors.append((msg, rule))
            return

        # ── NOT ───────────────────────────────────────────────
        if isinstance(expr, NotCondition):
            self._validate_expression(expr.condition, available_facts, rule, errors)
            return

        # ── AND / OR ──────────────────────────────────────────
        if isinstance(expr, ConditionSet):
            for child in expr.conditions:
                self._validate_expression(child, available_facts, rule, errors)
            return

        # ── Unknown node ──────────────────────────────────────
        errors.append((f"Invalid rule: {rule.id}: Unknown expression type {type(expr)}", rule))

    def _load_rules_from_toml(self, rules_path: pathlib.Path) -> list[Rule] | None:
        """
        Load rules from project.toml.

        Returns all rules defined in project.toml.
        """
        if not rules_path.exists():
            rules_path.parent.mkdir(parents=True, exist_ok=True)
            rules_path.touch()
        with rules_path.open("rb") as f:
            uf_rules = tomllib.load(f).get("rules", [])
        if not isinstance(uf_rules, list):
            msg = "Expected 'rules' to be a list of tables in TOML"
            raise InvalidRuleDataError(msg)
        rules = []
        for rule_data in uf_rules:
            try:
                rules.append(Rule.from_toml(rule_data))
            except InvalidRuleDataError as e:
                logger.warning(f"Skipping invalid rule_builder: {e}")
        return rules

    def match_rules(self, rules: dict[str, Rule], filters: list[str] | None) -> dict[str, Rule]:
        """
        Return only the rules matching the given filters.

        Args:
            rules: rules to filter
            filters: filters to apply. Can be rule_builder.id or rule_builder.name
                If filter is None, return all rules.

        Returns:
            dict rule.path : Rule

        Raises:
            InvalidRuleFilterError: if filter is invalid.

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
                    msg = (
                        f"Invalid rule_builder passed to filter: "
                        f"{"name" if isinstance(_filter, str) else "id"}: {_filter}"
                    )
                    raise InvalidRuleFilterError(msg) from err
        return active_rules
