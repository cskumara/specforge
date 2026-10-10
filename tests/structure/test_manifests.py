import json
import re

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")

# Component dirs/files that must live at the plugin root, never in .claude-plugin/
ROOT_COMPONENTS = ["commands", "agents", "skills", "hooks", "scripts"]


# ---------- plugin.json ----------

def test_plugin_json_is_valid_json(root):
    path = root / ".claude-plugin" / "plugin.json"
    assert path.is_file(), "missing .claude-plugin/plugin.json"
    json.loads(path.read_text())


def test_plugin_name_is_specforge(plugin_json):
    assert plugin_json["name"] == "specforge"


def test_plugin_name_is_kebab_case_and_not_reserved(plugin_json):
    name = plugin_json["name"]
    assert KEBAB.match(name)
    assert not name.startswith(RESERVED_PREFIXES)


def test_plugin_has_recommended_metadata(plugin_json):
    for field in ("version", "description", "license"):
        assert isinstance(plugin_json.get(field), str) and plugin_json[field], field
    assert plugin_json["author"]["name"]


def test_plugin_keywords_is_list_of_strings(plugin_json):
    kw = plugin_json.get("keywords", [])
    assert isinstance(kw, list) and all(isinstance(k, str) for k in kw)


def test_component_paths_in_manifest_start_with_dot_slash(plugin_json):
    for key in ("commands", "agents", "skills", "hooks"):
        value = plugin_json.get(key)
        if value is None:
            continue
        paths = value if isinstance(value, list) else [value]
        for p in paths:
            if isinstance(p, str):
                assert p.startswith("./"), f"{key}: {p}"


def test_components_not_inside_claude_plugin_dir(root):
    inner = root / ".claude-plugin"
    for name in ROOT_COMPONENTS:
        assert not (inner / name).exists(), f"{name}/ must be at plugin root"
    extras = {p.name for p in inner.iterdir()} - {"plugin.json", "marketplace.json"}
    assert not extras, f"unexpected files in .claude-plugin/: {extras}"


# ---------- marketplace.json ----------

def test_marketplace_json_is_valid_json(root):
    path = root / ".claude-plugin" / "marketplace.json"
    assert path.is_file(), "missing .claude-plugin/marketplace.json"
    json.loads(path.read_text())


def test_marketplace_has_required_top_level_fields(marketplace_json):
    assert KEBAB.match(marketplace_json["name"])
    assert marketplace_json["owner"]["name"]
    assert isinstance(marketplace_json["plugins"], list) and marketplace_json["plugins"]


def test_marketplace_name_is_not_reserved(marketplace_json):
    assert not marketplace_json["name"].startswith(RESERVED_PREFIXES)


def test_marketplace_lists_specforge_with_matching_name(marketplace_json, plugin_json):
    entries = {p["name"]: p for p in marketplace_json["plugins"]}
    assert plugin_json["name"] in entries
    entry = entries[plugin_json["name"]]
    assert entry["description"]


def test_marketplace_source_is_relative_and_resolves_to_plugin_root(
    marketplace_json, plugin_json, root
):
    entry = next(p for p in marketplace_json["plugins"] if p["name"] == plugin_json["name"])
    source = entry["source"]
    assert isinstance(source, str) and source.startswith("./")
    assert ".." not in source
    resolved = (root / source).resolve()
    assert (resolved / ".claude-plugin" / "plugin.json").is_file()
