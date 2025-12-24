from typing import Mapping

from src.fact_processor.fact_sheet import FactSheet
from src.fact_processor.fact_registry import FactRegistry
from _common.facts import FactSpec


class FactProcessor:
    def __init__(self):
        pass

    def get_possible_facts(self) -> Mapping[str, FactSpec]:
        return FactRegistry.all_facts()

    def parse_facts(self, snapshots: list) -> list[FactSheet]:
        pass

