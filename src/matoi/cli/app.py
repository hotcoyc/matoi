"""Main CLI application."""

import typer

from matoi.cli.agents import agents_app
from matoi.cli.team import team_app
from matoi.cli.task import task_app
from matoi.cli.session import session_app
from matoi.cli.memory import memory_app

app = typer.Typer(
    name="matoi",
    help="纏 Matoi — your full startup team in the terminal.",
    no_args_is_help=True,
)

app.add_typer(agents_app, name="roster", help="Browse and inspect available agents.")
app.add_typer(team_app, name="team", help="Compose and manage your team.")
app.add_typer(task_app, name="task", help="Run tasks with your team.")
app.add_typer(session_app, name="session", help="View sessions, artifacts, and costs.")
app.add_typer(memory_app, name="memory", help="Browse and search the knowledge graph.")


@app.command()
def init() -> None:
    """Initialize a new matoi project in the current directory."""
    typer.echo("Initializing matoi project...")


@app.command()
def cost() -> None:
    """Show cost summary for recent sessions."""
    typer.echo("Cost summary not yet implemented.")
