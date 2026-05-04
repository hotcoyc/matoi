"""Tests for CostTracker."""

from matoi.core.agent import ModelTier
from matoi.core.cost import Budget, CostRecord
from matoi.storage.costs import CostTracker


def _make_record(agent: str = "test", stage: str = "brief", tier: str = "cheap",
                 input_tokens: int = 100, output_tokens: int = 50,
                 input_cost: float = 0.0001, output_cost: float = 0.00025) -> CostRecord:
    return CostRecord(
        agent_slug=agent,
        stage=stage,
        model_tier=ModelTier(tier),
        model_id=f"claude-{tier}",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
    )


def test_empty_tracker():
    tracker = CostTracker()
    assert tracker.total_cost == 0.0
    assert tracker.total_tokens == 0
    assert tracker.premium_calls == 0
    assert not tracker.is_over_budget()


def test_record_cost():
    tracker = CostTracker()
    tracker.record(_make_record())
    assert tracker.total_cost > 0
    assert tracker.total_tokens == 150
    assert len(tracker.records) == 1


def test_budget_enforcement():
    tracker = CostTracker(Budget(max_total_usd=0.001))
    tracker.record(_make_record(input_cost=0.0005, output_cost=0.0006))
    assert tracker.is_over_budget()


def test_premium_call_limit():
    tracker = CostTracker(Budget(max_premium_calls=2))
    tracker.record(_make_record(tier="premium"))
    assert tracker.can_use_premium()
    tracker.record(_make_record(tier="premium"))
    assert not tracker.can_use_premium()


def test_summary_breakdown():
    tracker = CostTracker()
    tracker.record(_make_record(agent="pm", stage="brief"))
    tracker.record(_make_record(agent="eng", stage="expert_pass"))
    summary = tracker.summary()
    assert summary["total_calls"] == 2
    assert len(summary["breakdown"]) == 2
    assert summary["breakdown"][0]["agent"] == "pm"
    assert summary["breakdown"][1]["agent"] == "eng"
