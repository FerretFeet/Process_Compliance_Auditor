from typing import Mapping, Any

from core.fact_processor.fact_sheet import FactSheet
from core.fact_processor.fact_registry import FactRegistry
from shared._common.facts import FactSpec, FactData
from shared.custom_exceptions import FactNotFoundException
from shared.services import logger
from shared.utils import cfg
from shared.utils.resolve_path import resolve_path


strict = cfg.get('strict')

class FactProcessor:
    def __init__(self):
        self._all_facts: dict[str, FactSpec] | None = None

    def get_possible_facts(self) -> dict[str, FactSpec]:
        if self._all_facts is None:
            self._all_facts = FactRegistry.all_facts()
        return self._all_facts

    def parse_facts(self, snapshots: dict[str, list[object | dict]]) -> dict[str, dict[str, Any]]:
        """
        Get all fact data from snapshots.

        Raises FactNotFoundException if strict and no data can be found for a particular fact.
        """
        factsheets = {}
        for fact in self._all_facts.values():
            for s in fact.source:
                if s not in factsheets:
                    factsheets[s] = {}
                try:
                    f = resolve_path(snapshots[s.value], fact.path)

                    factsheets[s.value][fact.path] = f

                except ValueError as err:
                    msg = f'{fact.path} is not a valid path for {type(s).__name__}'
                    logger.warning(msg)
                    if strict:
                        raise FactNotFoundException(msg) from err

        return factsheets

