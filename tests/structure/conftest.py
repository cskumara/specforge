import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def plugin_json(root) -> dict:
    return json.loads((root / ".claude-plugin" / "plugin.json").read_text())


@pytest.fixture(scope="session")
def marketplace_json(root) -> dict:
    return json.loads((root / ".claude-plugin" / "marketplace.json").read_text())
