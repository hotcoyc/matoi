"""Tests for agent registry."""

from pathlib import Path

from agency.agents.registry import AgentRegistry


AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"


def test_load_all_agents():
    registry = AgentRegistry(AGENTS_DIR)
    registry.load_all()
    agents = registry.list_all()
    assert len(agents) >= 4  # at least 4 PM agents


def test_get_startup_pm():
    registry = AgentRegistry(AGENTS_DIR)
    registry.load_all()
    pm = registry.get("startup-pm")
    assert pm is not None
    assert pm.name == "Startup PM"
    assert pm.risk_tolerance == 0.8
    assert pm.motto == "Ship it by Friday."


def test_list_by_type():
    registry = AgentRegistry(AGENTS_DIR)
    registry.load_all()
    coordinators = registry.list_by_type("coordinator")
    assert len(coordinators) >= 4
