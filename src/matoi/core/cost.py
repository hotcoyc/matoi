"""Domain models for cost tracking."""

from datetime import datetime

from pydantic import BaseModel, Field

from matoi.core.agent import ModelTier


class CostRecord(BaseModel):
    """Cost of a single LLM call."""

    agent_slug: str
    stage: str
    model_tier: ModelTier
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def total_cost(self) -> float:
        return self.input_cost + self.output_cost


class Budget(BaseModel):
    """Budget constraints for a session."""

    max_total_usd: float = Field(5.0, description="Max total cost in USD.")
    max_debate_rounds: int = Field(3, description="Max debate rounds per conflict.")
    max_premium_calls: int = Field(5, description="Max Opus-tier calls per session.")
