"""CLI commands for browsing and inspecting agents."""

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from matoi.cli.common import get_registry, load_avatar
from matoi.core.agent import AgentDefinition

console = Console()
agents_app = typer.Typer(no_args_is_help=True)

# Category display config
CATEGORY_STYLES = {
    "strategy": ("bold yellow", "Strategy & Business"),
    "research": ("bold cyan", "Research"),
    "marketing": ("bold magenta", "Marketing & Growth"),
    "design": ("bold green", "Design & Product"),
    "engineering": ("bold blue", "Engineering"),
    "quality": ("bold red", "Quality & Ops"),
}

TYPE_ICONS = {
    "coordinator": "👔",
    "executor": "⚙️",
    "thinker": "🧠",
    "critic": "🔍",
}


@agents_app.command("list")
def list_agents(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category."),
    agent_type: str = typer.Option(None, "--type", "-t", help="Filter by type."),
) -> None:
    """List all available agents in the registry."""
    registry = get_registry()

    if category:
        agents = registry.list_by_category(category)
    elif agent_type:
        agents = registry.list_by_type(agent_type)
    else:
        agents = registry.list_all()

    if not agents:
        console.print("[dim]No agents found.[/dim]")
        raise typer.Exit()

    table = Table(
        title="🏢 Agent Registry",
        title_style="bold white",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Agent", style="bold", min_width=20)
    table.add_column("Type", width=14)
    table.add_column("Category", width=20)
    table.add_column("Risk", width=6, justify="center")
    table.add_column("Motto", style="italic dim", min_width=25)

    for i, agent in enumerate(sorted(agents, key=lambda a: (a.category.value, a.name)), 1):
        cat_style, cat_label = CATEGORY_STYLES.get(
            agent.category.value, ("white", agent.category.value)
        )
        type_icon = TYPE_ICONS.get(agent.agent_type.value, "")

        risk_bar = _risk_bar(agent.risk_tolerance)

        table.add_row(
            str(i),
            agent.name,
            f"{type_icon} {agent.agent_type.value}",
            f"[{cat_style}]{cat_label}[/{cat_style}]",
            risk_bar,
            agent.motto or "—",
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]{len(agents)} agents loaded[/dim]")


@agents_app.command("show")
def show_agent(name: str = typer.Argument(help="Agent slug (e.g. 'startup-pm').")) -> None:
    """Show detailed info about a specific agent."""
    registry = get_registry()
    agent = registry.get(name)

    if agent is None:
        console.print(f"[red]Agent '{name}' not found.[/red]")
        console.print("[dim]Use 'matoi roster list' to see available agents.[/dim]")
        raise typer.Exit(1)

    _render_agent_card(agent)


def _render_agent_card(agent: AgentDefinition) -> None:
    """Render a full agent card with avatar and details."""
    cat_style, cat_label = CATEGORY_STYLES.get(
        agent.category.value, ("white", agent.category.value)
    )
    type_icon = TYPE_ICONS.get(agent.agent_type.value, "")

    # Avatar
    avatar_text = load_avatar(agent.slug)

    # Build info panel
    info_lines: list[str] = []
    info_lines.append(f"[bold]{agent.name}[/bold]")
    info_lines.append(f'[italic]"{agent.motto}"[/italic]' if agent.motto else "")
    info_lines.append("")
    info_lines.append(f"  Role:     {agent.role}")
    info_lines.append(f"  Type:     {type_icon} {agent.agent_type.value}")
    info_lines.append(f"  Category: [{cat_style}]{cat_label}[/{cat_style}]")
    info_lines.append(f"  Risk:     {_risk_bar(agent.risk_tolerance)} ({agent.risk_tolerance})")
    info_lines.append(f"  Debate:   {agent.debate_style}")
    info_lines.append("")

    # Model policy
    policy = agent.model_policy
    info_lines.append("[bold]Model Policy[/bold]")
    info_lines.append(f"  Brief:       {_tier_badge(policy.brief.value)}")
    info_lines.append(f"  Expert pass: {_tier_badge(policy.expert_pass.value)}")
    info_lines.append(f"  Debate:      {_tier_badge(policy.debate.value)}")
    info_lines.append(f"  Synthesis:   {_tier_badge(policy.synthesis.value)}")

    info_content = "\n".join(info_lines)

    # Compose layout: avatar left, info right
    if avatar_text:
        avatar_panel = Panel(
            avatar_text.strip(),
            border_style=cat_style,
            width=36,
            padding=(0, 1),
        )
        info_panel = Panel(
            info_content,
            border_style=cat_style,
            expand=True,
            padding=(0, 1),
        )
        console.print()
        console.print(Columns([avatar_panel, info_panel], expand=True))
    else:
        console.print()
        console.print(Panel(info_content, border_style=cat_style, title=agent.name))

    # Strengths & Weaknesses
    if agent.strengths or agent.weaknesses:
        sw_table = Table(show_header=True, border_style="dim", expand=True)
        sw_table.add_column("✅ Strengths", style="green")
        sw_table.add_column("⚠️  Weaknesses", style="yellow")

        max_len = max(len(agent.strengths), len(agent.weaknesses))
        for i in range(max_len):
            s = agent.strengths[i] if i < len(agent.strengths) else ""
            w = agent.weaknesses[i] if i < len(agent.weaknesses) else ""
            sw_table.add_row(s, w)

        console.print(sw_table)

    # Responsibilities
    if agent.responsibilities:
        console.print()
        console.print("[bold]Responsibilities[/bold]")
        for r in agent.responsibilities:
            console.print(f"  • {r}")

    # Collaboration preferences
    if agent.collaboration_preferences:
        console.print()
        console.print("[bold]Collaboration[/bold]")
        for c in agent.collaboration_preferences:
            console.print(f"  • {c}")

    console.print()


def _risk_bar(risk: float) -> str:
    """Render a risk tolerance bar like ███░░."""
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
    """Render a colored model tier badge."""
    badges = {
        "cheap": "[green]Haiku[/green]",
        "balanced": "[yellow]Sonnet[/yellow]",
        "premium": "[red bold]Opus[/red bold]",
    }
    return badges.get(tier, tier)
