"""Memory system backed by MemPalace.

Uses MemPalace for:
- Semantic search across past sessions
- Knowledge graph (entities + triples)
- Per-agent wings for multi-agent memory
- Auto-indexing of pipeline artifacts
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from rich.console import Console

console = Console()


class MemoryStore:
    """Matoi memory backed by MemPalace."""

    def __init__(self, project_dir: Path, wing: str = "matoi") -> None:
        self.project_dir = project_dir
        self.wing = wing

    def store_artifacts(self, session_id: str, artifacts_dir: Path) -> int:
        """Index pipeline artifacts into MemPalace. Returns drawer count."""
        try:
            from mempalace.miner import mine_directory

            count = mine_directory(
                str(artifacts_dir),
                wing=self.wing,
                mode="projects",
            )
            return count
        except ImportError:
            console.print("[yellow]mempalace not installed, skipping memory storage.[/yellow]")
            return 0
        except Exception as e:
            console.print(f"[yellow]Memory storage failed: {e}[/yellow]")
            return 0

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Semantic search across memory."""
        try:
            from mempalace.searcher import search_memories

            results = search_memories(
                query=query,
                wing=self.wing,
                n_results=n_results,
            )
            return results if isinstance(results, list) else results.get("results", [])
        except ImportError:
            return []
        except Exception:
            return []

    def get_context(self, task_description: str, max_results: int = 5) -> str:
        """Get relevant memory context for a pipeline run."""
        try:
            from mempalace.layers import MemoryStack

            stack = MemoryStack()

            # Layer 3: semantic search for relevant past knowledge
            results = stack.search(task_description, wing=self.wing, n_results=max_results)

            if not results:
                return ""

            lines = ["## Relevant Knowledge from Past Sessions\n"]

            if isinstance(results, list):
                for r in results[:max_results]:
                    content = r.get("document", r.get("content", ""))[:200]
                    source = r.get("metadata", {}).get("source", "")
                    if content:
                        lines.append(f"- {content}")
                        if source:
                            lines.append(f"  *(from {source})*")
                        lines.append("")
            elif isinstance(results, dict):
                for doc in results.get("documents", [[]])[0][:max_results]:
                    if doc:
                        lines.append(f"- {doc[:200]}")
                        lines.append("")

            return "\n".join(lines) if len(lines) > 1 else ""
        except ImportError:
            return ""
        except Exception:
            return ""

    def wake_up(self) -> str:
        """Get Layer 0 + Layer 1 context (~600-900 tokens)."""
        try:
            from mempalace.layers import MemoryStack

            stack = MemoryStack()
            return stack.wake_up(wing=self.wing)
        except (ImportError, Exception):
            return ""

    def status(self) -> dict:
        """Get memory status."""
        try:
            from mempalace.layers import MemoryStack

            stack = MemoryStack()
            return stack.status()
        except (ImportError, Exception):
            return {"drawers": 0, "wings": [], "rooms": []}

    def add_to_knowledge_graph(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 0.9,
        source_file: str = "",
    ) -> None:
        """Add a triple to the knowledge graph."""
        try:
            from mempalace.knowledge_graph import KnowledgeGraph

            kg = KnowledgeGraph()
            kg.add_triple(
                subject=subject,
                predicate=predicate,
                obj=obj,
                confidence=confidence,
                source_file=source_file,
            )
            kg.close()
        except (ImportError, Exception):
            pass
