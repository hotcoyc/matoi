"""CLI commands for memory (backed by MemPalace)."""

import subprocess

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
memory_app = typer.Typer(no_args_is_help=True)


@memory_app.command("show")
def show_memory() -> None:
    """Show memory status (powered by MemPalace)."""
    try:
        result = subprocess.run(
            ["mempalace", "status"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print("[dim]MemPalace not initialized. Run 'mempalace init .' first.[/dim]")
    except FileNotFoundError:
        console.print("[red]mempalace not installed. Run 'pip install mempalace'.[/red]")


@memory_app.command("search")
def search_memory(query: str = typer.Argument(help="Search query.")) -> None:
    """Semantic search across memory."""
    try:
        result = subprocess.run(
            ["mempalace", "search", query, "--wing", "matoi"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print(f"[dim]No results for '{query}'.[/dim]")
    except FileNotFoundError:
        console.print("[red]mempalace not installed.[/red]")


@memory_app.command("mine")
def mine_project(
    path: str = typer.Argument(".", help="Directory to index."),
    wing: str = typer.Option("matoi", "--wing", "-w", help="Wing name."),
) -> None:
    """Index files into memory."""
    try:
        result = subprocess.run(
            ["mempalace", "mine", path, "--wing", wing],
            capture_output=False, timeout=120,
        )
    except FileNotFoundError:
        console.print("[red]mempalace not installed.[/red]")


@memory_app.command("wake-up")
def wake_up(
    wing: str = typer.Option("matoi", "--wing", "-w", help="Wing name."),
) -> None:
    """Show wake-up context (Layer 0 + Layer 1)."""
    try:
        result = subprocess.run(
            ["mempalace", "wake-up", "--wing", wing],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            console.print(Panel(result.stdout.strip(), title="🧠 Wake-up Context", border_style="magenta"))
        else:
            console.print("[dim]No wake-up context available.[/dim]")
    except FileNotFoundError:
        console.print("[red]mempalace not installed.[/red]")


@memory_app.command("clear")
def clear_memory(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation."),
) -> None:
    """Clear all memory (removes MemPalace data)."""
    if not force:
        confirm = typer.confirm("This will delete all memory. Continue?")
        if not confirm:
            raise typer.Exit()

    import shutil
    from pathlib import Path

    palace_dir = Path.home() / ".mempalace"
    if palace_dir.exists():
        shutil.rmtree(palace_dir)
        console.print("[dim]MemPalace data cleared.[/dim]")
    else:
        console.print("[dim]No MemPalace data found.[/dim]")
