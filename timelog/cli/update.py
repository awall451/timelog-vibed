import re
import click
from timelog import service


@click.command("tlupdate")
@click.argument("date", required=False)
def update(date: str | None) -> None:
    """Add a new timelog entry interactively."""
    if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise click.BadParameter("must be in YYYY-MM-DD format", param_hint="'date'")

    click.echo("Greetings!\n")

    project = click.prompt("What project did you work on?")
    click.echo()
    category = click.prompt("Category?\nSome options: Timelog, Vulnerability/Security, SCRUM, Product, Automation")
    click.echo()
    description = click.prompt("Give a brief description of the work")
    click.echo()
    hours_str = click.prompt("How many hours?")
    click.echo()

    try:
        hours = float(hours_str)
        if hours <= 0:
            raise ValueError
    except ValueError:
        raise click.ClickException("hours must be a positive number")

    service.add_entry(project, category, description, hours, date)
    click.echo("Entry added.")
