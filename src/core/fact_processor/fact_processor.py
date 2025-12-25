from typing import Mapping

from core.fact_processor.fact_sheet import FactSheet
from core.fact_processor.fact_registry import FactRegistry
from shared._common.facts import FactSpec


class FactProcessor:
    def __init__(self):
        self._all_facts = None

    def get_possible_facts(self) -> dict[str, FactSpec]:
        if self._all_facts is None:
            self._all_facts = FactRegistry.all_facts()
        return self._all_facts

    def parse_facts(self, snapshots: dict[str, list[object | dict]]) -> list[FactSheet]:
        factsheets = []
        for key, value in snapshots.items():
            for fact in self

