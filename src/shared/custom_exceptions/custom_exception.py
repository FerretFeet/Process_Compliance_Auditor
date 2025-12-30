"""Custom Exceptions."""


class InvalidCliParserConfigurationError(Exception):
    """Raised when CLI parser is used incorrectly."""


class InvalidRuleFilterError(Exception):
    """Raised when a filter does not match any given rule_builder."""


class InvalidRuleError(Exception):
    """Raised when a rule builder entry is invalid."""


class InvalidProjectConfigurationError(Exception):
    """Raised when a project configuration is used incorrectly or is missing."""


class ProcessNotCreatedError(Exception):
    """Raised when a process is not created or was not created."""


class InvalidRuleDataError(Exception):
    """Raised when a TOML rule_builder entry is invalid."""


class RuleWithNoAvailableFactError(Exception):
    """Raised when a rule's condition does not meet any available fact."""


class FactNotFoundError(Exception):
    """Raised when a Fact is not found or was not found."""
