"""Global config."""

import platform
import tomllib
from pathlib import Path
from typing import Any

from shared.custom_exceptions import InvalidProjectConfigurationError


class ConfigManager:
    """Global read-only project config."""

    def __init__(self) -> None:
        """
        Initialize a ConfigManager object.

        Read-Only Project Level Configuration.
        """
        self._config: dict[str, Any] = {}
        self._loaded = False
        self.load_config()

    def get(self, key: str) -> Any:  # noqa: ANN401
        """
        Get a value from the config.

        Args:
            key (str): The key to look for in the config.

        Raises:
            InvalidProjectConfigurationError: if no item is found in config.

        """
        try:
            return self._config[key]
        except KeyError as err:
            msg = f"{key} not found in config"
            raise InvalidProjectConfigurationError(msg) from err

    def load_config(self, fp: Path | None = None) -> dict:
        """
        Load the config from a file.

        Args:
            fp (Path | None): Path or file to load config from. If None, load the default config

        """
        if not self._loaded:
            if fp is None:
                fp = Path("config/project_config.toml")

            with fp.open("rb") as f:
                raw_data = tomllib.load(f).get("project_config", {})

            self._config = {k: (None if v == "None" else v) for k, v in raw_data.items()}
            self._config.setdefault("os", platform.system())
            self._loaded = True

        return self._config

    def clear(self) -> None:
        """Reset the state for fresh tests."""
        self._config = {}
        self._loaded = False

    def get_file_path(self, key: str) -> Path:
        """
        Get a relative path to a file.

        Makes sure the path exists.

        Args:
            key (str): The key to look for in the config.

        Raises:
            InvalidProjectConfigurationError: if the path is interpreted as absolute path.

        """
        path = self.get(key)
        if path is None:
            msg = f"{key} not found in config"
            raise InvalidProjectConfigurationError(msg)
        if path[0] == "/":
            msg = f"Invalid path: {path}. Should not start with '/'"
            raise InvalidProjectConfigurationError(msg)
        return Path(path)


cfg = ConfigManager()
