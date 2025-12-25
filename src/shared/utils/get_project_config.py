import platform
import tomllib
from pathlib import Path
from typing import Any


class ConfigManager:
    def __init__(self):
        self._config: dict[str, Any] = {}
        self._loaded = False
        self.get_config()

    def get(self, key: str) -> Any:
        return self._config[key]

    def get_config(self, fp: Path = None) -> dict:
        if not self._loaded:
            if fp is None:
                fp = Path("config/project_config.toml")

            with open(fp, 'rb') as f:
                raw_data = tomllib.load(f).get('project_config', {})

            self._config = {k: (None if v == "None" else v) for k, v in raw_data.items()}
            self._config.setdefault('os', platform.system())
            self._loaded = True

        return self._config

    def override(self, key: str, value: Any):
        """Method specifically for testing."""
        self._config[key] = value

    def clear(self):
        """Resets the state for fresh tests."""
        self._config = {}
        self._loaded = False

cfg = ConfigManager()