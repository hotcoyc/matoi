"""CLI commands for team composition."""

import json
from pathlib import Path

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from matoi.cli.common import get_project_root, get_registry, load_avatar
from matoi.core.agent import AgentDefinition
from matoi.core.team import TeamConfig

console = Console()
team_app = typer.Typer(no_args_is_help=True)

# Style mapping for PM display
PM_COLORS = {
    "startup-pm": "bold red",
    "delivery-pm": "bold blue",
    "enterprise-pm": "bold yellow",
    "product-strategist-pm": "bold green",
}


@team_app.command("create")
def create_team(name: str = typer.Argument(help="Team name.")) -> None:
    """Create a new team with interactive PM selection."""
    registry = get_registry()
    coordinators = registry.list_by_type("coordinator")

    if not coordinators:
        console.print("[red]No PM agents found in registry.[/red]")
        raise typer.Exit(1)

    # Step 1: Choose PM
    console.print()
    console.print("[bold]Step 1:[/bold] Choose your PM\n")

    _render_pm_gallery(coordinators)

    # Prompt for selection
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
    console.print(f'\n  ✓ Selected: [bold]{selected_pm.name}[/bold] — "{selected_pm.motto}"')

    # Step 2: Add agents
    console.print()
    console.print("[bold]Step 2:[/bold] Add agents to your team (max 4)\n")

    all_agents = [a for a in registry.list_all() if a.slug != selected_pm.slug]

    if not all_agents:
        console.print("[dim]  No other agents available yet.[/dim]")
        team_agents: list[str] = []
    else:
        _render_agent_picker(all_agents)
        team_agents = _pick_agents(all_agents, max_count=4)

    # Step 3: Save team
    team = TeamConfig(
        name=name,
        pm=selected_pm.slug,
        agents=team_agents,
        description=f"Team '{name}' led by {selected_pm.name}",
    )

    teams_dir = get_project_root() / "teams"
    teams_dir.mkdir(exist_ok=True)
    team_file = teams_dir / f"{name}.json"
    team_file.write_text(team.model_dump_json(indent=2))

    # Summary
    console.print()
    _render_team_summary(team, selected_pm)
    console.print(f"\n[dim]  Saved to {team_file}[/dim]\n")


@team_app.command("add")
def add_agent(
    team: str = typer.Argument(help="Team name."),
    agent: str = typer.Argument(help="Agent to add."),
) -> None:
    """Add an agent to a team."""
    team_config = _load_team(team)
    if team_config is None:
        raise typer.Exit(1)

    if len(team_config.agents) >= 4:
        console.print("[red]Team already has maximum 4 agents (+ PM).[/red]")
        raise typer.Exit(1)

    registry = get_registry()
    if registry.get(agent) is None:
        console.print(f"[red]Agent '{agent}' not found in registry.[/red]")
        raise typer.Exit(1)

    if agent in team_config.agents:
        console.print(f"[yellow]Agent '{agent}' is already in team.[/yellow]")
        raise typer.Exit(1)

    team_config.agents.append(agent)
    _save_team(team_config)
    console.print(f"  ✓ Added [bold]{agent}[/bold] to team [bold]{team}[/bold]")


@team_app.command("remove")
def remove_agent(
    team: str = typer.Argument(help="Team name."),
    agent: str = typer.Argument(help="Agent to remove."),
) -> None:
    """Remove an agent from a team."""
    team_config = _load_team(team)
    if team_config is None:
        raise typer.Exit(1)

    if agent not in team_config.agents:
        console.print(f"[red]Agent '{agent}' is not in team '{team}'.[/red]")
        raise typer.Exit(1)

    team_config.agents.remove(agent)
    _save_team(team_config)
    console.print(f"  ✓ Removed [bold]{agent}[/bold] from team [bold]{team}[/bold]")


