import click
from timelog import service


@click.command("tlimport")
@click.argument("filepath", type=click.Path(exists=True, readable=True))
def import_cmd(filepath: str) -> None:
    """Replace the database with entries from a CSV file."""
    click.echo(f"Importing from {filepath}...")
    try:
        count = service.import_from_csv(filepath)
    except ValueError as e:
        raise click.ClickException(str(e))
    click.echo(f"Imported {count} entries.")
