"""Selective activation — PM recommends which agents to activate for a task.

Uses LLM (Haiku) to analyze the task and select relevant agents
from the team, avoiding unnecessary API calls.
"""

import json

from rich.console import Console

from matoi.core.agent import AgentDefinition, ModelTier
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import MODEL_MAP

console = Console()

ACTIVATION_PROMPT = """\
You are a project manager deciding which team members to activate for a task.

Available agents:
{agents_list}

Task: {task}

Select ONLY the agents whose expertise is directly relevant to this task.
Do NOT activate agents "just in case" -- each agent costs money and time.

Rules:
- For market/business tasks: activate researchers, analysts, marketers. Skip engineers.
- For technical tasks: activate engineers, architects. Skip marketers, researchers.
- For product tasks: activate designers, researchers, engineers.
- For strategy tasks: activate analysts, researchers, strategists.
- Always be selective. 2-3 agents is usually enough. 4 is the max.

Return a JSON array of agent slugs to activate.
Example: ["market-researcher", "business-analyst", "growth-marketer"]

Return ONLY valid JSON, no markdown fences, no explanation.
"""


class ActivationEngine:
    """PM recommends which agents to activate for a given task."""

    def __init__(self, provider: AnthropicProvider) -> None:
        self.provider = provider

    def select_active(
        self,
        agents: list[AgentDefinition],
        task_description: str,
    ) -> list[AgentDefinition]:
        """Return the subset of agents that should be activated."""
        if len(agents) <= 2:
            return agents  # no point filtering with 2 or fewer

        agents_list = ""
        for a in agents:
            agents_list += (
                f"- {a.slug}: {a.name} ({a.role}). "
                f"Category: {a.category.value}. "
                f"Strengths: {', '.join(a.strengths[:3])}. "
                f"Activation rules: {'; '.join(a.activation_rules[:2])}\n"
            )

        prompt = ACTIVATION_PROMPT.format(
            agents_list=agents_list,
            task=task_description,
        )

        model_id = MODEL_MAP[ModelTier.CHEAP]  # Haiku

        try:
            text, _ = self.provider.call(
                model_id=model_id,
                system_prompt=prompt,
                user_message=task_description,
                max_tokens=200,
            )
        except Exception:
            return agents  # fallback: activate all

        # Parse response
        try:
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            selected_slugs = json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return agents

        if not isinstance(selected_slugs, list) or not selected_slugs:
            return agents

        # Filter agents by selected slugs
        slug_set = set(selected_slugs)
        active = [a for a in agents if a.slug in slug_set]

        # Fallback: if LLM returned nonsense, keep all
        if not active:
            return agents

        return active
