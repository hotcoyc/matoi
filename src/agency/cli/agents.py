"""CLI commands for browsing and inspecting agents."""

import typer

agents_app = typer.Typer(no_args_is_help=True)


@agents_app.command("list")
def list_agents() -> None:
    """List all available agents in the registry."""
    typer.echo("Agents registry not yet loaded.")


@agents_app.command("show")
def show_agent(name: str = typer.Argument(help="Agent name to inspect.")) -> None:
    """Show detailed info about a specific agent."""
    typer.echo(f"Agent '{name}' details not yet implemented.")