@team_app.command("list")
def list_teams() -> None:
    """List all saved teams."""
    from matoi.core.config import get_project_dir

    # Check project dir first, then package teams
    teams_dirs = []
    project_dir = get_project_dir()
    if (project_dir / "config.json").exists():
        teams_dirs.append(project_dir.parent)  # project root may have teams/

    teams_dirs.append(get_project_root() / "teams")

    found: list[TeamConfig] = []
    seen: set[str] = set()

    # Project team (from matoi/config.json)
    from matoi.core.config import load_project_config
    pc = load_project_config()
    if pc and pc.team_name:
        found.append(TeamConfig(name=pc.team_name, pm=pc.pm, agents=pc.agents))
        seen.add(pc.team_name)

    # Saved teams from teams/ dirs
    for teams_dir in teams_dirs:
        if not teams_dir.exists():
            continue
        for f in sorted(teams_dir.glob("**/*.json")):
            try:
                tc = TeamConfig.model_validate_json(f.read_text())
                if tc.name not in seen:
                    found.append(tc)
                    seen.add(tc.name)
            except Exception:
                continue

    if not found:
        console.print("[dim]No teams found. Run 'matoi team create' or 'matoi' to create one.[/dim]")
        raise typer.Exit()

    registry = get_registry()

    table = Table(title="Teams", border_style="dim", show_lines=True)
    table.add_column("Name", style="bold", min_width=15)
    table.add_column("PM", min_width=20)
    table.add_column("Agents", min_width=30)
    table.add_column("Size", justify="right", width=5)

    for tc in found:
        pm = registry.get(tc.pm)
        pm_name = pm.name if pm else tc.pm
        agent_names = []
        for slug in tc.agents:
            a = registry.get(slug)
            agent_names.append(a.name if a else slug)

        table.add_row(
            tc.name,
            pm_name,
            ", ".join(agent_names) if agent_names else "[dim]none[/dim]",
            str(tc.agent_count()),
        )

    console.print()
    console.print(table)
    console.print()


@team_app.command("show")
def show_team(name: str = typer.Argument(help="Team name.")) -> None:
    """Show team composition with avatars and agent details."""
    team_config = _load_team(name)
    if team_config is None:
        raise typer.Exit(1)

    registry = get_registry()
    pm = registry.get(team_config.pm)
    if not pm:
        console.print(f"[yellow]PM '{team_config.pm}' not found in registry.[/yellow]")
        raise typer.Exit(1)

    _render_team_full(team_config, pm, registry)


@team_app.command("recommend")
def recommend(task: str = typer.Argument(help="Task description for recommendation.")) -> None:
    """Ask PM to recommend a team composition for a task."""
    console.print("[dim]Team recommendation not yet implemented.[/dim]")


# ── Rendering helpers ──────────────────────────────────────────────────────


def _render_pm_gallery(coordinators: list[AgentDefinition]) -> None:
    """Render PM agents as a gallery with avatars."""
    panels: list[Panel] = []

    for i, pm in enumerate(coordinators):
        color = PM_COLORS.get(pm.slug, "white")
        avatar = load_avatar(pm.slug) or ""

        content_lines = [
            avatar.strip(),
            "",
            f"[bold]{pm.name}[/bold]",
            f'[italic]"{pm.motto}"[/italic]' if pm.motto else "",
            "",
            f"  Risk:   {_risk_bar(pm.risk_tolerance)}",
            f"  Debate: {pm.debate_style}",
            f"  Focus:  {pm.collaboration_preferences[0] if pm.collaboration_preferences else '—'}",
        ]

        panels.append(
            Panel(
                "\n".join(content_lines),
                title=f"[{color}][{i + 1}][/{color}]",
                border_style=color,
                width=38,
                padding=(0, 1),
            )
        )

    console.print(Columns(panels, equal=True, expand=True))


def _render_agent_picker(agents: list[AgentDefinition]) -> None:
    """Render a numbered list of agents for selection."""
    table = Table(border_style="dim", show_lines=False)
    table.add_column("#", style="bold", width=3, justify="right")
    table.add_column("Agent", min_width=20)
    table.add_column("Category", width=20)
    table.add_column("Motto", style="italic dim")

    for i, agent in enumerate(agents, 1):
        table.add_row(str(i), agent.name, agent.category.value, agent.motto or "—")

    console.print(table)


def _pick_agents(agents: list[AgentDefinition], max_count: int = 4) -> list[str]:
    """Interactive agent picker. Returns list of selected slugs."""
    console.print(f"  [dim]Enter agent numbers separated by commas (max {max_count}), or 'skip':[/dim]")
    raw = Prompt.ask("  Agents", default="skip")

    if raw.strip().lower() == "skip":
        return []

    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(agents) and agents[idx].slug not in selected:
                selected.append(agents[idx].slug)
        if len(selected) >= max_count:
            break

    return selected


def _render_team_summary(team: TeamConfig, pm: AgentDefinition) -> None:
    """Render compact team summary panel (used after team create)."""
    color = PM_COLORS.get(pm.slug, "white")

    lines = [
        f"  [bold]Team:[/bold] {team.name}",
        f"  [bold]PM:[/bold]   [{color}]{pm.name}[/{color}] — \"{pm.motto}\"",
        f"  [bold]Size:[/bold] {team.agent_count()} agents",
        "",
    ]

    if team.agents:
        lines.append("  [bold]Members:[/bold]")
        for slug in team.agents:
            lines.append(f"    • {slug}")
    else:
        lines.append("  [dim]No agents added yet. Use 'matoi team add' to add agents.[/dim]")

    console.print(Panel(
        "\n".join(lines),
        title="Team Summary",
        border_style=color,
    ))


