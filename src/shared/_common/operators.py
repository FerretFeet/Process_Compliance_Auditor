import operator
from enum import Enum


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


NUMERIC_OPS = {
    Operator.EQ,
    Operator.NE,
    Operator.LT,
    Operator.LTE,
    Operator.GT,
    Operator.GTE,
    Operator.EXISTS,
    Operator.NOT_EXISTS,
}

STRING_OPS = {
    Operator.EQ,
    Operator.NE,
    Operator.CONTAINS,
    Operator.STARTS_WITH,
    Operator.ENDS_WITH,
    Operator.IN,
    Operator.NOT_IN,
    Operator.EXISTS,
    Operator.NOT_EXISTS,
}

BOOL_OPS = {
    Operator.IS,
    Operator.IS_NOT,
    Operator.EXISTS,
    Operator.NOT_EXISTS,
}

COLLECTION_OPS = {
    Operator.CONTAINS,
    Operator.IN,
    Operator.NOT_IN,
    Operator.EXISTS,
    Operator.NOT_EXISTS,
}

STRUCT_OPS = {
    Operator.CONTAINS,
    Operator.EXISTS,
    Operator.NOT_EXISTS,
}


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
