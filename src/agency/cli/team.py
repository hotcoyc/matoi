"""CLI commands for team composition."""

import typer

team_app = typer.Typer(no_args_is_help=True)


@team_app.command("create")
def create_team(name: str = typer.Argument(help="Team name.")) -> None:
    """Create a new team with interactive PM selection."""
    typer.echo(f"Creating team '{name}'...")


@team_app.command("add")
def add_agent(
    team: str = typer.Argument(help="Team name."),
    agent: str = typer.Argument(help="Agent to add."),
) -> None:
    """Add an agent to a team."""
    typer.echo(f"Adding '{agent}' to team '{team}'...")


@team_app.command("remove")
def remove_agent(
    team: str = typer.Argument(help="Team name."),
    agent: str = typer.Argument(help="Agent to remove."),
) -> None:
    """Remove an agent from a team."""
    typer.echo(f"Removing '{agent}' from team '{team}'...")


@team_app.command("recommend")
def recommend(task: str = typer.Argument(help="Task description for recommendation.")) -> None:
    """Ask PM to recommend a team composition for a task."""
    typer.echo("Team recommendation not yet implemented.")
