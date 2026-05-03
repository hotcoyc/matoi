"""Cost-intelligent model routing."""

from matoi.core.agent import AgentDefinition, ModelTier


# Model ID mapping — update when new models are available
MODEL_MAP: dict[ModelTier, str] = {
    ModelTier.CHEAP: "claude-haiku-4-5-20251001",
    ModelTier.BALANCED: "claude-sonnet-4-6",
    ModelTier.PREMIUM: "claude-opus-4-6",
}


class ModelRouter:
    """Routes requests to the appropriate model tier based on agent policy and stage."""

    def resolve_model(self, agent: AgentDefinition, stage: str) -> str:
        """Return the model ID for a given agent and pipeline stage."""
        policy = agent.model_policy
        tier = getattr(policy, stage, policy.default)
        return MODEL_MAP[tier]
