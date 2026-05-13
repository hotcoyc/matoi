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
from matoi.cli.viz import viz_app

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
app.add_typer(viz_app, name="viz", help="Project visualizations (graph, 3D city).")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Matoi -- your full startup team in the terminal."""
    if ctx.invoked_subcommand is not None:
        return

    from matoi.cli.session_repl import Session
    session = Session()
    session.start()


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
    console.print(Panel(scan.summary(), title="Project Scan", border_style="cyan"))

    if scan.file_tree:
        console.print(Panel(scan.file_tree, title="[dim]Structure[/dim]", border_style="dim"))

    # ── Step 2b: Build code graph ──
    _build_code_graph(cwd)

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

    TYPE_ICONS = {"coordinator": "[PM]", "executor": "[EXE]", "thinker": "[THK]", "critic": "[CRT]"}

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


def _build_code_graph(cwd: Path) -> None:
    """Build code-review-graph + CodeCharta visualizations."""
    import shutil
    import subprocess

    console.print()
    console.print("[bold]Building project visualizations...[/bold]")

    built_anything = False

    # ── code-review-graph (AI navigation) ──
    if shutil.which("code-review-graph"):
        try:
            result = subprocess.run(
                ["code-review-graph", "build"],
                cwd=cwd,
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                for line in result.stderr.splitlines() + result.stdout.splitlines():
                    if "nodes" in line and "edges" in line:
                        console.print(f"  [green]✓ Code graph: {line.strip()}[/green]")
                        break
                else:
                    console.print("  [green]✓ Code graph built[/green]")

                # HTML visualization
                subprocess.run(
                    ["code-review-graph", "visualize"],
                    cwd=cwd,
                    capture_output=True, text=True, timeout=30,
                )
                graph_html = cwd / ".code-review-graph" / "graph.html"
                if graph_html.exists():
                    console.print(f"  [dim]  → Dependency graph: {graph_html}[/dim]")

                built_anything = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    else:
        console.print("  [dim]code-review-graph not found (pip install code-review-graph)[/dim]")

    # ── CodeCharta (3D city) ──
    if shutil.which("ccsh"):
        try:
            output_name = cwd.name or "project"
            cc_file = cwd / f"{output_name}.cc.json.gz"

            result = subprocess.run(
                ["ccsh", "unifiedparser", f"-o={output_name}", "src/"]
                if (cwd / "src").is_dir()
                else ["ccsh", "unifiedparser", f"-o={output_name}", "."],
                cwd=cwd,
                capture_output=True, text=True, timeout=120,
                env={**__import__("os").environ, "PATH": f"/opt/homebrew/opt/openjdk@17/bin:{__import__('os').environ.get('PATH', '')}"},
            )
            if result.returncode == 0 and cc_file.exists():
                console.print(f"  [green]✓ 3D city: {cc_file}[/green]")
                console.print("  [dim]  → Open at https://codecharta.com/visualization/app/[/dim]")
                built_anything = True
            elif result.returncode != 0:
                # Try without src/ prefix
                pass
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    else:
        console.print("  [dim]CodeCharta not found (npm i -g codecharta-analysis)[/dim]")

    if not built_anything:
        console.print("  [dim]No visualization tools available. Install with:[/dim]")
        console.print("  [dim]  pip install code-review-graph[/dim]")
        console.print("  [dim]  npm i -g codecharta-analysis[/dim]")

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
    """Show cost summary across all sessions."""
    import json

    from matoi.core.config import get_project_dir, load_project_config
    from rich.table import Table

    project_config = load_project_config()
    if project_config is None:
        console.print("[red]Project not initialized. Run 'matoi' first.[/red]")
        raise typer.Exit(1)

    artifacts_dir = get_project_dir() / "artifacts"
    if not artifacts_dir.exists():
        console.print("[dim]No sessions yet.[/dim]")
        raise typer.Exit()

    # Collect all cost.json files
    sessions = []
    for session_dir in sorted(artifacts_dir.iterdir(), reverse=True):
        cost_file = session_dir / "cost.json"
        if cost_file.exists():
            data = json.loads(cost_file.read_text())
            data["session_id"] = session_dir.name
            sessions.append(data)

    if not sessions:
        console.print("[dim]No cost data found.[/dim]")
        raise typer.Exit()

    # Per-session table
    console.print()
    table = Table(title="Cost by Session", border_style="dim", show_lines=False)
    table.add_column("Session", style="dim", min_width=22)
    table.add_column("Calls", justify="right", width=6)
    table.add_column("Tokens", justify="right", width=10)
    table.add_column("Cost", justify="right", style="yellow", width=10)

    grand_total = 0.0
    grand_tokens = 0
    grand_calls = 0

    for s in sessions:
        cost_usd = s.get("total_cost_usd", 0)
        tokens = s.get("total_tokens", 0)
        calls = s.get("total_calls", 0)
        grand_total += cost_usd
        grand_tokens += tokens
        grand_calls += calls

        table.add_row(
            s["session_id"],
            str(calls),
            f"{tokens:,}",
            f"${cost_usd:.4f}",
        )

    table.add_section()
    table.add_row(
        f"[bold]{len(sessions)} sessions[/bold]",
        f"[bold]{grand_calls}[/bold]",
        f"[bold]{grand_tokens:,}[/bold]",
        f"[bold]${grand_total:.4f}[/bold]",
    )

    console.print(table)

    # Per-model breakdown across all sessions
    model_costs: dict[str, dict] = {}
    for s in sessions:
        for row in s.get("breakdown", []):
            model = row.get("model", "unknown")
            if model not in model_costs:
                model_costs[model] = {"calls": 0, "input": 0, "output": 0, "cost": 0.0}
            model_costs[model]["calls"] += 1
            model_costs[model]["input"] += row.get("input_tokens", 0)
            model_costs[model]["output"] += row.get("output_tokens", 0)
            model_costs[model]["cost"] += row.get("cost_usd", 0)

    if model_costs:
        console.print()
        mtable = Table(title="Cost by Model", border_style="dim", show_lines=False)
        mtable.add_column("Model", min_width=28)
        mtable.add_column("Calls", justify="right", width=6)
        mtable.add_column("In tokens", justify="right", width=10)
        mtable.add_column("Out tokens", justify="right", width=10)
        mtable.add_column("Cost", justify="right", style="yellow", width=10)

        for model in sorted(model_costs, key=lambda m: model_costs[m]["cost"], reverse=True):
            mc = model_costs[model]
            model_short = model.replace("claude-", "").replace("-20251001", "")
            mtable.add_row(
                model_short,
                str(mc["calls"]),
                f"{mc['input']:,}",
                f"{mc['output']:,}",
                f"${mc['cost']:.4f}",
            )

        console.print(mtable)

    console.print()


@app.command()
def history(
    session_id: str = typer.Argument(None, help="Session ID to view details. Omit for list."),
) -> None:
    """Browse past sessions and their artifacts."""
    import json

    from matoi.core.config import get_project_dir, load_project_config
    from rich.table import Table
    from rich.markdown import Markdown

    project_config = load_project_config()
    if project_config is None:
        console.print("[red]Project not initialized. Run 'matoi' first.[/red]")
        raise typer.Exit(1)

    artifacts_dir = get_project_dir() / "artifacts"
    if not artifacts_dir.exists():
        console.print("[dim]No sessions yet.[/dim]")
        raise typer.Exit()

    sessions = sorted(artifacts_dir.iterdir(), reverse=True)
    if not sessions:
        console.print("[dim]No sessions yet.[/dim]")
        raise typer.Exit()

    # ── List mode ──
    if session_id is None:
        table = Table(title="Sessions", border_style="dim", show_lines=False)
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Session", style="bold", min_width=24)
        table.add_column("Artifacts", width=10, justify="right")
        table.add_column("Cost", justify="right", style="yellow", width=10)

        for i, sd in enumerate(sessions, 1):
            if not sd.is_dir():
                continue
            files = list(sd.iterdir())
            file_count = len(files)

            cost_str = ""
            cost_file = sd / "cost.json"
            if cost_file.exists():
                try:
                    data = json.loads(cost_file.read_text())
                    cost_str = f"${data.get('total_cost_usd', 0):.4f}"
                except Exception:
                    pass

            table.add_row(str(i), sd.name, str(file_count), cost_str)

        console.print()
        console.print(table)
        console.print(f"\n  [dim]View details: matoi history <session_id>[/dim]\n")
        return

    # ── Detail mode ──
    # Find session by exact ID or prefix
    target = None
    for sd in sessions:
        if sd.name == session_id or sd.name.startswith(session_id):
            target = sd
            break

    if target is None:
        console.print(f"[red]Session '{session_id}' not found.[/red]")
        raise typer.Exit(1)

    console.print(f"\n  [bold]Session: {target.name}[/bold]\n")

    # List artifacts
    files = sorted(target.iterdir())
    for f in files:
        size = f"({f.stat().st_size / 1024:.1f} KB)"
        console.print(f"  {f.name} [dim]{size}[/dim]")

    console.print()

    # Show key artifacts
    for name in ["brief.md", "decision.md", "debate.md"]:
        artifact = target / name
        if artifact.exists():
            content = artifact.read_text()
            console.rule(f"[bold]{name}[/bold]")
            try:
                console.print(Markdown(content))
            except Exception:
                console.print(content)
            console.print()

    # Show cost
    cost_file = target / "cost.json"
    if cost_file.exists():
        try:
            data = json.loads(cost_file.read_text())
            console.rule("[bold]Cost[/bold]")
            breakdown = data.get("breakdown", [])
            if breakdown:
                ctable = Table(border_style="dim", show_lines=False)
                ctable.add_column("Agent", min_width=18)
                ctable.add_column("Stage", width=14)
                ctable.add_column("Tokens", justify="right", width=10)
                ctable.add_column("Cost", justify="right", style="yellow", width=10)
                for row in breakdown:
                    tokens = row.get("input_tokens", 0) + row.get("output_tokens", 0)
                    ctable.add_row(
                        row.get("agent", ""),
                        row.get("stage", ""),
                        f"{tokens:,}",
                        f"${row.get('cost_usd', 0):.4f}",
                    )
                console.print(ctable)
            console.print(f"\n  [bold]Total: ${data.get('total_cost_usd', 0):.4f}[/bold]\n")
        except Exception:
            pass


@app.command()
def demo() -> None:
    """Record a demo GIF of matoi in action (requires VHS)."""
    import shutil
    import subprocess
    from pathlib import Path

    if not shutil.which("vhs"):
        console.print("[red]VHS not installed. Install with: brew install vhs[/red]")
        raise typer.Exit(1)

    # Find demo.tape
    tape_locations = [
        Path.cwd() / "demo.tape",
        Path(__file__).resolve().parent.parent.parent.parent / "demo.tape",
    ]

    tape = None
    for loc in tape_locations:
        if loc.exists():
            tape = loc
            break

    if not tape:
        console.print("[red]demo.tape not found.[/red]")
        raise typer.Exit(1)

    console.print(f"  Recording demo from {tape.name}...")
    console.print("  [dim]This will take ~30 seconds. Don't touch the terminal.[/dim]\n")

    result = subprocess.run(
        ["vhs", str(tape)],
        capture_output=False,
    )

    if result.returncode == 0:
        console.print("\n  [green]Demo recorded: demo.gif[/green]")
    else:
        console.print("\n  [red]Recording failed.[/red]")
