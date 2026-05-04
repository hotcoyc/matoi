"""Anthropic SDK wrapper with cost calculation and streaming."""

from collections.abc import Generator

import anthropic

from matoi.core.cost import CostRecord, ModelTier
from matoi.gateway.router import calculate_cost


class AnthropicProvider:
    """Wrapper around Anthropic Python SDK for making LLM calls."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic()

    def call(
        self,
        model_id: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
    ) -> tuple[str, CostRecord]:
        """Make a non-streaming LLM call. Returns (full_text, cost)."""
        message = self.client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        input_cost, output_cost = calculate_cost(model_id, input_tokens, output_tokens)

        cost = CostRecord(
            agent_slug="",
            stage="",
            model_tier=self._infer_tier(model_id),
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
        )

        return message.content[0].text, cost

    def stream(
        self,
        model_id: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
    ) -> Generator[str | CostRecord, None, None]:
        """Stream an LLM call. Yields text chunks, then a final CostRecord."""
        with self.client.messages.stream(
            model=model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text in stream.text_stream:
                yield text

            # After stream completes, get final message for usage
            message = stream.get_final_message()

        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        input_cost, output_cost = calculate_cost(model_id, input_tokens, output_tokens)

        yield CostRecord(
            agent_slug="",
            stage="",
            model_tier=self._infer_tier(model_id),
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
        )

    def _infer_tier(self, model_id: str) -> ModelTier:
        if "haiku" in model_id:
            return ModelTier.CHEAP
        if "opus" in model_id:
            return ModelTier.PREMIUM
        return ModelTier.BALANCED
