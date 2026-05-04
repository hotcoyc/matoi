"""Tests for DebateEngine models and parsing."""

from matoi.core.task import Conflict, DebateRound


def test_debate_round_model():
    dr = DebateRound(
        round_number=1,
        agent="backend-engineer",
        claim="We should use PostgreSQL",
        critique="MongoDB lacks ACID guarantees",
        alternative="Could consider CockroachDB",
        recommendation="PostgreSQL for MVP, revisit at scale",
    )
    assert dr.round_number == 1
    assert dr.agent == "backend-engineer"
    assert "PostgreSQL" in dr.claim
    assert "ACID" in dr.critique


def test_debate_round_defaults():
    dr = DebateRound(round_number=1, agent="test", claim="My position")
    assert dr.critique == ""
    assert dr.alternative == ""
    assert dr.recommendation == ""


def test_debate_round_from_conflict():
    conflict = Conflict(
        topic="Database choice",
        agents=["agent-a", "agent-b"],
        positions={"agent-a": "SQL", "agent-b": "NoSQL"},
        severity=0.8,
    )
    # Create rounds from conflict
    rounds = [
        DebateRound(
            round_number=1,
            agent=conflict.agents[0],
            claim=conflict.positions[conflict.agents[0]],
        ),
        DebateRound(
            round_number=1,
            agent=conflict.agents[1],
            claim=conflict.positions[conflict.agents[1]],
        ),
    ]
    assert len(rounds) == 2
    assert rounds[0].claim == "SQL"
    assert rounds[1].claim == "NoSQL"
