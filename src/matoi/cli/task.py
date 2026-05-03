"""CLI commands for running tasks."""

import os

import typer
from dotenv import load_dotenv
from rich.console import Console

console = Console()
task_app = typer.Typer(no_args_is_help=True)


def _require_api_key() -> str:
    """Load .env and return API key, or exit with a helpful error."""
    load_dotenv()
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        console.print()
        console.print("[red bold]ANTHROPIC_API_KEY not set.[/red bold]")
        console.print()
        console.print("  To fix this, add your key to [bold].env[/bold] file:")
        console.print()
        console.print("    [dim]echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env[/dim]")
        console.print()
        console.print("  Get your key at: [link]https://console.anthropic.com/settings/keys[/link]")
        console.print()
        raise typer.Exit(1)
    return key


@task_app.command("run")
def run_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option("default", "--team", "-t", help="Team to use."),
) -> None:
    """Run a task with the full orchestration pipeline."""
    _require_api_key()
    console.print(f"[dim]Running task with team '{team}': {task}[/dim]")
    console.print("[yellow]Pipeline not yet implemented.[/yellow]")


@task_app.command("plan")
def plan_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option("default", "--team", "-t", help="Team to use."),
) -> None:
    """Plan a task without executing (dry run)."""
    _require_api_key()
    console.print(f"[dim]Planning task with team '{team}': {task}[/dim]")
    console.print("[yellow]Planning not yet implemented.[/yellow]")
