"""Main entry point for the NOF1 Tracker CLI application."""

import typer

app = typer.Typer(
    name="nof1-tracker",
    help="NOF1 Tracker - Experiment tracking and analysis for N-of-1 trials.",
)


@app.command()
def version() -> None:
    """Display the current version of nof1-tracker."""
    from nof1_tracker import __version__

    typer.echo(f"nof1-tracker version {__version__}")


if __name__ == "__main__":
    app()
