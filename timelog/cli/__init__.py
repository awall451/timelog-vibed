import click


@click.command("tlhelp")
def help_cmd():
    """Show all available commands and usage."""
    click.echo("""cli-timelog
Track work entries in a local SQLite timelog database.

USAGE
  tlhelp
  tlshow  [subcommand]
  tlsum   [subcommand] [YYYY-MM]
  tlupdate [YYYY-MM-DD]
  tlexport

COMMANDS
  tlshow      Display entries
                (none)               All entries
                today                Today's entries
                yesterday            Yesterday's entries
                last                 Most recent entry
                month <YYYY-MM>      Entries for a specific month
                projects             All distinct projects
                project <name>       Entries for a specific project
                categories           All distinct categories
                category <name>      Entries for a specific category

  tlsum       Display total hours
                (none)               All-time total
                today                Today's total
                yesterday            Yesterday's total
                month <YYYY-MM>      Total for a specific month
                projects [YYYY-MM]   Total per project
                project <name>       Total for a specific project
                categories [YYYY-MM] Total per category
                category <name>      Total for a specific category

  tlupdate    Add a new entry interactively
                tlupdate             Uses today's date
                tlupdate YYYY-MM-DD  Sets the entry date explicitly

  tlexport    Export all entries to timelog-YYYY-MM-DD.csv

  tlimport    Replace database with entries from a CSV file
                tlimport <file.csv>
""")
