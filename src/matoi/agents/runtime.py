"""Agent runtime — context builder and prompt assembly."""

from matoi.core.agent import AgentDefinition


class AgentRuntime:
    """Builds context and runs an agent against the model gateway."""

    def __init__(self, agent: AgentDefinition) -> None:
        self.agent = agent

    def build_system_prompt(self, task_context: str = "") -> str:
        """Assemble the full system prompt for this agent."""
        parts = [
            f"You are {self.agent.name}, a {self.agent.role}.",
            f"Motto: {self.agent.motto}" if self.agent.motto else "",
            "",
            self.agent.system_prompt,
        ]
        if task_context:
            parts.extend(["", "## Current Task Context", task_context])
        return "\n".join(parts).strip()

    async def execute(self, user_message: str, task_context: str = "") -> str:
        """Run the agent and return its response."""
        raise NotImplementedError
