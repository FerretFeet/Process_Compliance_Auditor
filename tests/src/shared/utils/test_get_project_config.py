import platform

import pytest
import shared

from shared.custom_exceptions import InvalidProjectConfigurationError
from shared.utils import get_project_config


class TestGetProjectConfig:
    def test_loads_valid_config(self, tmp_path):
        # Create a temporary TOML file with valid content
        config_data = {
            "project_config": {
                "name": "MyProject",
                "version": "1.0"
            }
        }
        toml_path = tmp_path / "project_config.toml"
        toml_path.write_text(
            """
            [project_config]
            name = "MyProject"
            version = "1.0"
            """
        )

        config = get_project_config(fp=toml_path)
        assert config["name"] == "MyProject"
        assert config["version"] == "1.0"
        assert config["os"] == platform.system()  # default added

    def test_converts_none_string_to_none(self, tmp_path):
        toml_path = tmp_path / "project_config.toml"
        toml_path.write_text(
            """
            [project_config]
            description = "None"
            """
        )
        config = get_project_config(fp=toml_path)
        assert config["description"] is None
        assert config["os"] == platform.system()

    def test_raises_error_for_empty_config(self, tmp_path):
        # Empty TOML
        toml_path = tmp_path / "project_config.toml"
        toml_path.write_text(
            """
            [project_config]
            """
        )
        with pytest.raises(InvalidProjectConfigurationError):
            get_project_config(fp=toml_path)

    def test_raises_error_for_missing_file(self, tmp_path):
        missing_file = tmp_path / "nonexistent.toml"
        with pytest.raises(FileNotFoundError):
            get_project_config(fp=missing_file)
