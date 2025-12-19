"""Custom Exceptions"""

class InvalidRuleException(Exception):
    def __init__(self, err: Exception, rule_id: int, msg: str = "Invalid rule"):
        self.rule = rule_id
        self.original_error = err
        full_msg = f"{msg}: {rule_id}"
        if err:
            full_msg += f" ({err})"
        super().__init__(full_msg)

class InvalidRuleExc(Exception):
    def __init__(self, msg:str):
        super().__init__(msg)

class InvalidProjectConfigurationError(Exception):
    def __init__(self, err: Exception | None = None):
        self.original_error = err if err else ''
        msg = f"Invalid project configuration, expect 'project_config' in root/config/project_config.toml: {err}"
        super().__init__(msg)

class InvalidCLI_ParserConfigurationError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class InvalidRuleDataError(Exception):
    """Raised when a TOML rule entry is invalid."""
    pass