def _render_team_full(
    team: TeamConfig, pm: AgentDefinition, registry: "AgentRegistry"
) -> None:
    """Render full team view with PM avatar and agent cards."""
    from matoi.agents.registry import AgentRegistry

    color = PM_COLORS.get(pm.slug, "white")
    avatar = load_avatar(pm.slug) or ""

    # ── PM header with avatar ──
    pm_info = [
        f"[bold]{pm.name}[/bold]",
        f'[italic]"{pm.motto}"[/italic]' if pm.motto else "",
        "",
        f"  Role:     {pm.role}",
        f"  Risk:     {_risk_bar(pm.risk_tolerance)} ({pm.risk_tolerance})",
        f"  Debate:   {pm.debate_style}",
        f"  Model:    brief={_tier_badge(pm.model_policy.brief.value)}"
        f"  debate={_tier_badge(pm.model_policy.debate.value)}"
        f"  synth={_tier_badge(pm.model_policy.synthesis.value)}",
    ]

    if avatar:
        avatar_panel = Panel(
            avatar.strip(),
            border_style=color,
            width=36,
            padding=(0, 1),
        )
        info_panel = Panel(
            "\n".join(pm_info),
            title=f"[{color}]PM[/{color}]",
            border_style=color,
            expand=True,
            padding=(0, 1),
        )
        console.print()
        console.print(Columns([avatar_panel, info_panel], expand=True))
    else:
        console.print()
        console.print(Panel("\n".join(pm_info), title=f"[{color}]PM[/{color}]", border_style=color))

    # ── Team members table ──
    if not team.agents:
        console.print()
        console.print("[dim]  No agents in team. Use 'matoi team add' to add agents.[/dim]")
        console.print()
        return

    TYPE_ICONS = {
        "coordinator": "[PM]",
        "executor": "[EXE]",
        "thinker": "[THK]",
        "critic": "[CRT]",
    }

    CATEGORY_STYLES = {
        "strategy": ("bold yellow", "Strategy"),
        "research": ("bold cyan", "Research"),
        "marketing": ("bold magenta", "Marketing"),
        "design": ("bold green", "Design"),
        "engineering": ("bold blue", "Engineering"),
        "quality": ("bold red", "Quality"),
    }

    table = Table(
        title="Team Members",
        title_style="bold white",
        border_style="dim",
        show_lines=True,
        expand=True,
    )
    table.add_column("Agent", style="bold", min_width=20)
    table.add_column("Type", width=14)
    table.add_column("Category", width=16)
    table.add_column("Risk", width=6, justify="center")
    table.add_column("Debate", width=14)
    table.add_column("Motto", style="italic dim", min_width=20)

    for slug in team.agents:
        agent = registry.get(slug)
        if not agent:
            table.add_row(slug, "?", "?", "?", "?", "[red]not found[/red]")
            continue

        cat_style, cat_label = CATEGORY_STYLES.get(
            agent.category.value, ("white", agent.category.value)
        )
        type_icon = TYPE_ICONS.get(agent.agent_type.value, "")

        table.add_row(
            agent.name,
            f"{type_icon} {agent.agent_type.value}",
            f"[{cat_style}]{cat_label}[/{cat_style}]",
            _risk_bar(agent.risk_tolerance),
            agent.debate_style,
            agent.motto or "—",
        )

    console.print()
    console.print(table)

    # ── Cost estimate ──
    console.print()
    console.print(f"  [dim]Team size: {team.agent_count()} agents (1 PM + {len(team.agents)} members)[/dim]")
    console.print()


def _risk_bar(risk: float) -> str:
    filled = round(risk * 5)
    empty = 5 - filled
    if risk >= 0.7:
        color = "red"
    elif risk >= 0.4:
        color = "yellow"
    else:
        color = "green"
    return f"[{color}]{'█' * filled}{'░' * empty}[/{color}]"


def _tier_badge(tier: str) -> str:
    badges = {
        "cheap": "[green]Haiku[/green]",
        "balanced": "[yellow]Sonnet[/yellow]",
        "premium": "[red bold]Opus[/red bold]",
    }
    return badges.get(tier, tier)


# ── Team file helpers ──────────────────────────────────────────────────────


def _load_team(name: str) -> TeamConfig | None:
    teams_dir = get_project_root() / "teams"
    path = teams_dir / f"{name}.json"
    if not path.exists():
        console.print(f"[red]Team '{name}' not found.[/red]")
        return None
    return TeamConfig.model_validate_json(path.read_text())


def _save_team(team: TeamConfig) -> None:
    teams_dir = get_project_root() / "teams"
    path = teams_dir / f"{team.name}.json"
    path.write_text(team.model_dump_json(indent=2))
