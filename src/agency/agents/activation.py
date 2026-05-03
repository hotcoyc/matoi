"""Selective activation logic — not all agents are active for every task."""

from agency.core.agent import AgentDefinition


class ActivationEngine:
    """Determines which agents should be active for a given task."""

    def select_active(
        self,
        agents: list[AgentDefinition],
        task_description: str,
    ) -> list[AgentDefinition]:
        """Return the subset of agents that should be activated."""
        raise NotImplementedError
