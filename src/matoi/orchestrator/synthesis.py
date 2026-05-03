"""Synthesis engine — PM synthesizes final decision."""

from matoi.core.task import DebateRound, TaskResult


class SynthesisEngine:
    """PM or synthesizer agent produces the final decision."""

    async def synthesize(
        self,
        brief: dict,
        opinions: list[dict],
        debate_rounds: list[DebateRound],
    ) -> TaskResult:
        """Synthesize final decision from all inputs."""
        raise NotImplementedError
