"""Tests for config models."""

from matoi.core.config import GlobalConfig, ProjectConfig


def test_global_config_defaults():
    config = GlobalConfig()
    assert config.anthropic_api_key == ""


def test_project_config_defaults():
    config = ProjectConfig()
    assert config.team_name == ""
    assert config.pm == ""
    assert config.agents == []


def test_project_config_with_team():
    config = ProjectConfig(
        team_name="my-team",
        pm="startup-pm",
        agents=["backend-engineer", "market-researcher"],
        project_name="test-project",
    )
    assert config.pm == "startup-pm"
    assert len(config.agents) == 2
    assert config.project_name == "test-project"
