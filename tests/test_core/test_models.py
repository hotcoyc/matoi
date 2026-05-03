"""Tests for core domain models."""

from matoi.core.agent import AgentCategory, AgentDefinition, AgentType, ModelPolicy, ModelTier
from matoi.core.cost import Budget, CostRecord
from matoi.core.team import TeamConfig


def test_agent_definition_defaults():
    agent = AgentDefinition(
        name="Test Agent",
        slug="test-agent",
        role="Tester",
        category=AgentCategory.ENGINEERING,
        agent_type=AgentType.EXECUTOR,
        system_prompt="You are a test agent.",
    )
    assert agent.risk_tolerance == 0.5
    assert agent.model_policy.default == ModelTier.BALANCED
    assert agent.avatar_path is None


def test_model_policy():
    policy = ModelPolicy(
        default=ModelTier.BALANCED,
        brief=ModelTier.CHEAP,
        synthesis=ModelTier.PREMIUM,
    )
    assert policy.brief == ModelTier.CHEAP
    assert policy.synthesis == ModelTier.PREMIUM
    assert policy.debate == ModelTier.BALANCED  # default


def test_team_config_count():
    team = TeamConfig(name="test", pm="startup-pm", agents=["eng1", "eng2", "designer"])
    assert team.agent_count() == 4  # 3 agents + PM


def test_cost_record_total():
    record = CostRecord(
        agent_slug="test",
        stage="brief",
        model_tier=ModelTier.CHEAP,
        model_id="claude-haiku-4-5-20251001",
        input_cost=0.001,
        output_cost=0.002,
    )
    assert record.total_cost == 0.003


def test_budget_defaults():
    budget = Budget()
    assert budget.max_total_usd == 5.0
    assert budget.max_debate_rounds == 3
    assert budget.max_premium_calls == 5
