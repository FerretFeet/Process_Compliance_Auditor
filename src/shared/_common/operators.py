import operator
from enum import Enum
from typing import runtime_checkable, Protocol


class Operator(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    IN = "in"
    NOT_IN = "not in"
    IS = "is"
    IS_NOT = "is not"

    CONTAINS = "contains"
    STARTS_WITH = "starts with"
    ENDS_WITH = "ends with"

    EXISTS = "exists"
    NOT_EXISTS = "not exists"

OPERATOR_FN = {
    Operator.EQ: operator.eq,
    Operator.NE: operator.ne,
    Operator.LT: operator.lt,
    Operator.LTE: operator.le,
    Operator.GT: operator.gt,
    Operator.GTE: operator.ge,
    Operator.IN: lambda a, b: a in b,
    Operator.NOT_IN: lambda a, b: a not in b,
    Operator.IS: operator.is_,
    Operator.IS_NOT: operator.is_not,

    Operator.CONTAINS: lambda a, b: b in a,
    Operator.STARTS_WITH: lambda a, b: a.startswith(b),
    Operator.ENDS_WITH: lambda a, b: a.endswith(b),

    Operator.EXISTS: lambda value: value is not None,
    Operator.NOT_EXISTS: lambda value: value is None,
}



class GroupOperator(Enum):
    ALL = "all"
    ANY = "any"
