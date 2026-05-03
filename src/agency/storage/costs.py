"""Cost tracking — aggregate and report LLM usage costs."""

from agency.core.cost import Budget, CostRecord


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
    def premium_calls(self) -> int:
        return sum(1 for r in self.records if r.model_tier.value == "premium")

    def is_over_budget(self) -> bool:
        return self.total_cost >= self.budget.max_total_usd

    def can_use_premium(self) -> bool:
        return self.premium_calls < self.budget.max_premium_calls

    def summary(self) -> dict:
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "total_calls": len(self.records),
            "premium_calls": self.premium_calls,
            "budget_remaining_usd": round(self.budget.max_total_usd - self.total_cost, 4),
        }
