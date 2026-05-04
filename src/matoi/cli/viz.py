"""CLI commands for project visualization."""

import os
import shutil
import subprocess
import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()
viz_app = typer.Typer(no_args_is_help=True)


def _find_cc_file() -> Path | None:
    """Find the CodeCharta .cc.json.gz file in current directory."""
    cwd = Path.cwd()
    for f in cwd.glob("*.cc.json.gz"):
        return f
    return None


def _java17_env() -> dict:
    """Return env with Java 17 path for CodeCharta."""
    env = os.environ.copy()
    java17 = "/opt/homebrew/opt/openjdk@17/bin"
    if Path(java17).exists():
        env["PATH"] = f"{java17}:{env.get('PATH', '')}"
    return env


@viz_app.command("graph")
def open_graph() -> None:
    """Open the code dependency graph in browser."""
    graph_html = Path.cwd() / ".code-review-graph" / "graph.html"

    if not graph_html.exists():
        console.print("[yellow]Graph not built yet. Building...[/yellow]")
        build_all()
        if not graph_html.exists():
            console.print("[red]Failed to build graph. Install: pip install code-review-graph[/red]")
            raise typer.Exit(1)

    webbrowser.open(f"file://{graph_html.resolve()}")
    console.print(f"[green]✓ Opened dependency graph in browser[/green]")


@viz_app.command("city")
def open_city() -> None:
    """Open the 3D code city visualization."""
    cc_file = _find_cc_file()

    if cc_file is None:
        console.print("[yellow]3D city not built yet. Building...[/yellow]")
        build_all()
        cc_file = _find_cc_file()

    if cc_file is None:
        console.print("[red]Failed to build 3D city. Install: npm i -g codecharta-analysis[/red]")
        raise typer.Exit(1)

    # Open CodeCharta web viewer with instructions
    webbrowser.open("https://codecharta.com/visualization/app/")
    console.print()
    console.print(Panel(
        f"[bold]CodeCharta viewer opened in browser.[/bold]\n\n"
        f"  Drag and drop this file into the viewer:\n"
        f"  [cyan]{cc_file.resolve()}[/cyan]\n\n"
        f"  Or use the 'Load map' button.",
        title="3D Code City",
        border_style="cyan",
    ))


@viz_app.command("build")
def build_all() -> None:
    """Rebuild all visualizations."""
    cwd = Path.cwd()

    console.print()

    # ── code-review-graph ──
    if shutil.which("code-review-graph"):
        with console.status("[bold]Building dependency graph...[/bold]"):
            try:
                result = subprocess.run(
                    ["code-review-graph", "build"],
                    cwd=cwd,
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0:
                    for line in result.stderr.splitlines() + result.stdout.splitlines():
                        if "nodes" in line and "edges" in line:
                            console.print(f"  [green]✓ {line.strip()}[/green]")
                            break
                    else:
                        console.print("  [green]✓ Code graph built[/green]")

                    subprocess.run(
                        ["code-review-graph", "visualize"],
                        cwd=cwd,
                        capture_output=True, text=True, timeout=30,
                    )
                    graph_html = cwd / ".code-review-graph" / "graph.html"
                    if graph_html.exists():
                        console.print(f"  [dim]  → {graph_html}[/dim]")
                else:
                    console.print(f"  [yellow]Graph build failed[/yellow]")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                console.print("  [yellow]Graph build failed[/yellow]")
    else:
        console.print("  [dim]code-review-graph not installed (pip install code-review-graph)[/dim]")

    # ── CodeCharta ──
    if shutil.which("ccsh"):
        with console.status("[bold]Building 3D code city...[/bold]"):
            try:
                output_name = cwd.name or "project"

                # Determine source dir
                src_arg = "src/" if (cwd / "src").is_dir() else "."

                result = subprocess.run(
                    ["ccsh", "unifiedparser", f"-o={output_name}", src_arg],
                    cwd=cwd,
                    capture_output=True, text=True, timeout=120,
                    env=_java17_env(),
                )
                cc_file = cwd / f"{output_name}.cc.json.gz"
                if result.returncode == 0 and cc_file.exists():
                    console.print(f"  [green]✓ 3D city: {cc_file.name}[/green]")
                    console.print(f"  [dim]  → Open with: matoi viz city[/dim]")
                else:
                    console.print(f"  [yellow]CodeCharta build failed[/yellow]")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                console.print("  [yellow]CodeCharta build failed[/yellow]")
    else:
        console.print("  [dim]CodeCharta not installed (npm i -g codecharta-analysis)[/dim]")

    console.print()


@viz_app.command("status")
def viz_status() -> None:
    """Show status of visualizations."""
    cwd = Path.cwd()

    graph_html = cwd / ".code-review-graph" / "graph.html"
    cc_file = _find_cc_file()

    console.print()

    if graph_html.exists():
        stat = graph_html.stat()
        size = f"{stat.st_size / 1024:.0f} KB"
        console.print(f"  [green]✓[/green] Dependency graph: {graph_html.name} ({size})")
        console.print(f"    [dim]matoi viz graph[/dim] — open in browser")
    else:
        console.print(f"  [dim]✗ Dependency graph: not built[/dim]")

    if cc_file:
        stat = cc_file.stat()
        size = f"{stat.st_size / 1024:.0f} KB"
        console.print(f"  [green]✓[/green] 3D code city: {cc_file.name} ({size})")
        console.print(f"    [dim]matoi viz city[/dim] — open in browser")
    else:
        console.print(f"  [dim]✗ 3D code city: not built[/dim]")

    console.print()
    console.print("  [dim]Rebuild: matoi viz build[/dim]")
    console.print()
