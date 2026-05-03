"""7-stage orchestration pipeline.

Stages:
1. Intake — receive raw user request
2. PM Brief — PM formulates goal, constraints, deliverables
3. Independent Expert Pass — each active agent gives independent opinion
4. Conflict Detection — identify real disagreements
5. Debate — structured debate on conflicts only
6. Synthesis — PM synthesizes final decision
7. Artifacts — save all results to files
"""

from matoi.core.task import Task, TaskResult, TaskStatus


class Pipeline:
    """Main orchestration pipeline."""

    def __init__(self, team_name: str) -> None:
        self.team_name = team_name

    async def run(self, task: Task) -> TaskResult:
        """Execute the full 7-stage pipeline."""
        task.status = TaskStatus.BRIEFING
        brief = await self._stage_brief(task)

        task.status = TaskStatus.EXPERT_PASS
        opinions = await self._stage_expert_pass(task, brief)

        task.status = TaskStatus.CONFLICT_DETECTION
        conflicts = await self._stage_conflict_detection(opinions)

        task.status = TaskStatus.DEBATE
        debate_rounds = await self._stage_debate(conflicts)

        task.status = TaskStatus.SYNTHESIS
        result = await self._stage_synthesis(task, brief, opinions, debate_rounds)

        task.status = TaskStatus.ARTIFACTS
        await self._stage_artifacts(task, result)

        task.status = TaskStatus.COMPLETED
        return result

    async def _stage_brief(self, task: Task) -> dict:
        raise NotImplementedError

    async def _stage_expert_pass(self, task: Task, brief: dict) -> list[dict]:
        raise NotImplementedError

    async def _stage_conflict_detection(self, opinions: list[dict]) -> list:
        raise NotImplementedError

    async def _stage_debate(self, conflicts: list) -> list:
        raise NotImplementedError

    async def _stage_synthesis(
        self, task: Task, brief: dict, opinions: list[dict], debate_rounds: list
    ) -> TaskResult:
        raise NotImplementedError

    async def _stage_artifacts(self, task: Task, result: TaskResult) -> None:
        raise NotImplementedError
