"""Main CLI application."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from matoi.cli.agents import agents_app
from matoi.cli.team import team_app
from matoi.cli.task import task_app
from matoi.cli.session import session_app
from matoi.cli.memory import memory_app

console = Console()

app = typer.Typer(
    name="matoi",
    help="纏 Matoi — your full startup team in the terminal.",
    invoke_without_command=True,
)

app.add_typer(agents_app, name="roster", help="Browse and inspect available agents.")
app.add_typer(team_app, name="team", help="Compose and manage your team.")
app.add_typer(task_app, name="task", help="Run tasks with your team.")
app.add_typer(session_app, name="session", help="View sessions, artifacts, and costs.")
app.add_typer(memory_app, name="memory", help="Browse and search the knowledge graph.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """纏 Matoi — your full startup team in the terminal."""
    if ctx.invoked_subcommand is not None:
        return

    # No subcommand → interactive onboarding or status
    from matoi.core.config import load_project_config

    project_config = load_project_config()

    if project_config is None:
        _onboarding()
    else:
        _status(project_config)


def _onboarding() -> None:
    """First-time setup: API key → scan → team assembly."""
    from matoi.core.config import (
        GlobalConfig,
        ProjectConfig,
        ensure_project_structure,
        load_global_config,
        save_global_config,
        save_project_config,
    )
    from matoi.core.scanner import scan_project
    from matoi.cli.common import get_registry, load_avatar

    console.print()
    console.print(Panel(
        "[bold]纏 Welcome to Matoi![/bold]\n\n"
        "Your full startup team in the terminal.\n"
        "Let's set up your project.",
        border_style="bold white",
    ))
    console.print()

    # ── Step 1: API Key ──
    global_config = load_global_config()
    if not global_config.anthropic_api_key:
        console.print("[bold]Step 1:[/bold] Connect your Anthropic API key\n")
        console.print("  Get your key at: https://console.anthropic.com/settings/keys\n")
        key = Prompt.ask("  API Key", password=True)
        if not key.strip():
            console.print("[red]API key is required.[/red]")
            raise typer.Exit(1)
        global_config.anthropic_api_key = key.strip()
        save_global_config(global_config)
        console.print("  [green]✓ API key saved to ~/.matoi/config.json[/green]\n")
    else:
        console.print("[dim]  ✓ API key found[/dim]\n")

    # ── Step 2: Scan Project ──
    console.print("[bold]Step 2:[/bold] Scanning your project...\n")
    cwd = Path.cwd()
    scan = scan_project(cwd)
    console.print(Panel(scan.summary(), title="📁 Project Scan", border_style="cyan"))

    if scan.file_tree:
        console.print(Panel(scan.file_tree, title="[dim]Structure[/dim]", border_style="dim"))

    # ── Step 3: Assemble Team ──
    console.print()
    console.print("[bold]Step 3:[/bold] Assemble your team\n")

    registry = get_registry()
    coordinators = registry.list_by_type("coordinator")

    if not coordinators:
        console.print("[red]No PM agents found in registry.[/red]")
        raise typer.Exit(1)

    # Import PM gallery renderer from team module
    from matoi.cli.team import _render_pm_gallery, _pick_agents, PM_COLORS

    _render_pm_gallery(coordinators)

    slugs = [c.slug for c in coordinators]
    choices_display = ", ".join(
        f"[bold]{i + 1}[/bold]={c.slug}" for i, c in enumerate(coordinators)
    )
    console.print(f"\n  {choices_display}")

    choice = Prompt.ask(
        "\n  Select PM",
        choices=[str(i + 1) for i in range(len(coordinators))],
    )
    selected_pm = coordinators[int(choice) - 1]
    color = PM_COLORS.get(selected_pm.slug, "white")
    console.print(f'\n  ✓ Selected: [{color}]{selected_pm.name}[/{color}] — "{selected_pm.motto}"')

    # Select agents
    console.print()
    console.print("[bold]Add agents to your team (max 4):[/bold]\n")

    all_agents = [a for a in registry.list_all() if a.slug != selected_pm.slug]

    from rich.table import Table
    table = Table(border_style="dim", show_lines=False)
    table.add_column("#", style="bold", width=3, justify="right")
    table.add_column("Agent", min_width=20)
    table.add_column("Type", width=14)
    table.add_column("Category", width=16)
    table.add_column("Motto", style="italic dim")

    TYPE_ICONS = {"coordinator": "👔", "executor": "⚙️", "thinker": "🧠", "critic": "🔍"}

    for i, agent in enumerate(all_agents, 1):
        icon = TYPE_ICONS.get(agent.agent_type.value, "")
        table.add_row(str(i), agent.name, f"{icon} {agent.agent_type.value}", agent.category.value, agent.motto or "—")

    console.print(table)

    selected_agents = _pick_agents(all_agents, max_count=4)

    # ── Save project config ──
    project_config = ProjectConfig(
        team_name=scan.name,
        pm=selected_pm.slug,
        agents=selected_agents,
        project_name=scan.name,
        project_description=scan.summary(),
    )

    project_dir = ensure_project_structure()
    save_project_config(project_config)

    # Summary
    console.print()
    agent_names = []
    for slug in selected_agents:
        a = registry.get(slug)
        agent_names.append(a.name if a else slug)

    summary_lines = [
        f"  [bold]Project:[/bold] {scan.name}",
        f"  [bold]PM:[/bold] [{color}]{selected_pm.name}[/{color}]",
        f"  [bold]Team:[/bold] {', '.join(agent_names) if agent_names else 'none yet'}",
        f"  [bold]Matoi dir:[/bold] {project_dir}",
    ]
    console.print(Panel(
        "\n".join(summary_lines),
        title="[bold]纏 Project Ready![/bold]",
        border_style="green",
    ))

    console.print()
    console.print("  Now you can run:")
    console.print(f'  [bold]matoi run "your task description"[/bold]')
    console.print()


def _status(project_config: "ProjectConfig") -> None:
    """Show current project status when matoi is already initialized."""
    from matoi.core.config import get_project_dir, ProjectConfig
    from matoi.cli.common import get_registry

    registry = get_registry()
    pm = registry.get(project_config.pm)
    pm_name = pm.name if pm else project_config.pm

    from matoi.cli.team import PM_COLORS
    color = PM_COLORS.get(project_config.pm, "white")

    agent_names = []
    for slug in project_config.agents:
        a = registry.get(slug)
        agent_names.append(a.name if a else slug)

    # Check memory (MemPalace)
    project_dir = get_project_dir()
    memory_info = ""
    try:
        from matoi.storage.memory import MemoryStore
        mem = MemoryStore(project_dir)
        status = mem.status()
        drawer_count = status.get("drawers", 0) if isinstance(status, dict) else 0
        if drawer_count:
            memory_info = f"\n  [bold]Memory:[/bold] {drawer_count} drawers in MemPalace"
    except Exception:
        pass

    # Count artifacts
    artifacts_dir = project_dir / "artifacts"
    session_count = len(list(artifacts_dir.iterdir())) if artifacts_dir.exists() else 0

    lines = [
        f"  [bold]Project:[/bold] {project_config.project_name}",
        f"  [bold]PM:[/bold] [{color}]{pm_name}[/{color}]",
        f"  [bold]Team:[/bold] {', '.join(agent_names) if agent_names else 'none'}",
        f"  [bold]Sessions:[/bold] {session_count}",
    ]
    if memory_info:
        lines.append(memory_info)

    console.print()
    console.print(Panel(
        "\n".join(lines),
        title="纏 Matoi",
        border_style="white",
    ))
    console.print()
    console.print("  Commands:")
    console.print('  [bold]matoi run "task"[/bold]         — run task with your team')
    console.print("  [bold]matoi roster list[/bold]        — browse agents")
    console.print("  [bold]matoi team show[/bold]          — show your team")
    console.print("  [bold]matoi memory show[/bold]        — browse knowledge graph")
    console.print()


@app.command()
def run(
    task: str = typer.Argument(help="Task description."),
    budget: float = typer.Option(5.0, "--budget", "-b", help="Max budget in USD."),
) -> None:
    """Run a task with your project team."""
    from matoi.core.config import load_project_config, require_api_key, get_project_dir
    from matoi.cli.common import get_registry

    api_key = require_api_key()
    if not api_key:
        console.print("[red]Run 'matoi' first to set up your API key.[/red]")
        raise typer.Exit(1)

    project_config = load_project_config()
    if project_config is None:
        console.print("[red]Project not initialized. Run 'matoi' first.[/red]")
        raise typer.Exit(1)

    from matoi.core.cost import Budget
    from matoi.core.team import TeamConfig
    from matoi.gateway.provider import AnthropicProvider
    from matoi.gateway.router import ModelRouter
    from matoi.orchestrator.pipeline import MVPPipeline
    from matoi.storage.memory import MemoryStore

    team_config = TeamConfig(
        name=project_config.team_name,
        pm=project_config.pm,
        agents=project_config.agents,
    )
    registry = get_registry()
    provider = AnthropicProvider()
    router = ModelRouter()
    project_dir = get_project_dir()
    memory = MemoryStore(project_dir)

    pipeline = MVPPipeline(
        team=team_config,
        registry=registry,
        provider=provider,
        router=router,
        output_dir=project_dir / "artifacts",
        memory=memory,
        budget=Budget(max_total_usd=budget),
    )

    pipeline.run(task)


@app.command()
def cost() -> None:
    """Show cost summary for recent sessions."""
    console.print("[dim]Cost summary not yet implemented.[/dim]")
