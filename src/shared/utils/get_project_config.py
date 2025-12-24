import platform

import shared
import tomllib
from pathlib import Path

from shared import utils
from shared.custom_exceptions.custom_exception import InvalidProjectConfigurationError


def get_project_config(fp: Path = utils.project_root / 'config' / 'project_config.toml'):
    """Get the global config object."""
    with Path.open(fp, 'rb') as f:
        config = tomllib.load(f).get('project_config', {})
    if not config:
        raise InvalidProjectConfigurationError()
    for key, val in config.items():
        if val == "None":
            config[key] = None

    config.setdefault('os', platform.system())
    return config
