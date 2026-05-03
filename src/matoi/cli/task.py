"""CLI commands for running tasks."""

import os
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from matoi.cli.common import get_project_root, get_registry
from matoi.core.team import TeamConfig

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


def _load_team(name: str) -> TeamConfig:
    """Load a team config or exit."""
    teams_dir = get_project_root() / "teams"
    path = teams_dir / f"{name}.json"
    if not path.exists():
        console.print(f"[red]Team '{name}' not found.[/red]")
        console.print("[dim]Use 'matoi team create' to create a team first.[/dim]")
        raise typer.Exit(1)
    return TeamConfig.model_validate_json(path.read_text())


@task_app.command("run")
def run_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option(..., "--team", "-t", help="Team to use."),
    budget: float = typer.Option(5.0, "--budget", "-b", help="Max budget in USD."),
) -> None:
    """Run a task with the full orchestration pipeline."""
    _require_api_key()

    from matoi.core.cost import Budget
    from matoi.gateway.provider import AnthropicProvider
    from matoi.gateway.router import ModelRouter
    from matoi.orchestrator.pipeline import MVPPipeline

    team_config = _load_team(team)
    registry = get_registry()
    provider = AnthropicProvider()
    router = ModelRouter()
    output_dir = get_project_root() / "artifacts"

    pipeline = MVPPipeline(
        team=team_config,
        registry=registry,
        provider=provider,
        router=router,
        output_dir=output_dir,
        budget=Budget(max_total_usd=budget),
    )

    pipeline.run(task)


@task_app.command("plan")
def plan_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option(..., "--team", "-t", help="Team to use."),
) -> None:
    """Show what the pipeline would do (dry run, no API calls)."""
    team_config = _load_team(team)
    registry = get_registry()

    pm = registry.get(team_config.pm)
    pm_name = pm.name if pm else team_config.pm

    console.print()
    console.print(Panel(f"[bold]{task}[/bold]", title="纏 Task (dry run)", border_style="yellow"))
    console.print()

    table = Table(title="Pipeline Plan", border_style="dim")
    table.add_column("Stage", style="bold")
    table.add_column("Agent")
    table.add_column("Model")

    from matoi.gateway.router import ModelRouter
    router = ModelRouter()

    if pm:
        brief_model = router.resolve_model(pm, "brief")
        synth_model = router.resolve_model(pm, "synthesis")
        table.add_row("1. Brief", pm_name, brief_model)
    else:
        table.add_row("1. Brief", pm_name, "?")

    for slug in team_config.agents:
        agent = registry.get(slug)
        if agent:
            model = router.resolve_model(agent, "expert_pass")
            table.add_row("2. Expert Pass", agent.name, model)
        else:
            table.add_row("2. Expert Pass", slug, "?")

    if pm:
        table.add_row("3. Synthesis", pm_name, synth_model)

    console.print(table)
    console.print(f"\n[dim]Total API calls: {2 + len(team_config.agents)} (1 brief + {len(team_config.agents)} opinions + 1 synthesis)[/dim]\n")
