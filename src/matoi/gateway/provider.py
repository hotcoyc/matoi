"""Anthropic SDK wrapper with cost calculation, streaming, and error handling."""

import time
from collections.abc import Generator

import anthropic

from matoi.core.cost import CostRecord, ModelTier
from matoi.gateway.router import calculate_cost

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 15]  # seconds between retries


class APIError(Exception):
    """Raised when an API call fails after all retries."""

    def __init__(self, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class AnthropicProvider:
    """Wrapper around Anthropic Python SDK for making LLM calls."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic()

    def call(
        self,
        model_id: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 16384,
    ) -> tuple[str, CostRecord]:
        """Make a non-streaming LLM call with retry. Returns (full_text, cost)."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
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

            except anthropic.RateLimitError as e:
                last_error = e
                delay = _get_retry_delay(e, attempt)
                _log_retry("Rate limited", attempt, delay)
                time.sleep(delay)

            except anthropic.APIConnectionError as e:
                last_error = e
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                _log_retry("Connection error", attempt, delay)
                time.sleep(delay)

            except anthropic.InternalServerError as e:
                last_error = e
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                _log_retry("Server error (5xx)", attempt, delay)
                time.sleep(delay)

            except anthropic.AuthenticationError:
                raise APIError(
                    "Invalid API key. Check your ANTHROPIC_API_KEY.",
                    retryable=False,
                )

            except anthropic.BadRequestError as e:
                raise APIError(f"Bad request: {e}", retryable=False)

            except anthropic.APIStatusError as e:
                if e.status_code == 529:  # Overloaded
                    last_error = e
                    delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                    _log_retry("API overloaded", attempt, delay)
                    time.sleep(delay)
                else:
                    raise APIError(f"API error ({e.status_code}): {e}", retryable=False)

        raise APIError(
            f"Failed after {MAX_RETRIES} retries: {last_error}",
            retryable=True,
        )

    def stream(
        self,
        model_id: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 16384,
    ) -> Generator[str | CostRecord, None, None]:
        """Stream an LLM call with retry. Yields text chunks, then a final CostRecord."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                with self.client.messages.stream(
                    model=model_id,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                ) as stream:
                    for text in stream.text_stream:
                        yield text

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
                return  # success

            except anthropic.RateLimitError as e:
                last_error = e
                delay = _get_retry_delay(e, attempt)
                _log_retry("Rate limited", attempt, delay)
                time.sleep(delay)

            except anthropic.APIConnectionError as e:
                last_error = e
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                _log_retry("Connection error", attempt, delay)
                time.sleep(delay)

            except anthropic.InternalServerError as e:
                last_error = e
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                _log_retry("Server error", attempt, delay)
                time.sleep(delay)

            except anthropic.AuthenticationError:
                raise APIError(
                    "Invalid API key. Check your ANTHROPIC_API_KEY.",
                    retryable=False,
                )

            except anthropic.BadRequestError as e:
                raise APIError(f"Bad request: {e}", retryable=False)

            except anthropic.APIStatusError as e:
                if e.status_code == 529:
                    last_error = e
                    delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                    _log_retry("API overloaded", attempt, delay)
                    time.sleep(delay)
                else:
                    raise APIError(f"API error ({e.status_code}): {e}", retryable=False)

        raise APIError(
            f"Failed after {MAX_RETRIES} retries: {last_error}",
            retryable=True,
        )

    def _infer_tier(self, model_id: str) -> ModelTier:
        if "haiku" in model_id:
            return ModelTier.CHEAP
        if "opus" in model_id:
            return ModelTier.PREMIUM
        return ModelTier.BALANCED


def _get_retry_delay(error: anthropic.RateLimitError, attempt: int) -> float:
    """Extract retry-after from headers, or use exponential backoff."""
    try:
        if hasattr(error, "response") and error.response is not None:
            retry_after = error.response.headers.get("retry-after")
            if retry_after:
                return float(retry_after)
    except (ValueError, AttributeError):
        pass
    return RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]


def _log_retry(reason: str, attempt: int, delay: float) -> None:
    """Print retry info to stderr."""
    from rich.console import Console
    console = Console(stderr=True)
    console.print(
        f"  [yellow]{reason}. Retry {attempt + 1}/{MAX_RETRIES} in {delay:.0f}s...[/yellow]"
    )
