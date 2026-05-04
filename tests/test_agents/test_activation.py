"""Tests for activation engine models (no API calls)."""

from matoi.core.agent import AgentCategory, AgentDefinition, AgentType


def _make_agent(slug: str, category: str, activation_rules: list[str] = None) -> AgentDefinition:
    return AgentDefinition(
        name=slug.replace("-", " ").title(),
        slug=slug,
        role=f"Role for {slug}",
        category=AgentCategory(category),
        agent_type=AgentType.EXECUTOR,
        system_prompt="test",
        activation_rules=activation_rules or [],
    )


def test_agent_activation_rules():
    agent = _make_agent(
        "backend-engineer",
        "engineering",
        activation_rules=[
            "Active when task involves backend code, APIs, databases",
            "Skipped for pure strategy, marketing, or research tasks",
        ],
    )
    assert len(agent.activation_rules) == 2
    assert "backend" in agent.activation_rules[0]
    assert "Skipped" in agent.activation_rules[1]


def test_agents_have_different_categories():
    eng = _make_agent("backend-engineer", "engineering")
    mkt = _make_agent("growth-marketer", "marketing")
    res = _make_agent("market-researcher", "research")
    assert eng.category != mkt.category
    assert mkt.category != res.category
