from enum import Enum


class Operator(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    IN = "in"


class GroupOperator(Enum):
    ALL = "all"
    ANY = "any"
