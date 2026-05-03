"""Conflict detection between agent opinions.

Detects real disagreements:
- Different tech stack choices
- Different product tradeoffs
- Different architectural assumptions
- Different UX priorities
- Different scope decisions
"""

from agency.core.task import Conflict


class ConflictDetector:
    """Analyzes independent expert opinions to find meaningful disagreements."""

    async def detect(self, opinions: list[dict]) -> list[Conflict]:
        """Return list of detected conflicts from agent opinions."""
        raise NotImplementedError
