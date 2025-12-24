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


class GroupOperator(Enum):
    ALL = "all"
    ANY = "any"
