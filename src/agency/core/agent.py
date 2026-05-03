"""Domain models for agent definitions."""

from enum import Enum

from pydantic import BaseModel, Field


class AgentCategory(str, Enum):
    STRATEGY = "strategy"
    RESEARCH = "research"
    MARKETING = "marketing"
    DESIGN = "design"
    ENGINEERING = "engineering"
    QUALITY = "quality"


class AgentType(str, Enum):
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    THINKER = "thinker"
    CRITIC = "critic"


class ModelTier(str, Enum):
    CHEAP = "cheap"        # Haiku
    BALANCED = "balanced"  # Sonnet
    PREMIUM = "premium"    # Opus


class ModelPolicy(BaseModel):
    """Per-stage model tier assignment."""

    default: ModelTier = ModelTier.BALANCED
    brief: ModelTier = ModelTier.CHEAP
    expert_pass: ModelTier = ModelTier.BALANCED
    debate: ModelTier = ModelTier.BALANCED
    synthesis: ModelTier = ModelTier.PREMIUM


class AgentDefinition(BaseModel):
    """An agent loaded from a .md registry file."""

    name: str
    slug: str = Field(description="Filename-safe identifier, e.g. 'startup-pm'.")
    role: str
    category: AgentCategory
    agent_type: AgentType
    motto: str = ""
    system_prompt: str = Field(description="Markdown body of the agent file.")

    responsibilities: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    tools: list[str] = []

    model_policy: ModelPolicy = Field(default_factory=ModelPolicy)

    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0)
    debate_style: str = "balanced"
    collaboration_preferences: list[str] = []
    activation_rules: list[str] = []

    avatar_path: str | None = Field(None, description="Path to Braille-art avatar file.")
