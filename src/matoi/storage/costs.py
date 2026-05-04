"""Cost tracking — aggregate and report LLM usage costs."""

from matoi.core.cost import Budget, CostRecord


class CostTracker:
    """Tracks costs during a session and enforces budget limits."""

    def __init__(self, budget: Budget | None = None) -> None:
        self.budget = budget or Budget()
        self.records: list[CostRecord] = []

    def record(self, cost: CostRecord) -> None:
        self.records.append(cost)

    @property
    def total_cost(self) -> float:
        return sum(r.total_cost for r in self.records)

    @property
    def total_tokens(self) -> int:
        return sum(r.input_tokens + r.output_tokens for r in self.records)

    @property
    def premium_calls(self) -> int:
        return sum(1 for r in self.records if r.model_tier.value == "premium")

    def is_over_budget(self) -> bool:
        return self.total_cost >= self.budget.max_total_usd

    def can_use_premium(self) -> bool:
        return self.premium_calls < self.budget.max_premium_calls

    def summary(self) -> dict:
        return {
            "total_cost_usd": round(self.total_cost, 6),
            "total_tokens": self.total_tokens,
            "total_calls": len(self.records),
            "premium_calls": self.premium_calls,
            "budget_remaining_usd": round(self.budget.max_total_usd - self.total_cost, 6),
            "breakdown": self._breakdown(),
        }

    def _breakdown(self) -> list[dict]:
        """Per-call cost breakdown."""
        rows = []
        for r in self.records:
            rows.append({
                "agent": r.agent_slug,
                "stage": r.stage,
                "model": r.model_id,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "cost_usd": round(r.total_cost, 6),
            })
        return rows
