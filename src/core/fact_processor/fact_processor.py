from typing import Mapping

from core.fact_processor.fact_sheet import FactSheet
from core.fact_processor.fact_registry import FactRegistry
from shared._common.facts import FactSpec


class FactProcessor:
    def __init__(self):
        pass

    def get_possible_facts(self) -> Mapping[str, FactSpec]:
        return FactRegistry.all_facts()

    def parse_facts(self, snapshots: list) -> list[FactSheet]:
        pass

