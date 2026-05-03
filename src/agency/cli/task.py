"""CLI commands for running tasks."""

import typer

task_app = typer.Typer(no_args_is_help=True)


@task_app.command("run")
def run_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option("default", "--team", "-t", help="Team to use."),
) -> None:
    """Run a task with the full orchestration pipeline."""
    typer.echo(f"Running task with team '{team}': {task}")


@task_app.command("plan")
def plan_task(
    task: str = typer.Argument(help="Task description."),
    team: str = typer.Option("default", "--team", "-t", help="Team to use."),
) -> None:
    """Plan a task without executing (dry run)."""
    typer.echo(f"Planning task with team '{team}': {task}")
