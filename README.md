# 🕐 CLI Timelog App

<details>
<summary>Table of Contents</summary>

<!-- mtoc-start -->

* [How it works](#how-it-works)
* [Installation and pre-requisites](#installation-and-pre-requisites)
* [`tlhelp`](#tlhelp)
* [Functions](#functions)
  * [`tlupdate`](#tlupdate)
    * [`tlupdate [YYYY-MM-DD]`](#tlupdate-yyyy-mm-dd)
  * [`tlshow`](#tlshow)
    * [`tlshow today`](#tlshow-today)
    * [`tlshow yesterday`](#tlshow-yesterday)
    * [`tlshow last`](#tlshow-last)
    * [`tlshow projects`](#tlshow-projects)
    * [`tlshow project <project_name>`](#tlshow-project-project_name)
    * [`tlshow categories`](#tlshow-categories)
    * [`tlshow category <category_name>`](#tlshow-category-category_name)
    * [`tlshow month <YYYY-MM>`](#tlshow-month-yyyy-mm)
  * [`tlsum`](#tlsum)
    * [`tlsum today`](#tlsum-today)
    * [`tlsum yesterday`](#tlsum-yesterday)
    * [`tlsum projects [YYYY-MM]`](#tlsum-projects-yyyy-mm)
    * [`tlsum project <project_name>`](#tlsum-project-project_name)
    * [`tlsum categories [YYYY-MM]`](#tlsum-categories-yyyy-mm)
    * [`tlsum category <category_name>`](#tlsum-category-category_name)
    * [`tlsum month <YYYY-MM>`](#tlsum-month-yyyy-mm)
  * [`tlexport`](#tlexport)

<!-- mtoc-end -->

</details>

Tired of living with an intern timelog project that accidentally became production software?  
Started a new company with an even worse time tracking application than you could have ever imagined?  
Tired of having to use your freaking mouse?!

Well - look no further. This CLI Timelog App is your one-way ticket to time efficiency!

## How it works

This application runs entirely locally in Docker. Two containers — a Python/FastAPI backend and a SvelteKit frontend — are managed by Docker Compose. Your data lives in a SQLite file at `./data/timelog.db`, bind-mounted from your host so it's always accessible and easy to back up.

CLI commands (`tlshow`, `tlsum`, etc.) are available as shell functions that forward into the API container — no separate install required.

## Installation and pre-requisites

Pre-requisites:
* Docker + Docker Compose
* Git

**1. Clone the repo:**
```bash
git clone https://github.com/awall451/timelog-vibed.git
cd timelog-vibed
```

**2. Source the dev helpers:**
```bash
source dev.sh
```

Add this to your `~/.bashrc` to make `tlstart`, `tlstop`, and all `tl*` commands available in every shell.

**3. Start the app:**
```bash
tlstart
```

That's it! Docker builds and starts both containers on first run.

| Service  | URL                      |
|----------|--------------------------|
| Frontend | http://localhost:3000    |
| API      | http://localhost:8888    |

```bash
tlstop   # stop everything
```

Your database is created automatically at `./data/timelog.db` on first run.

## `tlhelp`

If you ever get stuck, just type `tlhelp` in the terminal for the built-in reference page. It prints a help screen with explanations of all functions and subcommands.

![](.img/tlhelp.png)

Please, forgive me if the image is out of date. This is going to be an ever-evolving project, and "ain't nobody got time for that."

![](.img/aint-nobody-got-time-for-that-kimberly-wilkins.gif)

Sheesh.

## Functions

The CLI commands make updating and viewing your timelog a breeze.

### `tlupdate`

`tlupdate` will be your bread & butter. Use this to submit a time entry for today's date. It walks you through interactive prompts for project, category, description, and hours.

![](.img/tlupdate.png)

#### `tlupdate [YYYY-MM-DD]`

Optionally pass a date argument to create an entry for a specific day. For example, to submit an entry for Feb 03, 2026:

```bash
tlupdate 2026-02-03
```

The format must be `YYYY-MM-DD` (as all dates should be, but I digress).

![](.img/tlupdate_date.png)

### `tlshow`

The `tlshow` function shows all of your timelog entries.

![](.img/tlshow.png)

The `tlshow` function also has several subcommands to help filter down to specific types of entries.

```bash
tlshow .
Unknown subcommand: .
Usage: tlshow [OPTIONS] COMMAND [ARGS]...
Commands:
  categories  List all distinct categories.
  category    Show entries for a specific category.
  last        Show the most recent entry.
  month       Show entries for YYYY-MM.
  project     Show entries for a specific project.
  projects    List all distinct projects.
  today       Show today's entries.
  yesterday   Show yesterday's entries.
```

#### `tlshow today`

Use `tlshow today` to see only today's entries!

![](.img/tlshow_today.png)

#### `tlshow yesterday`

Use `tlshow yesterday` to see entries for the day before.

![](.img/tlshow_yesterday.png)

#### `tlshow last`

Use `tlshow last` to see the last entry in the table. Useful to verify the entry you just submitted was correct!

![](.img/tlshow_last.png)

#### `tlshow projects`

Use `tlshow projects` to see a list of all projects in the entries table.

```bash
tlshow projects
Nebula Kart
Personal Growth
Starfall Odyssey
Studio Ops
Studio Website
```

#### `tlshow project <project_name>`

Use `tlshow project` to see all entries filtered by a specific project. Don't forget to wrap `<project_name>` in quotes if it is more than one word!

```bash
tlshow project "Nebula Kart"
```

![](.img/tlshow_project.png)

#### `tlshow categories`

Use `tlshow categories` to see a list of all categories in the entries table.

```bash
tlshow categories
Audio
Bugfixing
CI/CD
Code Review
Design
Development
Finance
Learning
Marketing
Meetings
Optimization
Testing
```

#### `tlshow category <category_name>`

Use `tlshow category` to see all entries filtered by a specific category. Don't forget to wrap `<category_name>` in quotes if it is more than one word!

```bash
tlshow category "Code Review"
```

![](.img/tlshow_category.png)

#### `tlshow month <YYYY-MM>`

Use `tlshow month` to see all entries filtered by the provided month.

```bash
tlshow month 2026-01
```

![](.img/tlshow_month.png)

### `tlsum`

The `tlsum` function shows the total sum of hours for all timelog entries.

![](.img/tlsum.png)

The `tlsum` function also has several subcommands to filter down what sum you are looking for.

```bash
tlsum .
Unknown subcommand: .
Usage: tlsum [OPTIONS] COMMAND [ARGS]...
Commands:
  categories  Total hours per category, optionally filtered to YYYY-MM.
  category    Total hours for a specific category.
  month       Total hours for YYYY-MM.
  project     Total hours for a specific project.
  projects    Total hours per project, optionally filtered to YYYY-MM.
  today       Total hours for today.
  yesterday   Total hours for yesterday.
```

#### `tlsum today`

Use `tlsum today` to see the total of today's entries. Helpful when filling out your timelog and trying to hit 8 hours without doing math in your head (or on your fingers!).

```bash
tlsum today
Total hours: 1.00
```

#### `tlsum yesterday`

Use `tlsum yesterday` to see the sum of all entries for the day before.

```bash
tlsum yesterday
Total hours: 4.00
```

#### `tlsum projects [YYYY-MM]`

Use `tlsum projects` to see the sum of hours per distinct project.
Optionally pass a month as a second argument to filter to a specific month.

![](.img/tlsum_projects.png)

#### `tlsum project <project_name>`

Use `tlsum project` to see the total hours for a specific project. Don't forget quotes for multi-word names!

```bash
tlsum project 'Nebula Kart'
Total hours: 54.50
```

#### `tlsum categories [YYYY-MM]`

Use `tlsum categories` to see the sum of hours per distinct category.
Optionally pass a month argument to filter to a specific month.

![](.img/tlsum_categories.png)

#### `tlsum category <category_name>`

Use `tlsum category` to see the total hours for a specific category.

```bash
tlsum category 'Code Review'
Total hours: 4.00
```

#### `tlsum month <YYYY-MM>`

Use `tlsum month` to see the total hours for a specific month.

```bash
tlsum month 2026-01
Total hours: 47.50
```

### `tlexport`

Use `tlexport` to export your entire timelog database to a CSV file in the current directory.

```bash
tlexport
Exporting entries to timelog-2026-04-16.csv...
Export complete: timelog-2026-04-16.csv
```

![](.img/tlexport.png)

## Database

Your data lives at `~/.local/share/timelog/timelog.db` — a plain SQLite file. Back it up like any other file. You can open it directly with any SQLite client if you ever need raw access.
