"""Main CLI application."""

import typer

from agency.cli.agents import agents_app
from agency.cli.team import team_app
from agency.cli.task import task_app
from agency.cli.session import session_app

app = typer.Typer(
    name="agency",
    help="AI Agency Platform — your full startup team in the terminal.",
    no_args_is_help=True,
)

app.add_typer(agents_app, name="agents", help="Browse and inspect available agents.")
app.add_typer(team_app, name="team", help="Compose and manage your team.")
app.add_typer(task_app, name="task", help="Run tasks with your team.")
app.add_typer(session_app, name="session", help="View sessions, artifacts, and costs.")


@app.command()
def init() -> None:
    """Initialize a new agency project in the current directory."""
    typer.echo("Initializing agency project...")


@app.command()
def cost() -> None:
    """Show cost summary for recent sessions."""
    typer.echo("Cost summary not yet implemented.")
