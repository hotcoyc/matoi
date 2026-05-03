"""Structured debate engine.

Debate protocol:
1. Claim — agent states their position
2. Critique — opposing agent critiques
3. Alternative — propose a different approach
4. Tradeoff — articulate the tradeoff
5. Recommendation — final recommendation from this round
"""

from agency.core.task import Conflict, DebateRound


class DebateEngine:
    """Manages structured debate between agents on detected conflicts."""

    def __init__(self, max_rounds: int = 3) -> None:
        self.max_rounds = max_rounds

    async def run_debate(self, conflict: Conflict) -> list[DebateRound]:
        """Run structured debate on a single conflict."""
        raise NotImplementedError
