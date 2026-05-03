"""Knowledge graph persistence and LLM-based entity extraction."""

import json
from pathlib import Path
from uuid import uuid4

from rich.console import Console

from matoi.core.memory import Edge, EdgeType, KnowledgeGraph, Node, NodeType
from matoi.gateway.provider import AnthropicProvider
from matoi.gateway.router import MODEL_MAP
from matoi.core.agent import ModelTier

console = Console()

MEMORY_DIR_NAME = "memory"
GRAPH_FILE = "graph.json"

EXTRACTION_PROMPT = """\
You are a knowledge extraction system. Analyze the following artifacts from a team session \
and extract structured knowledge.

Return a JSON object with:
{
  "nodes": [
    {
      "type": "decision|topic|insight|risk|rejected",
      "label": "Short name (max 10 words)",
      "content": "Full description (1-2 sentences)",
      "tags": ["tag1", "tag2"]
    }
  ],
  "edges": [
    {
      "source_label": "label of source node",
      "target_label": "label of target node",
      "type": "related_to|builds_on|contradicts|mitigates",
      "label": "optional edge description"
    }
  ]
}

Rules:
- Extract 3-8 nodes per session (focus on the most important)
- Every decision should be a node
- Key risks should be nodes
- Rejected alternatives should be nodes (type: "rejected")
- Non-obvious insights should be nodes
- Tags should be general topics (e.g. "market-validation", "pricing", "pet-care", "landing-page")
- Edges connect related nodes within this session
- Return ONLY valid JSON, no markdown fences, no explanation
"""


class MemoryStore:
    """Persists and queries the knowledge graph."""

    def __init__(self, project_root: Path) -> None:
        self.memory_dir = project_root / MEMORY_DIR_NAME
        self.memory_dir.mkdir(exist_ok=True)
        self.graph_path = self.memory_dir / GRAPH_FILE
        self.graph = self._load()

    def _load(self) -> KnowledgeGraph:
        if self.graph_path.exists():
            data = json.loads(self.graph_path.read_text())
            return KnowledgeGraph.model_validate(data)
        return KnowledgeGraph()

    def save(self) -> None:
        self.graph_path.write_text(self.graph.model_dump_json(indent=2))

    def extract_and_store(
        self,
        session_id: str,
        artifacts: dict[str, str],
        provider: AnthropicProvider,
    ) -> list[Node]:
        """Extract knowledge from session artifacts using LLM and store in graph."""
        # Combine artifacts into one text
        combined = ""
        for name, content in artifacts.items():
            combined += f"\n\n## {name}\n{content}"

        if not combined.strip():
            return []

        # Use Haiku for extraction (cheap)
        model_id = MODEL_MAP[ModelTier.CHEAP]

        with console.status("[bold]🧠 Extracting knowledge from session...[/bold]"):
            try:
                response_text, _ = provider.call(
                    model_id=model_id,
                    system_prompt=EXTRACTION_PROMPT,
                    user_message=combined[:15000],  # cap context to avoid huge bills
                    max_tokens=2000,
                )
            except Exception as e:
                console.print(f"[yellow]Memory extraction failed: {e}[/yellow]")
                return []

        # Parse LLM response
        try:
            # Strip markdown fences if present
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            data = json.loads(text)
        except (json.JSONDecodeError, IndexError):
            console.print("[yellow]Could not parse memory extraction response.[/yellow]")
            return []

        # Create nodes
        new_nodes: list[Node] = []
        label_to_id: dict[str, str] = {}

        for node_data in data.get("nodes", []):
            node_id = uuid4().hex[:8]
            try:
                node = Node(
                    id=node_id,
                    type=NodeType(node_data["type"]),
                    label=node_data["label"],
                    content=node_data.get("content", ""),
                    session_id=session_id,
                    tags=node_data.get("tags", []),
                )
                self.graph.add_node(node)
                new_nodes.append(node)
                label_to_id[node.label] = node_id
            except (ValueError, KeyError):
                continue

        # Create edges
        for edge_data in data.get("edges", []):
            source_label = edge_data.get("source_label", "")
            target_label = edge_data.get("target_label", "")
            source_id = label_to_id.get(source_label)
            target_id = label_to_id.get(target_label)

            if source_id and target_id:
                try:
                    edge = Edge(
                        source=source_id,
                        target=target_id,
                        type=EdgeType(edge_data.get("type", "related_to")),
                        label=edge_data.get("label", ""),
                        session_id=session_id,
                    )
                    self.graph.add_edge(edge)
                except ValueError:
                    continue

        # Connect to existing graph — find edges to previous nodes by matching tags
        existing_nodes = [n for n in self.graph.nodes.values() if n.session_id != session_id]
        for new_node in new_nodes:
            for existing in existing_nodes:
                shared_tags = set(new_node.tags) & set(existing.tags)
                if shared_tags:
                    self.graph.add_edge(Edge(
                        source=new_node.id,
                        target=existing.id,
                        type=EdgeType.RELATED_TO,
                        label=f"shared: {', '.join(shared_tags)}",
                        session_id=session_id,
                    ))

        self.save()
        return new_nodes

    def get_context(self, task_description: str = "", max_nodes: int = 10) -> str:
        """Get relevant knowledge context for a new pipeline run."""
        if not self.graph.nodes:
            return ""

        # If task description provided, try to find relevant nodes
        if task_description:
            # Simple keyword matching
            words = set(task_description.lower().split())
            scored = []
            for node in self.graph.nodes.values():
                node_words = set(node.label.lower().split()) | set(node.tags)
                overlap = len(words & node_words)
                if overlap > 0:
                    scored.append((overlap, node))
            if scored:
                scored.sort(key=lambda x: x[0], reverse=True)
                relevant = [n for _, n in scored[:max_nodes]]
                lines = ["## Relevant Knowledge from Past Sessions\n"]
                for node in relevant:
                    icon = {"decision": "🎯", "topic": "📌", "insight": "💡", "risk": "⚠️", "rejected": "❌"}.get(node.type.value, "•")
                    lines.append(f"{icon} **{node.label}** ({node.type.value})")
                    lines.append(f"   {node.content[:200]}")
                    lines.append("")
                return "\n".join(lines)

        # Fallback: return recent knowledge
        return self.graph.summary_for_context(max_nodes)
