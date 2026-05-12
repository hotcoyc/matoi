"""Memory system backed by MemPalace -- per-project storage.

Each project gets its own memory in matoi/memory/.
No cross-project contamination.
All methods silently fail if MemPalace is not available.
"""

import os
from pathlib import Path

from rich.console import Console

console = Console()


class MemoryStore:
    """Matoi memory backed by MemPalace. Per-project storage."""

    def __init__(self, project_dir: Path, wing: str = "matoi") -> None:
        self.project_dir = project_dir
        self.wing = wing
        self.palace_path = str(project_dir / "memory" / "palace")
        self.kg_path = str(project_dir / "memory" / "knowledge_graph.sqlite3")

        # Ensure memory dir exists
        (project_dir / "memory").mkdir(parents=True, exist_ok=True)

        # Set env var so MemPalace uses per-project path
        os.environ["MEMPALACE_PALACE_PATH"] = self.palace_path

    def store_artifacts(self, session_id: str, artifacts_dir: Path) -> int:
        """Index pipeline artifacts into per-project MemPalace."""
        try:
            from mempalace.miner import mine

            count = mine(
                project_dir=str(artifacts_dir),
                palace_path=self.palace_path,
                wing_override=self.wing,
            )
            return count or 0
        except Exception:
            return 0

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Semantic search across project memory."""
        try:
            from mempalace.searcher import search_memories

            results = search_memories(
                query=query,
                wing=self.wing,
                n_results=n_results,
            )
            return results if isinstance(results, list) else []
        except Exception:
            return []

    def get_context(self, task_description: str, max_results: int = 5) -> str:
        """Get relevant memory context for a pipeline run."""
        try:
            from mempalace.searcher import search_memories

            results = search_memories(
                query=task_description,
                wing=self.wing,
                n_results=max_results,
            )

            if not results:
                return ""

            lines = ["## Relevant Knowledge from Past Sessions\n"]
            items = results if isinstance(results, list) else []
            for r in items[:max_results]:
                content = ""
                if isinstance(r, dict):
                    content = r.get("document", r.get("content", ""))[:200]
                elif isinstance(r, str):
                    content = r[:200]
                if content:
                    lines.append(f"- {content}")
                    lines.append("")

            return "\n".join(lines) if len(lines) > 1 else ""
        except Exception:
            return ""

    def status(self) -> dict:
        """Get memory status."""
        try:
            from mempalace.miner import status
            return status() or {}
        except Exception:
            return {}

    def add_to_knowledge_graph(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 0.9,
        source_file: str = "",
    ) -> None:
        """Add a triple to the per-project knowledge graph."""
        try:
            from mempalace.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph(db_path=self.kg_path)
            kg.add_triple(
                subject=subject,
                predicate=predicate,
                obj=obj,
                confidence=confidence,
                source_file=source_file,
            )
            kg.close()
        except Exception:
            pass
