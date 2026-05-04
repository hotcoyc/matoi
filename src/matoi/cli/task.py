"""CLI commands for task utilities (plan, dry-run)."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from matoi.cli.common import get_project_root, get_registry
from matoi.core.team import TeamConfig

console = Console()
task_app = typer.Typer(no_args_is_help=True)


def _load_team(name: str) -> TeamConfig:
    """Load a team config or exit."""
    teams_dir = get_project_root() / "teams"
    path = teams_dir / f"{name}.json"
    if not path.exists():
        console.print(f"[red]Team '{name}' not found.[/red]")
        raise typer.Exit(1)
    return TeamConfig.model_validate_json(path.read_text())


@task_app.command("plan")
def plan_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option("demo", "--team", "-t", help="Team to use."),
) -> None:
    """Show what the pipeline would do (dry run, no API calls)."""
    team_config = _load_team(team)
    registry = get_registry()

    pm = registry.get(team_config.pm)
    pm_name = pm.name if pm else team_config.pm

    console.print()
    console.print(Panel(f"[bold]{task}[/bold]", title="Task (dry run)", border_style="yellow"))
    console.print()

    from matoi.gateway.router import ModelRouter
    router = ModelRouter()

    table = Table(title="Pipeline Plan", border_style="dim")
    table.add_column("Stage", style="bold")
    table.add_column("Agent")
    table.add_column("Model")

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

    table.add_row("3. Conflict Detect", "(auto)", "haiku-4-5")

    table.add_row("4. Debate", "(if conflicts)", "per agent policy")

    if pm:
        table.add_row("5. Synthesis", pm_name, synth_model)

    console.print(table)

    total_calls = 2 + len(team_config.agents)  # brief + experts + synthesis
    console.print(
        f"\n  [dim]Min API calls: {total_calls} "
        f"(1 brief + {len(team_config.agents)} opinions + 1 synthesis)"
        f"\n  + conflict detection + debate rounds if conflicts found[/dim]\n"
    )
