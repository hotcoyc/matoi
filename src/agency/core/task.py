"""Domain models for tasks and results."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    BRIEFING = "briefing"
    EXPERT_PASS = "expert_pass"
    CONFLICT_DETECTION = "conflict_detection"
    DEBATE = "debate"
    SYNTHESIS = "synthesis"
    ARTIFACTS = "artifacts"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """A user task to be processed by the team."""

    id: str
    description: str
    team_name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)


class Conflict(BaseModel):
    """A detected disagreement between agents."""

    topic: str
    agents: list[str] = Field(description="Slugs of disagreeing agents.")
    positions: dict[str, str] = Field(description="Agent slug -> their position.")
    severity: float = Field(0.5, ge=0.0, le=1.0)


class DebateRound(BaseModel):
    """One round of structured debate."""

    round_number: int
    agent: str
    claim: str
    critique: str = ""
    alternative: str = ""
    tradeoff: str = ""
    recommendation: str = ""


class TaskResult(BaseModel):
    """Final output of the orchestration pipeline."""

    task_id: str
    decision: str
    rationale: str
    rejected_alternatives: list[str] = []
    risks: list[str] = []
    next_steps: list[str] = []
    conflicts: list[Conflict] = []
    debate_rounds: list[DebateRound] = []
    completed_at: datetime = Field(default_factory=datetime.now)
