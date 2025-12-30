from typing import TYPE_CHECKING, Any

from core.fact_processor.fact_registry import FactRegistry
from core.rules_engine.model.rule import SourceEnum
from shared.custom_exceptions import FactNotFoundError
from shared.services import logger
from shared.utils.resolve_path import resolve_path

if TYPE_CHECKING:
    from shared._common.facts import FactSpec


class FactProcessor:
    def __init__(self, fact_registry: FactRegistry | None = None) -> None:
        self._all_facts: dict[str, FactSpec] | None = (
            fact_registry.all_facts() if fact_registry else None
        )

    def get_all_facts(self) -> dict[str, FactSpec]:
        """
        Get all available facts.

        Returns:
            dict[str, FactSpec]: A dict of key (FactSpec.path) value FactSpec

        """
        if self._all_facts is None:
            self._all_facts = FactRegistry.all_facts()
        return self._all_facts

    def get_facts_by_sources(self, sources: list[str]) -> dict[str, dict[str, FactSpec]]:
        """Get all available facts from all passed sources."""
        returndict = {}
        for source in sources:
            val = self.get_facts_by_source(source)
            if val:
                returndict[source] = val
        return returndict

    def get_facts_by_source(self, source: str) -> dict[str, FactSpec]:
        """Get a set of available facts for a particular source."""
        returndict: dict[str, FactSpec] = {}
        for fact in self._all_facts.values():
            try:
                if fact.source == SourceEnum(source):
                    returndict[fact.path] = fact
            except ValueError as err:
                msg = f"Error getting fact for {source}: {err}"
                logger.warning(msg)
        return returndict

    def parse_facts(self, snapshots: dict[str, list[object | dict]]) -> dict[str, dict[str, Any]]:
        """
        Get all fact data from snapshots.

        Args:
            snapshots (dict[str, list[object | dict]]): A dict of key (snapshot_source) value list(snapshot)

        Returns:
            dict[str, dict[str, Any]]: A dict of key (source) value FactSheet

        Exception:
            FactNotFoundException: if no data can be found for a particular fact.

        """
        factsheets = {}
        for src, snapshots in snapshots.items():
            # TODO: Limited to one snapshot per source
            # Unsure if worth it to implement multi snapshot per source for multiple processes.
            # Disregard for now
            # 12/26/2025

            factsheets[src] = {}
            facts = self.get_facts_by_source(src)
            for snapshot in snapshots:
                for fact in facts.values():
                    try:
                        factsheets[src][fact.path] = resolve_path(snapshot, fact.path)

                    except ValueError as err:
                        msg = f"{fact.path} is not a valid path for {type(snapshot).__name__}"
                        raise FactNotFoundError(msg) from err

        return factsheets
