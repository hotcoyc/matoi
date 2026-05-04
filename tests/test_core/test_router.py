"""Tests for ModelRouter and pricing."""

from matoi.core.agent import AgentCategory, AgentDefinition, AgentType, ModelPolicy, ModelTier
from matoi.gateway.router import MODEL_MAP, ModelRouter, calculate_cost


def _make_agent(brief: str = "cheap", expert: str = "balanced", synthesis: str = "premium") -> AgentDefinition:
    return AgentDefinition(
        name="Test",
        slug="test",
        role="Tester",
        category=AgentCategory.ENGINEERING,
        agent_type=AgentType.EXECUTOR,
        system_prompt="test",
        model_policy=ModelPolicy(
            brief=ModelTier(brief),
            expert_pass=ModelTier(expert),
            synthesis=ModelTier(synthesis),
        ),
    )


def test_model_map_has_all_tiers():
    assert ModelTier.CHEAP in MODEL_MAP
    assert ModelTier.BALANCED in MODEL_MAP
    assert ModelTier.PREMIUM in MODEL_MAP


def test_resolve_model_by_stage():
    router = ModelRouter()
    agent = _make_agent()
    assert "haiku" in router.resolve_model(agent, "brief")
    assert "sonnet" in router.resolve_model(agent, "expert_pass")
    assert "opus" in router.resolve_model(agent, "synthesis")


def test_resolve_model_default_fallback():
    router = ModelRouter()
    agent = _make_agent()
    # Unknown stage falls back to default (balanced)
    model = router.resolve_model(agent, "nonexistent_stage")
    assert "sonnet" in model


def test_calculate_cost_haiku():
    input_cost, output_cost = calculate_cost("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
    assert input_cost == 1.0
    assert output_cost == 5.0


def test_calculate_cost_sonnet():
    input_cost, output_cost = calculate_cost("claude-sonnet-4-6", 1_000_000, 1_000_000)
    assert input_cost == 3.0
    assert output_cost == 15.0


def test_calculate_cost_opus():
    input_cost, output_cost = calculate_cost("claude-opus-4-6", 1_000_000, 1_000_000)
    assert input_cost == 15.0
    assert output_cost == 75.0


def test_calculate_cost_unknown_model():
    input_cost, output_cost = calculate_cost("unknown-model", 1_000_000, 1_000_000)
    assert input_cost == 0.0
    assert output_cost == 0.0


def test_calculate_cost_small_usage():
    input_cost, output_cost = calculate_cost("claude-haiku-4-5-20251001", 500, 200)
    assert input_cost == 0.0005  # 500/1M * $1
    assert output_cost == 0.001  # 200/1M * $5
