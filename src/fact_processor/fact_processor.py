from typing import Mapping

from src.fact_processor.fact_registry import FactRegistry, FactSpec


class FactProcessor:
    def __init__(self):
        pass

    def get_possible_facts(self) -> dict[str, FactSpec]:
        return FactRegistry.all_facts()