"""Structured debate engine.

Protocol per conflict:
1. Round N: Each disagreeing agent states claim + critique of other position
2. After max_rounds or if agents converge: PM makes final call

Produces a debate transcript as markdown artifact.
"""

from rich.console import Console

from matoi.agents.registry import AgentRegistry
from matoi.core.agent import AgentDefinition
from matoi.core.task import Conflict, DebateRound
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import ModelRouter

console = Console()

DEBATE_SYSTEM = """\
You are {name}, a {role}.
Motto: "{motto}"

You are in a structured debate about: {topic}

The other agent's position: {other_position}

Your position from the expert pass: {my_position}

Respond with a structured argument:
1. **Claim**: State your position clearly (1-2 sentences)
2. **Critique**: What's wrong with the other position? Be specific.
3. **Concession**: What part of their argument has merit?
4. **Recommendation**: Your final recommendation considering both sides.

Be direct. No filler. Disagree where you genuinely disagree, concede where they have a point.
"""


class DebateEngine:
    """Manages structured debate between agents on detected conflicts."""

    def __init__(
        self,
        provider: AnthropicProvider,
        router: ModelRouter,
        registry: AgentRegistry,
        max_rounds: int = 2,
    ) -> None:
        self.provider = provider
        self.router = router
        self.registry = registry
        self.max_rounds = max_rounds

    def run_debate(self, conflict: Conflict) -> list[DebateRound]:
        """Run structured debate on a single conflict. Returns rounds."""
        if len(conflict.agents) < 2:
            return []

        rounds: list[DebateRound] = []

        for round_num in range(1, self.max_rounds + 1):
            console.print(f"  [dim]Round {round_num}/{self.max_rounds}: {conflict.topic}[/dim]")

            for i, agent_slug in enumerate(conflict.agents[:2]):
                agent = self.registry.get(agent_slug)
                if not agent:
                    continue

                other_slug = conflict.agents[1 - i] if len(conflict.agents) > 1 else ""
                my_position = conflict.positions.get(agent_slug, "")
                other_position = conflict.positions.get(other_slug, "")

                # Use previous round's recommendation as updated position
                prev_rounds = [r for r in rounds if r.agent == agent_slug]
                if prev_rounds:
                    my_position = prev_rounds[-1].recommendation or my_position

                prev_other = [r for r in rounds if r.agent == other_slug]
                if prev_other:
                    other_position = prev_other[-1].recommendation or other_position

                model_id = self.router.resolve_model(agent, "debate")

                system = DEBATE_SYSTEM.format(
                    name=agent.name,
                    role=agent.role,
                    motto=agent.motto,
                    topic=conflict.topic,
                    other_position=other_position[:500],
                    my_position=my_position[:500],
                )

                try:
                    text, _ = self.provider.call(
                        model_id=model_id,
                        system_prompt=system,
                        user_message=f"Round {round_num}. Make your argument.",
                        max_tokens=800,
                    )
                except Exception:
                    continue

                # Parse structured response
                dr = self._parse_debate_response(text, round_num, agent_slug)
                rounds.append(dr)

                console.print(f"    {agent.name}: {dr.claim[:80]}...")

        return rounds

    def format_transcript(
        self, conflict: Conflict, rounds: list[DebateRound]
    ) -> str:
        """Format debate rounds into a markdown transcript."""
        lines = [
            f"## Debate: {conflict.topic}",
            f"Severity: {conflict.severity}",
            f"Agents: {', '.join(conflict.agents)}",
            "",
        ]

        # Initial positions
        lines.append("### Starting Positions")
        for slug, position in conflict.positions.items():
            agent = self.registry.get(slug)
            name = agent.name if agent else slug
            lines.append(f"**{name}:** {position}")
        lines.append("")

        # Rounds
        current_round = 0
        for dr in rounds:
            if dr.round_number != current_round:
                current_round = dr.round_number
                lines.append(f"### Round {current_round}")
                lines.append("")

            agent = self.registry.get(dr.agent)
            name = agent.name if agent else dr.agent

            lines.append(f"**{name}:**")
            if dr.claim:
                lines.append(f"- Claim: {dr.claim}")
            if dr.critique:
                lines.append(f"- Critique: {dr.critique}")
            if dr.alternative:
                lines.append(f"- Concession: {dr.alternative}")
            if dr.recommendation:
                lines.append(f"- Recommendation: {dr.recommendation}")
            lines.append("")

        return "\n".join(lines)

    def _parse_debate_response(
        self, text: str, round_number: int, agent_slug: str
    ) -> DebateRound:
        """Parse structured debate response into a DebateRound."""
        claim = ""
        critique = ""
        alternative = ""
        recommendation = ""

        current_section = ""
        for line in text.split("\n"):
            line_lower = line.lower().strip()
            if "**claim**" in line_lower or line_lower.startswith("1."):
                current_section = "claim"
                claim = _extract_content(line)
            elif "**critique**" in line_lower or line_lower.startswith("2."):
                current_section = "critique"
                critique = _extract_content(line)
            elif "**concession**" in line_lower or line_lower.startswith("3."):
                current_section = "concession"
                alternative = _extract_content(line)
            elif "**recommendation**" in line_lower or line_lower.startswith("4."):
                current_section = "recommendation"
                recommendation = _extract_content(line)
            elif line.strip():
                # Continuation of current section
                if current_section == "claim":
                    claim += " " + line.strip()
                elif current_section == "critique":
                    critique += " " + line.strip()
                elif current_section == "concession":
                    alternative += " " + line.strip()
                elif current_section == "recommendation":
                    recommendation += " " + line.strip()

        # Fallback: if parsing failed, use full text as claim
        if not claim and text.strip():
            claim = text.strip()[:300]

        return DebateRound(
            round_number=round_number,
            agent=agent_slug,
            claim=claim.strip(),
            critique=critique.strip(),
            alternative=alternative.strip(),
            recommendation=recommendation.strip(),
        )


def _extract_content(line: str) -> str:
    """Extract content after section marker."""
    for marker in ["**Claim**:", "**Critique**:", "**Concession**:", "**Recommendation**:", "1.", "2.", "3.", "4."]:
        if marker in line:
            return line.split(marker, 1)[-1].strip()
    return line.strip()
