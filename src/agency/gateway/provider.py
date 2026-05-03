"""Anthropic SDK wrapper."""

import anthropic

from agency.core.cost import CostRecord, ModelTier


class AnthropicProvider:
    """Wrapper around Anthropic Python SDK for making LLM calls."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic()

    async def call(
        self,
        model_id: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
    ) -> tuple[str, CostRecord]:
        """Make an LLM call and return (response_text, cost_record)."""
        message = self.client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        tier = self._infer_tier(model_id)
        cost = CostRecord(
            agent_slug="",  # caller fills this in
            stage="",       # caller fills this in
            model_tier=tier,
            model_id=model_id,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )

        return message.content[0].text, cost

    def _infer_tier(self, model_id: str) -> ModelTier:
        if "haiku" in model_id:
            return ModelTier.CHEAP
        if "opus" in model_id:
            return ModelTier.PREMIUM
        return ModelTier.BALANCED
