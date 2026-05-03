"""Domain models for team composition."""

from pydantic import BaseModel, Field


class TeamConfig(BaseModel):
    """A user-defined team of agents."""

    name: str
    pm: str = Field(description="Slug of the PM agent leading this team.")
    agents: list[str] = Field(
        default_factory=list,
        description="Slugs of agents in the team (max 5).",
    )
    description: str = ""

    def agent_count(self) -> int:
        return len(self.agents) + 1  # +1 for PM


class TeamPreset(BaseModel):
    """A pre-configured team template."""

    name: str
    description: str
    pm: str
    agents: list[str]
    recommended_for: list[str] = Field(
        default_factory=list,
        description="Task types this preset is good for.",
    )
