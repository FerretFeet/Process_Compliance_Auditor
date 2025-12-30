import pytest

from shared.utils import cfg


@pytest.fixture
def mock_config_file(tmp_path):
    """Creates a temporary TOML file for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "project_config.toml"

    # Write dummy data
    content = """
    [project_config]
    app_name = "TestApp"
    version = 1.0
    debug = "None"
    """
    config_file.write_text(content)
    return config_file


@pytest.fixture(autouse=True)
def clean_cfg():
    """Automatically clears the global config before and after each test."""
    cfg.clear()
    yield
    cfg.clear()


def test_load_config(mock_config_file):
    """Test that file loading and 'None' string conversion works."""
    config = cfg.load_config(fp=mock_config_file)

    assert config["app_name"] == "TestApp"
    assert config["debug"] is None  # Check that "None" became None
    assert "os" in config  # Check that default OS was added


def test_clear_functionality(mock_config_file):
    """Tests that clear() actually wipes the internal state."""
    cfg.load_config(fp=mock_config_file)
    cfg.clear()

    assert cfg._loaded is False
    assert cfg._config == {}
