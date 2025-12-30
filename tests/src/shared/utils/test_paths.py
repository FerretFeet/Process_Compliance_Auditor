import pytest

from shared.utils.paths import find_project_root


def test_find_root_current_dir(tmp_path):
    """It should find the root if the marker is in the current directory."""
    marker = tmp_path / "pyproject.toml"
    marker.touch()

    assert find_project_root(tmp_path) == tmp_path


def test_find_root_in_parent(tmp_path):
    """It should find the root if the marker is several levels up."""
    # Create structure: /tmp/project/src/subdir/file.py
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "src").mkdir()  # This is our marker

    deep_dir = project_root / "subdir" / "subsubdir"
    deep_dir.mkdir(parents=True)

    assert find_project_root(deep_dir) == project_root


@pytest.mark.parametrize("marker", [".venv", "src", "pyproject.toml"])
def test_find_root_all_markers(tmp_path, marker):
    """It should identify the root using any of the defined markers."""
    (tmp_path / marker).mkdir() if marker != "pyproject.toml" else (tmp_path / marker).touch()

    assert find_project_root(tmp_path) == tmp_path


def test_find_root_raises_error(tmp_path):
    """It should raise RuntimeError if no markers are found in the hierarchy."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(RuntimeError, match="Project root not found"):
        find_project_root(empty_dir)
