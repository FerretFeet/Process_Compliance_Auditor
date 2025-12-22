""""""
import hashlib
import operator
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Union, Iterable, Sequence

from src.custom_exceptions.custom_exception import InvalidRuleDataError
from src.rules_engine.rule_builder.condition import Expression, any_of, all_of

ActionType = Callable[[dict], None]

@dataclass(frozen=True, slots=True)
class Action:
    name: str
    execute:ActionType
    description: Optional[str] = None


    def __call__(self, facts: dict) -> None:
        self.execute(facts)

@dataclass(frozen=True, slots=True)
class Rule:
    name: str
    description: str
    condition: Expression
    action: Action
    group: str = ""
    mutually_exclusive_group: str = ""
    id: str = field(init=False)


    def __post_init__(self):
        object.__setattr__(self, "id", self._generate_id())

    def _generate_id(self) -> str:
        """
        Generate a deterministic human-readable ID:
        - 3-character prefix derived from the group (or default "RUL")
        - 6-digit numeric portion from SHA256 hash of name + description
        """
        prefix = self.group[:3].upper() if self.group else "RUL"  # default "RUL" = Rule
        combined = f"{self.name}:{self.description}"
        h = hashlib.sha256(combined.encode()).hexdigest()
        numeric_id = str(int(h[:8], 16))[-6:].zfill(6)
        return f"{prefix}-{numeric_id}"

    @classmethod
    def from_toml(cls, toml_data: dict) -> "Rule":
        """
        Create a Rule object from a TOML dictionary.
        Expects keys:
          - name
          - description
          - condition (string or nested dict for complex conditions)
          - action (string message or callable reference)
          - group (optional)
          - mutually_exclusive_group (optional)
        """
        from src.rules_engine.rule_builder.condition import cond

        name = toml_data.get("name")
        description = toml_data.get("description", "")
        group = toml_data.get("group", "")
        mutually_exclusive_group = toml_data.get("mutually_exclusive_group", "")

        if not name:
            raise InvalidRuleDataError("TOML rule must have a 'name'")

        # Parse condition
        raw_condition = toml_data.get("condition")
        if raw_condition is None:
            raise InvalidRuleDataError("TOML rule must have a 'condition'")

        # If condition is a string, parse it
        if isinstance(raw_condition, str):
            condition = cond(raw_condition)
        elif isinstance(raw_condition, dict):
            # Nested conditions: simple AND/OR parsing
            op = raw_condition.get("operator", "all").lower()
            children = raw_condition.get("conditions", [])
            child_conditions = []
            for c in children:
                if isinstance(c, str):
                    child_conditions.append(cond(c))
                elif isinstance(c, dict):
                    child_conditions.append(cls._parse_nested_condition(c))
                else:
                    raise InvalidRuleDataError(f"Invalid condition type: {type(c)}")
            condition = all_of(*child_conditions) if op == "all" else any_of(*child_conditions)
        else:
            raise InvalidRuleDataError(f"Invalid condition type: {type(raw_condition)}")

        # Parse action
        raw_action = toml_data.get("action")
        if isinstance(raw_action, str):
            # Default: action that logs the message
            def execute_action(facts: dict, msg=raw_action):
                print(msg)
            action = Action(name="Log", execute=execute_action)
        elif callable(raw_action):
            action = Action(name=getattr(raw_action, "__name__", "Inline"), execute=raw_action)
        else:
            raise InvalidRuleDataError(f"Invalid action type: {type(raw_action)}")

        return cls(
            name=name,
            description=description,
            condition=condition,
            action=action,
            group=group,
            mutually_exclusive_group=mutually_exclusive_group,
        )

    @staticmethod
    def _parse_nested_condition(data: dict) -> "Expression":
        """
        Recursively parse nested condition dictionaries from TOML/JSON into
        Condition, NotCondition, or ConditionSet objects.
        """
        # Local imports to avoid circular imports
        from .condition import cond, all_of, any_of, Expression

        op = data.get("operator", "all").lower()
        children = data.get("conditions", [])
        child_conditions = []

        for c in children:
            if isinstance(c, str):
                child_conditions.append(cond(c))
            elif isinstance(c, dict):
                nested = Rule._parse_nested_condition(c)
                child_conditions.append(nested)
            else:
                raise InvalidRuleDataError(f"Invalid condition type: {type(c)}")

        # Handle single child: return it directly
        if len(child_conditions) == 0:
            raise InvalidRuleDataError("No conditions provided in nested condition")
        elif len(child_conditions) == 1:
            return child_conditions[0]

        # Multiple children: wrap in ConditionSet
        if op == "all":
            return all_of(*child_conditions)
        elif op == "any":
            return any_of(*child_conditions)
        else:
            raise InvalidRuleDataError(f"Unknown operator '{op}' in nested condition")
