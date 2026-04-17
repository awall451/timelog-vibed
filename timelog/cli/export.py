import click
from datetime import date
from timelog import service


@click.command("tlexport")
def export() -> None:
    """Export all entries to a dated CSV file."""
    filename = f"timelog-{date.today()}.csv"
    click.echo(f"Exporting entries to {filename}...")
    service.export_to_csv(filename)
    click.echo(f"Export complete: {filename}")
