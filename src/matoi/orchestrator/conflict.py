"""Conflict detection between agent opinions.

Uses LLM (Haiku -- cheap) to compare agent opinions and identify
real disagreements worth debating.
"""

import json

from rich.console import Console

from matoi.core.task import Conflict
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import MODEL_MAP
from matoi.core.agent import ModelTier

console = Console()

DETECT_PROMPT = """\
You are a conflict detection system. Compare the following agent opinions \
and identify REAL disagreements -- not minor phrasing differences.

A conflict is real when:
- Agents recommend different approaches (e.g. build vs buy)
- Agents disagree on priorities (e.g. speed vs quality)
- Agents make contradictory assumptions
- Agents propose incompatible technical choices

A conflict is NOT real when:
- Agents say the same thing differently
- One agent covers a topic another doesn't mention
- Agents agree on the conclusion but give different reasons

Return a JSON array of conflicts. Each conflict:
{
  "topic": "Short description of the disagreement (max 10 words)",
  "agents": ["agent_slug_1", "agent_slug_2"],
  "positions": {"agent_slug_1": "Their position in 1 sentence", "agent_slug_2": "Their position in 1 sentence"},
  "severity": 0.0-1.0 (1.0 = fundamental disagreement, 0.3 = minor preference)
}

Only include conflicts with severity >= 0.5. Return empty array [] if no real conflicts.
Return ONLY valid JSON, no markdown fences.
"""


class ConflictDetector:
    """Analyzes independent expert opinions to find meaningful disagreements."""

    def __init__(self, provider: AnthropicProvider, min_severity: float = 0.5) -> None:
        self.provider = provider
        self.min_severity = min_severity

    def detect(self, opinions: dict[str, str]) -> list[Conflict]:
        """Return list of detected conflicts from agent opinions."""
        if len(opinions) < 2:
            return []

        opinions_text = ""
        for slug, opinion in opinions.items():
            opinions_text += f"\n### Agent: {slug}\n{opinion[:2000]}\n"

        model_id = MODEL_MAP[ModelTier.CHEAP]  # Haiku -- cheap detection

        console.print("  [dim]Scanning for conflicts...[/dim]")

        try:
            text, _ = self.provider.call(
                model_id=model_id,
                system_prompt=DETECT_PROMPT,
                user_message=opinions_text,
                max_tokens=1500,
            )
        except Exception as e:
            console.print(f"  [yellow]Conflict detection failed: {e}[/yellow]")
            return []

        # Parse response
        try:
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            data = json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return []

        conflicts = []
        for item in data:
            try:
                severity = float(item.get("severity", 0))
                if severity >= self.min_severity:
                    conflicts.append(Conflict(
                        topic=item["topic"],
                        agents=item.get("agents", []),
                        positions=item.get("positions", {}),
                        severity=severity,
                    ))
            except (ValueError, KeyError):
                continue

        return conflicts
