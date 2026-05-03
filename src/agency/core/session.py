"""Domain models for sessions."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from agency.core.cost import CostRecord


class SessionState(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Session(BaseModel):
    """A complete orchestration session."""

    id: str
    task_description: str
    team_name: str
    state: SessionState = SessionState.ACTIVE
    started_at: datetime = Field(default_factory=datetime.now)
    finished_at: datetime | None = None
    costs: list[CostRecord] = []
    artifact_paths: list[str] = []

    @property
    def total_cost(self) -> float:
        return sum(c.total_cost for c in self.costs)
