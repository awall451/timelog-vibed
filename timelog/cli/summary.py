import re
import click
from tabulate import tabulate
from timelog import service


def _print_total(hours: float) -> None:
    click.echo(f"Total hours: {hours:.2f}")


def _validate_month(month: str) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise click.BadParameter("must be in YYYY-MM format", param_hint="'month'")


@click.group(invoke_without_command=True)
@click.pass_context
def summary(ctx: click.Context) -> None:
    """Display total hours."""
    if ctx.invoked_subcommand is None:
        _print_total(service.sum_all())


@summary.command("today")
def today() -> None:
    """Total hours for today."""
    _print_total(service.sum_today())


@summary.command("yesterday")
def yesterday() -> None:
    """Total hours for yesterday."""
    _print_total(service.sum_yesterday())


@summary.command("month")
@click.argument("month")
def month(month: str) -> None:
    """Total hours for YYYY-MM."""
    _validate_month(month)
    _print_total(service.sum_by_month(month))


@summary.command("projects")
@click.argument("month", required=False)
def projects(month: str | None) -> None:
    """Total hours per project, optionally filtered to YYYY-MM."""
    if month:
        _validate_month(month)
    rows = service.sum_per_project(month)
    if not rows:
        click.echo("No entries found.")
        return
    click.echo(tabulate(rows, headers={"project": "Project", "hours": "Hours"}, tablefmt="psql"))


@summary.command("project")
@click.argument("name")
def project(name: str) -> None:
    """Total hours for a specific project."""
    _print_total(service.sum_by_project(name))


@summary.command("categories")
@click.argument("month", required=False)
def categories(month: str | None) -> None:
    """Total hours per category, optionally filtered to YYYY-MM."""
    if month:
        _validate_month(month)
    rows = service.sum_per_category(month)
    if not rows:
        click.echo("No entries found.")
        return
    click.echo(tabulate(rows, headers={"category": "Category", "hours": "Hours"}, tablefmt="psql"))


@summary.command("category")
@click.argument("name")
def category(name: str) -> None:
    """Total hours for a specific category."""
    _print_total(service.sum_by_category(name))
