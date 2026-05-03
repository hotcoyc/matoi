"""CLI commands for sessions, artifacts, and costs."""

import typer

session_app = typer.Typer(no_args_is_help=True)


@session_app.command("list")
def list_sessions() -> None:
    """List recent sessions."""
    typer.echo("No sessions yet.")


@session_app.command("artifacts")
def list_artifacts(
    session_id: str = typer.Argument(None, help="Session ID (latest if omitted)."),
) -> None:
    """List artifacts from a session."""
    typer.echo("No artifacts yet.")
