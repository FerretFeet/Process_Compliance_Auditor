"""Custom Exceptions"""
from src import rules_engine


class InvalidRuleException(Exception):
    def __init__(self, err: Exception, rule_id: int, msg: str = "Invalid rule"):
        self.rule = rule_id
        self.original_error = err
        full_msg = f"{msg}: {rule_id}"
        if err:
            full_msg += f" ({err})"
        super().__init__(full_msg)