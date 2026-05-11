"""Context compaction -- compress old messages when context grows too large.

When conversation history reaches COMPACTION_THRESHOLD (85%) of the model's
context window, old messages are summarized into a compact summary.
Recent messages (last KEEP_RECENT) are kept verbatim.
Full history is preserved in MemPalace -- compaction only affects the
API call context, not long-term memory.
"""

from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import MODEL_MAP
from matoi.core.agent import ModelTier

# Approximate context windows per model tier (tokens)
CONTEXT_WINDOWS = {
    "claude-haiku-4-5-20251001": 200_000,
    "claude-sonnet-4-6": 200_000,
    "claude-opus-4-6": 200_000,
}

DEFAULT_WINDOW = 200_000
COMPACTION_THRESHOLD = 0.85  # trigger at 85% of window
KEEP_RECENT = 6  # keep last N messages verbatim
APPROX_TOKENS_PER_CHAR = 0.25  # rough estimate: 1 token ~ 4 chars


def estimate_tokens(text: str) -> int:
    """Rough token count estimate."""
    return int(len(text) * APPROX_TOKENS_PER_CHAR)


def estimate_history_tokens(history: list[dict]) -> int:
    """Estimate total tokens in conversation history."""
    total = 0
    for msg in history:
        total += estimate_tokens(msg.get("content", ""))
        total += estimate_tokens(msg.get("role", ""))
    return total


def needs_compaction(history: list[dict], model_id: str = "") -> bool:
    """Check if history needs compaction."""
    if len(history) <= KEEP_RECENT + 2:
        return False
    window = CONTEXT_WINDOWS.get(model_id, DEFAULT_WINDOW)
    tokens = estimate_history_tokens(history)
    return tokens > (window * COMPACTION_THRESHOLD)


def compact_history(
    history: list[dict],
    provider: AnthropicProvider,
) -> list[dict]:
    """Compress old messages into a summary, keep recent ones verbatim.

    Returns new history: [summary_message] + recent_messages.
    """
    if len(history) <= KEEP_RECENT + 2:
        return history

    old_messages = history[:-KEEP_RECENT]
    recent_messages = history[-KEEP_RECENT:]

    # Build text from old messages
    old_text = ""
    for msg in old_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        old_text += f"[{role}]: {content[:500]}\n\n"

    # Summarize using Haiku (cheapest)
    model_id = MODEL_MAP[ModelTier.CHEAP]

    system = (
        "Summarize this conversation history into a concise context summary. "
        "Preserve: key decisions, important facts, action items, agent names. "
        "Drop: filler, repeated information, verbose explanations. "
        "Max 500 words. Write as bullet points."
    )

    try:
        summary_text, _ = provider.call(
            model_id=model_id,
            system_prompt=system,
            user_message=old_text[:10000],  # cap to avoid huge input
            max_tokens=800,
        )
    except Exception:
        # If summarization fails, just truncate
        summary_text = f"[Session context: {len(old_messages)} earlier messages not shown]"

    # Build new compacted history
    summary_message = {
        "role": "system",
        "content": f"[Context from earlier in this session]\n{summary_text}",
    }

    return [summary_message] + recent_messages
