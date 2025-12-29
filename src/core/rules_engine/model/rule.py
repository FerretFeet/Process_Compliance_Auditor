""""""
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable

from core.rules_engine.model.condition import Expression
from shared.custom_exceptions.custom_exception import InvalidRuleDataError

class SourceEnum(Enum):
    PROCESS = "process"

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
    source: SourceEnum
    group: str = ""
    mutually_exclusive_group: str = ""
    enabled: bool = field(default=True)
    priority: int = field(default=0)
    metadata: dict = field(default_factory=dict)
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
          - model (string or nested dict for complex conditions)
          - action (string message or callable reference)
          - source (string or list of strings, optional)
          - group (optional)
          - mutually_exclusive_group (optional)
          - enabled (optional, defaults to True)
          - priority (optional, defaults to 0)
          - metadata (optional, dict)
        """
        from core.rules_engine.rule_builder.combinators import all_of, any_of
        from core.rules_engine.rule_builder.parsers import cond

        # Required fields
        name = toml_data.get("name")
        if not name:
            raise InvalidRuleDataError("TOML rule must have a 'name'")

        description = toml_data.get("description", "")

        # Grouping
        group = toml_data.get("group", "")
        mutually_exclusive_group = toml_data.get("mutually_exclusive_group", "")

        # Enabled and priority
        enabled = toml_data.get("enabled", True)
        priority = toml_data.get("priority", 0)

        # Metadata
        metadata = toml_data.get("metadata", {})

        # Source handling
        raw_source = toml_data.get("source")
        if raw_source is None:
            source = []  # default empty list if not specified
        elif isinstance(raw_source, str):
            source = SourceEnum(raw_source)
        # elif isinstance(raw_source, list):
        #     source = [SourceEnum(s) if isinstance(s, str) else s for s in raw_source]
        else:
            raise InvalidRuleDataError(f"Invalid source type: {type(raw_source)}")

        # Parse model/condition
        raw_condition = toml_data.get("model")
        if raw_condition is None:
            raise InvalidRuleDataError("TOML rule must have a 'model'")

        if isinstance(raw_condition, str):
            condition = cond(raw_condition)
        elif isinstance(raw_condition, dict):
            op = raw_condition.get("operator", "all").lower()
            children = raw_condition.get("conditions", [])
            child_conditions = []
            for c in children:
                if isinstance(c, str):
                    child_conditions.append(cond(c))
                elif isinstance(c, dict):
                    child_conditions.append(cls._parse_nested_condition(c))
                else:
                    raise InvalidRuleDataError(f"Invalid model type: {type(c)}")
            condition = all_of(*child_conditions) if op == "all" else any_of(*child_conditions)
        else:
            raise InvalidRuleDataError(f"Invalid model type: {type(raw_condition)}")

        # Parse action
        raw_action = toml_data.get("action")
        if isinstance(raw_action, str):
            def execute_action(facts: dict, msg=raw_action):
                print(msg)

            action = Action(name="Log", execute=execute_action)
        elif callable(raw_action):
            action = Action(name=getattr(raw_action, "__name__", "Inline"), execute=raw_action)
        else:
            raise InvalidRuleDataError(f"Invalid action type: {type(raw_action)}")

        # Construct Rule instance
        return cls(
            name=name,
            description=description,
            condition=condition,
            action=action,
            source=source,
            group=group,
            mutually_exclusive_group=mutually_exclusive_group,
            enabled=enabled,
            priority=priority,
            metadata=metadata,
        )

    @staticmethod
    def _parse_nested_condition(data: dict) -> "Expression":
        """
        Recursively parse nested model dictionaries from TOML/JSON into
        Condition, NotCondition, or ConditionSet objects.
        """
        from core.rules_engine.rule_builder.combinators import all_of, any_of
        from core.rules_engine.rule_builder.parsers import cond

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
                raise InvalidRuleDataError(f"Invalid model type: {type(c)}")

        if len(child_conditions) == 0:
            raise InvalidRuleDataError("No conditions provided in nested model")
        elif len(child_conditions) == 1:
            return child_conditions[0]

        if op == "all":
            return all_of(*child_conditions)
        elif op == "any":
            return any_of(*child_conditions)
        else:
            raise InvalidRuleDataError(f"Unknown operator '{op}' in nested model")
