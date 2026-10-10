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


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal YAML-frontmatter parser: flat `key: value` pairs only."""
    if not text.startswith("---\n"):
        return {}, text
    head, sep, body = text[4:].partition("\n---\n")
    if not sep:
        return {}, text
    meta = {}
    for line in head.splitlines():
        key, colon, value = line.partition(":")
        if colon:
            meta[key.strip()] = value.strip()
    return meta, body


def headings(text: str) -> list[str]:
    """Lower-cased markdown heading titles (any level)."""
    return [
        line.lstrip("#").strip().lower()
        for line in text.splitlines()
        if line.startswith("#")
    ]


def section(text: str, title: str) -> str:
    """Body of the first heading whose title equals `title` (case-insensitive)."""
    lines = text.splitlines()
    out, capturing, level = [], False, 0
    for line in lines:
        if line.startswith("#"):
            this_level = len(line) - len(line.lstrip("#"))
            if capturing and this_level <= level:
                break
            if not capturing and line.lstrip("#").strip().lower() == title.lower():
                capturing, level = True, this_level
                continue
        elif capturing:
            out.append(line)
    return "\n".join(out).strip()
