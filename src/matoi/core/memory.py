"""Domain models for knowledge graph memory."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    DECISION = "decision"      # A decision made by the team
    TOPIC = "topic"            # A topic/domain discussed
    INSIGHT = "insight"        # A key insight or finding
    RISK = "risk"              # An identified risk
    REJECTED = "rejected"      # A rejected alternative


class EdgeType(str, Enum):
    RELATED_TO = "related_to"       # General relationship
    BUILDS_ON = "builds_on"         # This decision extends a previous one
    CONTRADICTS = "contradicts"     # This contradicts a previous decision
    MITIGATES = "mitigates"         # This mitigates a risk
    DISCOVERED_IN = "discovered_in" # Found during a specific session


class Node(BaseModel):
    """A node in the knowledge graph."""
    id: str
    type: NodeType
    label: str = Field(description="Short name, e.g. 'Use Carrd for landing pages'")
    content: str = Field(description="Full description")
    session_id: str = Field(description="Session that created this node")
    agent_slug: str = Field("", description="Agent that produced this insight")
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = []


class Edge(BaseModel):
    """A directed edge between two nodes."""
    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    type: EdgeType
    label: str = Field("", description="Optional edge label")
    session_id: str = ""


class KnowledgeGraph(BaseModel):
    """The full knowledge graph."""
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def find_by_type(self, node_type: NodeType) -> list[Node]:
        return [n for n in self.nodes.values() if n.type == node_type]

    def find_by_tag(self, tag: str) -> list[Node]:
        return [n for n in self.nodes.values() if tag in n.tags]

    def find_related(self, node_id: str) -> list[Node]:
        """Find all nodes connected to a given node."""
        related_ids = set()
        for edge in self.edges:
            if edge.source == node_id:
                related_ids.add(edge.target)
            if edge.target == node_id:
                related_ids.add(edge.source)
        return [self.nodes[nid] for nid in related_ids if nid in self.nodes]

    def search(self, query: str) -> list[Node]:
        """Simple text search across node labels and content."""
        query_lower = query.lower()
        results = []
        for node in self.nodes.values():
            if query_lower in node.label.lower() or query_lower in node.content.lower():
                results.append(node)
        return results

    def summary_for_context(self, max_nodes: int = 10) -> str:
        """Generate a text summary of recent knowledge for pipeline context."""
        if not self.nodes:
            return ""

        # Get most recent nodes
        recent = sorted(
            self.nodes.values(),
            key=lambda n: n.created_at,
            reverse=True,
        )[:max_nodes]

        lines = ["## Previous Knowledge (from past sessions)\n"]
        for node in recent:
            icon = {"decision": "[>]", "topic": "[~]", "insight": "[*]", "risk": "[!]", "rejected": "[-]"}.get(node.type.value, "[.]")
            lines.append(f"{icon} **{node.label}** ({node.type.value})")
            lines.append(f"   {node.content[:200]}")
            if node.tags:
                lines.append(f"   Tags: {', '.join(node.tags)}")
            lines.append("")

        return "\n".join(lines)
