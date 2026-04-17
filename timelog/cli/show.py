import click
from tabulate import tabulate
from timelog import service


def _print_entries(entries: list[dict]) -> None:
    if not entries:
        click.echo("No entries found.")
        return
    click.echo(tabulate(entries, headers="keys", tablefmt="psql"))


@click.group(invoke_without_command=True)
@click.pass_context
def show(ctx: click.Context) -> None:
    """Display timelog entries."""
    if ctx.invoked_subcommand is None:
        _print_entries(service.get_all_entries())


@show.command("today")
def today() -> None:
    """Show today's entries."""
    _print_entries(service.get_entries_today())


@show.command("yesterday")
def yesterday() -> None:
    """Show yesterday's entries."""
    _print_entries(service.get_entries_yesterday())


@show.command("last")
def last() -> None:
    """Show the most recent entry."""
    entry = service.get_last_entry()
    if entry:
        _print_entries([entry])
    else:
        click.echo("No entries found.")


@show.command("projects")
def projects() -> None:
    """List all distinct projects."""
    for p in service.get_distinct_projects():
        click.echo(p)


@show.command("project")
@click.argument("name")
def project(name: str) -> None:
    """Show entries for a specific project."""
    _print_entries(service.get_entries_by_project(name))


@show.command("categories")
def categories() -> None:
    """List all distinct categories."""
    for c in service.get_distinct_categories():
        click.echo(c)


@show.command("category")
@click.argument("name")
def category(name: str) -> None:
    """Show entries for a specific category."""
    _print_entries(service.get_entries_by_category(name))


@show.command("month")
@click.argument("month")
def month(month: str) -> None:
    """Show entries for YYYY-MM."""
    import re
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise click.BadParameter("must be in YYYY-MM format", param_hint="'month'")
    _print_entries(service.get_entries_by_month(month))
