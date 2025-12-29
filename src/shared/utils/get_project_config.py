import platform
import tomllib
from pathlib import Path
from typing import Any

from shared.custom_exceptions import InvalidProjectConfigurationError


class ConfigManager:
    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._loaded = False
        self.get_config()

    def get(self, key: str) -> Any:
        try:
            return self._config[key]
        except KeyError as err:
            msg = f"{key} not found in config"
            raise InvalidProjectConfigurationError(msg) from err

    def get_config(self, fp: Path | None = None) -> dict:
        if not self._loaded:
            if fp is None:
                fp = Path("config/project_config.toml")

            with open(fp, "rb") as f:
                raw_data = tomllib.load(f).get("project_config", {})

            self._config = {k: (None if v == "None" else v) for k, v in raw_data.items()}
            self._config.setdefault("os", platform.system())
            self._loaded = True

        return self._config

    def override(self, key: str, value: Any) -> None:
        """Method specifically for testing."""
        self._config[key] = value

    def clear(self) -> None:
        """Resets the state for fresh tests."""
        self._config = {}
        self._loaded = False

    def get_file_path(self, key: str) -> Path:
        path = self.get(key)
        if path is None:
            msg = f"{key} not found in config"
            raise InvalidProjectConfigurationError(msg)
        if path[0] == "/":
            msg = f"Invalid path: {path}. Should not start with '/'"
            raise InvalidProjectConfigurationError(msg)
        return Path(path)


cfg = ConfigManager()
