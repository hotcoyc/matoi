"""Artifact writer — saves pipeline results to files."""

from pathlib import Path

from agency.core.task import TaskResult


class ArtifactWriter:
    """Writes orchestration results as Markdown/JSON artifacts."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    async def write_all(self, task_id: str, result: TaskResult) -> list[str]:
        """Write all artifacts for a completed task. Returns list of file paths."""
        session_dir = self.output_dir / task_id
        session_dir.mkdir(parents=True, exist_ok=True)

        paths: list[str] = []
        paths.append(await self._write_decision(session_dir, result))
        paths.append(await self._write_debate(session_dir, result))
        paths.append(await self._write_conflicts(session_dir, result))
        return paths

    async def _write_decision(self, session_dir: Path, result: TaskResult) -> str:
        raise NotImplementedError

    async def _write_debate(self, session_dir: Path, result: TaskResult) -> str:
        raise NotImplementedError

    async def _write_conflicts(self, session_dir: Path, result: TaskResult) -> str:
        raise NotImplementedError
