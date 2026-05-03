"""CLI commands for knowledge graph memory."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from matoi.cli.common import get_project_root
from matoi.storage.memory import MemoryStore

console = Console()
memory_app = typer.Typer(no_args_is_help=True)

NODE_ICONS = {
    "decision": "🎯",
    "topic": "📌",
    "insight": "💡",
    "risk": "⚠️",
    "rejected": "❌",
}

NODE_COLORS = {
    "decision": "green",
    "topic": "cyan",
    "insight": "yellow",
    "risk": "red",
    "rejected": "dim",
}


@memory_app.command("show")
def show_graph() -> None:
    """Show the knowledge graph overview."""
    memory = MemoryStore(get_project_root())
    graph = memory.graph

    if not graph.nodes:
        console.print("[dim]Knowledge graph is empty. Run 'matoi task run' to populate it.[/dim]")
        raise typer.Exit()

    # Stats
    type_counts = {}
    for node in graph.nodes.values():
        type_counts[node.type.value] = type_counts.get(node.type.value, 0) + 1

    sessions = set(n.session_id for n in graph.nodes.values())

    stats = (
        f"  Nodes: {len(graph.nodes)}  |  "
        f"Edges: {len(graph.edges)}  |  "
        f"Sessions: {len(sessions)}"
    )
    console.print()
    console.print(Panel(stats, title="🧠 Knowledge Graph", border_style="magenta"))

    # Type breakdown
    for ntype, count in sorted(type_counts.items()):
        icon = NODE_ICONS.get(ntype, "•")
        console.print(f"  {icon} {ntype}: {count}")

    # All nodes as table
    console.print()
    table = Table(title="Nodes", border_style="dim", show_lines=True)
    table.add_column("Type", width=10)
    table.add_column("Label", min_width=25)
    table.add_column("Tags", style="dim", width=25)
    table.add_column("Session", style="dim", width=18)

    for node in sorted(graph.nodes.values(), key=lambda n: n.created_at, reverse=True):
        icon = NODE_ICONS.get(node.type.value, "•")
        color = NODE_COLORS.get(node.type.value, "white")
        table.add_row(
            f"{icon} {node.type.value}",
            f"[{color}]{node.label}[/{color}]",
            ", ".join(node.tags[:3]),
            node.session_id[:15],
        )

    console.print(table)
    console.print()


@memory_app.command("search")
def search_graph(query: str = typer.Argument(help="Search query.")) -> None:
    """Search the knowledge graph."""
    memory = MemoryStore(get_project_root())
    results = memory.graph.search(query)

    if not results:
        console.print(f"[dim]No results for '{query}'.[/dim]")
        raise typer.Exit()

    console.print(f"\n[bold]Found {len(results)} results for '{query}':[/bold]\n")
    for node in results:
        icon = NODE_ICONS.get(node.type.value, "•")
        color = NODE_COLORS.get(node.type.value, "white")
        console.print(f"  {icon} [{color}]{node.label}[/{color}]")
        console.print(f"     {node.content[:150]}")
        if node.tags:
            console.print(f"     [dim]Tags: {', '.join(node.tags)}[/dim]")
        console.print()


@memory_app.command("clear")
def clear_graph(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation."),
) -> None:
    """Clear the knowledge graph."""
    if not force:
        confirm = typer.confirm("This will delete all memory. Continue?")
        if not confirm:
            raise typer.Exit()

    memory = MemoryStore(get_project_root())
    memory.graph_path.unlink(missing_ok=True)
    console.print("[dim]Knowledge graph cleared.[/dim]")
