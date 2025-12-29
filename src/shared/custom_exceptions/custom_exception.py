"""Custom Exceptions"""


class InvalidCLI_ParserConfigurationError(Exception):
    """Raised when CLI parser is used incorrectly."""

    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidRuleFilterException(Exception):
    """Raised when a filter does not match any given rule_builder."""

    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidRuleException(Exception):
    def __init__(self, err: Exception, rule_id: int, msg: str = "Invalid rule_builder"):
        self.rule = rule_id
        self.original_error = err
        full_msg = f"{msg}: {rule_id}"
        if err:
            full_msg += f" ({err})"
        super().__init__(full_msg)


class InvalidRuleExc(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidProjectConfigurationError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class ProcessNotCreatedException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidRuleDataError(Exception):
    """Raised when a TOML rule_builder entry is invalid."""

    pass


class RuleWithNoAvailableFactException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class FactNotFoundException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
