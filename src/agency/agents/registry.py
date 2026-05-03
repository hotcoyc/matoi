"""Agent registry — loads agent definitions from .md files."""

from pathlib import Path

import frontmatter

from agency.core.agent import AgentDefinition, ModelPolicy


class AgentRegistry:
    """Loads and manages agent definitions from Markdown + YAML frontmatter files."""

    def __init__(self, agents_dir: Path) -> None:
        self.agents_dir = agents_dir
        self._agents: dict[str, AgentDefinition] = {}

    def load_all(self) -> None:
        """Load all agent .md files from the registry directory."""
        for md_file in self.agents_dir.rglob("*.md"):
            agent = self._parse_agent_file(md_file)
            self._agents[agent.slug] = agent

    def get(self, slug: str) -> AgentDefinition | None:
        return self._agents.get(slug)

    def list_all(self) -> list[AgentDefinition]:
        return list(self._agents.values())

    def list_by_category(self, category: str) -> list[AgentDefinition]:
        return [a for a in self._agents.values() if a.category.value == category]

    def list_by_type(self, agent_type: str) -> list[AgentDefinition]:
        return [a for a in self._agents.values() if a.agent_type.value == agent_type]

    def _parse_agent_file(self, path: Path) -> AgentDefinition:
        """Parse a single agent .md file with YAML frontmatter."""
        post = frontmatter.load(path)
        meta = post.metadata

        model_policy_data = meta.get("model_policy", {})
        model_policy = ModelPolicy(**model_policy_data) if model_policy_data else ModelPolicy()

        return AgentDefinition(
            name=meta["name"],
            slug=path.stem,
            role=meta["role"],
            category=meta["category"],
            agent_type=meta["type"],
            motto=meta.get("motto", ""),
            system_prompt=post.content,
            responsibilities=meta.get("responsibilities", []),
            strengths=meta.get("strengths", []),
            weaknesses=meta.get("weaknesses", []),
            tools=meta.get("tools", []),
            model_policy=model_policy,
            risk_tolerance=meta.get("risk_tolerance", 0.5),
            debate_style=meta.get("debate_style", "balanced"),
            collaboration_preferences=meta.get("collaboration_preferences", []),
            activation_rules=meta.get("activation_rules", []),
            avatar_path=meta.get("avatar_path"),
        )
