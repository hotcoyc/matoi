"""Tests for ConflictDetector (unit tests with mock provider)."""

from matoi.core.task import Conflict


def test_conflict_model():
    conflict = Conflict(
        topic="Tech stack choice",
        agents=["backend-engineer", "frontend-engineer"],
        positions={
            "backend-engineer": "Use Python + FastAPI",
            "frontend-engineer": "Use Node.js + Express for full-stack",
        },
        severity=0.7,
    )
    assert conflict.severity == 0.7
    assert len(conflict.agents) == 2
    assert "backend-engineer" in conflict.positions


def test_conflict_severity_bounds():
    low = Conflict(topic="minor", agents=[], positions={}, severity=0.0)
    high = Conflict(topic="major", agents=[], positions={}, severity=1.0)
    assert low.severity == 0.0
    assert high.severity == 1.0
