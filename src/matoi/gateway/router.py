"""Cost-intelligent model routing with pricing."""

from matoi.core.agent import AgentDefinition, ModelTier


# Model ID mapping
MODEL_MAP: dict[ModelTier, str] = {
    ModelTier.CHEAP: "claude-haiku-4-5-20251001",
    ModelTier.BALANCED: "claude-sonnet-4-6",
    ModelTier.PREMIUM: "claude-opus-4-6",
}

# Pricing per million tokens (USD), as of May 2026
# Source: https://docs.anthropic.com/en/docs/about-claude/models
MODEL_PRICING: dict[str, tuple[float, float]] = {
    # model_id: (input_per_1M, output_per_1M)
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-6": (15.00, 75.00),
}


def calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> tuple[float, float]:
    """Calculate cost in USD for a given model and token counts.

    Returns (input_cost, output_cost).
    """
    pricing = MODEL_PRICING.get(model_id)
    if not pricing:
        return 0.0, 0.0

    input_per_1m, output_per_1m = pricing
    input_cost = (input_tokens / 1_000_000) * input_per_1m
    output_cost = (output_tokens / 1_000_000) * output_per_1m
    return input_cost, output_cost


class ModelRouter:
    """Routes requests to the appropriate model tier based on agent policy and stage."""

    def resolve_model(self, agent: AgentDefinition, stage: str) -> str:
        """Return the model ID for a given agent and pipeline stage."""
        policy = agent.model_policy
        tier = getattr(policy, stage, policy.default)
        return MODEL_MAP[tier]
