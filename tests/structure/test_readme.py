import pytest

from conftest import headings, section

COMMANDS = ["spec", "plan", "build", "review", "status", "approve"]


@pytest.fixture(scope="module")
def readme(root):
    path = root / "README.md"
    assert path.is_file(), "missing README.md"
    return path.read_text()


@pytest.mark.parametrize(
    "title",
    ["install", "workflow", "commands", "gates", "configuration", "example session",
     "limitations", "development"],
)
def test_readme_has_section(readme, title):
    assert title in headings(readme)


def test_install_uses_the_real_marketplace_and_plugin_names(readme, plugin_json, marketplace_json):
    install = section(readme, "install")
    assert "/plugin marketplace add" in install
    assert f"/plugin install {plugin_json['name']}@{marketplace_json['name']}" in install


@pytest.mark.parametrize("name", COMMANDS)
def test_every_command_is_documented(readme, name):
    assert f"/specforge:{name}" in section(readme, "commands")


def test_workflow_has_a_text_diagram_of_all_phases(readme):
    wf = section(readme, "workflow")
    assert "```" in wf
    low = wf.lower()
    for phase in ("spec", "plan", "build", "review"):
        assert phase in low
    assert "approve" in low


def test_example_session_walks_through_every_command(readme):
    example = section(readme, "example session")
    for name in COMMANDS:
        assert f"/specforge:{name}" in example


def test_gates_section_names_each_hook_behavior(readme):
    low = section(readme, "gates").lower()
    for needle in ("spec_approved", "plan_approved", "test:", "spec_version", "state.json"):
        assert needle in low, needle


def test_configuration_documents_config_json_keys(readme):
    cfg = section(readme, "configuration")
    for key in ("code_dirs", "test_dirs", "test_command", ".spec/config.json"):
        assert key in cfg


def test_limitations_are_honest_about_what_hooks_cannot_enforce(readme):
    low = section(readme, "limitations").lower()
    assert "red" in low and "green" in low  # TDD order is not mechanically enforced
    assert "bash" in low  # shell writes to state.json are best effort
