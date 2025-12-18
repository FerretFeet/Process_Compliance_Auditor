"""A Compliance Rule Object.

Contains:
    id,
    name: identifying string
    message: Message to print on failure
    info: Optional additional information

"""
from dataclasses import dataclass


@dataclass
class Rule:
    id: int
    name: str
    message: str
    info: str

    def to_toml(self):
        pass
    def from_toml(self):
        pass