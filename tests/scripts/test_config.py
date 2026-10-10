import json

import pytest

import config


def write(proj, text):
    (proj / ".spec").mkdir(exist_ok=True)
    (proj / ".spec" / "config.json").write_text(text)


def test_defaults_when_no_config_file(tmp_path):
    assert config.load(tmp_path) == {
        "code_dirs": ["src", "app", "lib"],
        "test_dirs": ["tests"],
        "test_command": None,
    }


def test_defaults_are_not_shared_between_calls(tmp_path):
    config.load(tmp_path)["code_dirs"].append("x")
    assert config.load(tmp_path)["code_dirs"] == ["src", "app", "lib"]


def test_overrides_are_merged_over_defaults(tmp_path):
    write(tmp_path, json.dumps({"code_dirs": ["backend"], "test_command": "make test"}))
    cfg = config.load(tmp_path)
    assert cfg["code_dirs"] == ["backend"]
    assert cfg["test_command"] == "make test"
    assert cfg["test_dirs"] == ["tests"]


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "{bad",
        "[]",
        '{"code_dirs": "src"}',
        '{"code_dirs": [1]}',
        '{"code_dirs": ["a/b"]}',  # directory names only, not paths
        '{"test_dirs": []}',
        '{"test_command": 5}',
        '{"test_command": ""}',
        '{"unknown": 1}',
    ],
)
def test_invalid_config_raises(tmp_path, raw):
    write(tmp_path, raw)
    with pytest.raises(config.ConfigError):
        config.load(tmp_path)
