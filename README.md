# 🕐 Timelog

<details>
<summary>Table of Contents</summary>

<!-- mtoc-start -->

* [How it works](#how-it-works)
* [Installation and pre-requisites](#installation-and-pre-requisites)
* [Frontend](#frontend)
  * [Dashboard](#dashboard)
  * [Log Time](#log-time)
  * [Live Timer](#live-timer)
  * [Themes](#themes)
  * [Entries page](#entries-page)
    * [Activity heatmap](#activity-heatmap)
    * [Sorting](#sorting)
    * [Click-to-filter](#click-to-filter)
    * [Date filter](#date-filter)
    * [Edit and delete entries](#edit-and-delete-entries)
  * [Charts page](#charts-page)
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
  * [`tlimport`](#tlimport)
* [Database](#database)

<!-- mtoc-end -->

</details>

Tired of living with an intern timelog project that accidentally became production software?  
Started a new company with an even worse time tracking application than you could have ever imagined?  
Tired of having to use your freaking mouse?!

Well - look no further. Timelog is your one-way ticket to time efficiency!

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

## Frontend

The web UI is available at http://localhost:3000 after running `tlstart`. Four pages are available in the navigation bar: **Dashboard**, **Entries**, **Charts**, and **Log Time**.

### Dashboard

The dashboard shows today's hours against an 8-hour goal, a live table of today's entries, and a bar chart of all-time hours by project.

![](.img/screenshots/dashboard.png)

### Log Time

The **Log Time** page is the web equivalent of `tlupdate`. Fill in project, category, description, hours, and an optional date (defaults to today), then hit **Save Entry**. Project and category fields support autocomplete from your existing data.

![](.img/screenshots/log_empty.png)

### Live Timer

A floating clock widget lives in the bottom-right corner of every page. Click it to expand a panel where you can start a timer for a project and category.

**Starting a timer:**
1. Click the clock to open the panel
2. Fill in Project, Category, and an optional Description
3. Click **Start Timer** — once running, the panel shows elapsed time and a **Stop & Log** button

<table align="center">
<tr>
<td align="center"><img src=".img/screenshots/timer_step1.png" width="220"><br><sub>Open</sub></td>
<td align="center" valign="middle"><strong>&nbsp;→&nbsp;</strong></td>
<td align="center"><img src=".img/screenshots/timer_step2.png" width="220"><br><sub>Fill in details</sub></td>
<td align="center" valign="middle"><strong>&nbsp;→&nbsp;</strong></td>
<td align="center"><img src=".img/screenshots/timer_step3.png" width="220"><br><sub>Running</sub></td>
</tr>
</table>

Clicking **Stop & Log** calculates hours, pre-fills the Log Time form, and redirects you there to review and save. Timer state persists to `localStorage`, so refreshing or navigating away won't lose a running timer.

### Themes

Six themes are available from the selector in the top navigation bar. Your choice is saved to `localStorage` and persists across page reloads.

| Theme | Description |
|---|---|
| Default | Dark blue-grey |
| Tokyo Night | Deep navy with purple accents |
| Cyberpunk | High contrast neon |
| Dracula | Classic purple dark theme |
| Rosé Pine | Muted warm tones |
| Catppuccin Latte | Light theme |

<table>
<tr>
<td align="center"><strong>Default</strong><br><img src=".img/screenshots/dashboard_default.png"></td>
<td align="center"><strong>Tokyo Night</strong><br><img src=".img/screenshots/dashboard_tokyonight.png"></td>
<td align="center"><strong>Cyberpunk</strong><br><img src=".img/screenshots/dashboard_cyberpunk.png"></td>
</tr>
<tr>
<td align="center"><strong>Dracula</strong><br><img src=".img/screenshots/dashboard_dracula.png"></td>
<td align="center"><strong>Rosé Pine</strong><br><img src=".img/screenshots/dashboard_rosepine.png"></td>
<td align="center"><strong>Catppuccin Latte</strong><br><img src=".img/screenshots/dashboard_catppuccin.png"></td>
</tr>
</table>

### Entries page

The **Entries** page shows your full history. A GitHub-style activity heatmap sits above the table, followed by a sortable, filterable entry list. The footer shows the entry count and total hours for the current view.

![](.img/screenshots/entries.png)

#### Activity heatmap

The heatmap displays the last 52 weeks of activity as a grid of cells — darker cells mean more hours logged that day. Color intensity has five levels: no activity, <2h, <4h, <6h, and 6h+.

![](.img/screenshots/entries_heatmap.png)

**Click any cell** to filter the entries table to that day — a date chip appears in the filter bar. Click the × on the chip to clear.

![](.img/screenshots/entries_heatmap_cell_selected.png)

**Filter-aware:** When a project or category filter is active, the heatmap re-derives its intensities from only the matching entries. This lets you see your activity pattern for a specific project at a glance.

![](.img/screenshots/entries_heatmap_filtered.png)

#### Sorting

Click the **Date** column header to toggle between newest-first and oldest-first. An ↑/↓ indicator shows the active direction.

![](.img/screenshots/entries_sort_asc.png)

#### Click-to-filter

Click directly on any value in the table to filter to it — no need to touch the dropdowns:

- **Project name** → filters the table and syncs the project dropdown
- **Category badge** → filters the table and syncs the category dropdown
- Click the same cell again (or the × chip) to clear

Project filter active:

![](.img/screenshots/entries_filter_project.png)

Category filter active:

![](.img/screenshots/entries_filter_category.png)

#### Date filter

Click the **Date** button in the filter bar to reveal a text input. Type any partial ISO date to filter:

| Input | Result |
|---|---|
| `2026` | All entries in 2026 |
| `2026-04` | All entries in April 2026 |
| `2026-04-15` | Entries on a specific day |

Click the calendar icon inside the input to use a date picker instead of typing. Click **Date** again to collapse — your typed value is retained.

![](.img/screenshots/entries_filter_date.png)

#### Edit and delete entries

Hover over any row to reveal the **⋮** action button on the right. Click it to open a dropdown with **Edit** and **Delete** options.

![](.img/screenshots/entries_row_menu.png)

Clicking **Edit** opens a modal pre-filled with the entry's current values. Update any field and hit **Save** — the table updates immediately and re-sorts by date.

![](.img/screenshots/entries_edit_modal.png)

Clicking **Delete** shows an inline confirmation (**Yes / No**) before removing the entry.

### Charts page

The **Charts** page (`/charts`) gives you a visual breakdown of where your time goes. All charts respond to the **From / To** date range picker in the top-right.

![](.img/screenshots/charts.png)

**Hours by Project** and **Hours by Category** donuts show the share of total hours for each, with exact hour counts and percentages in the legend.

![](.img/screenshots/charts_donuts.png)

**Daily Hours** shows a stacked bar chart of the last 14 days, with each project as a color segment. Gaps in the bars are days with no logged time.

![](.img/screenshots/charts_stacked_bar.png)

The page also includes a **Weekly Pace** sparkline (last 28 days vs. an 8h/day goal line) and a **Project × Category** heat matrix showing exactly where hours go across both dimensions.

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

### `tlimport`

Use `tlimport` to replace your entire database with entries from a CSV file. This is useful for migrating data from another timelog instance or restoring from a backup.

```bash
tlimport timelog-2026-04-19.csv
Importing from timelog-2026-04-19.csv...
Imported 217 entries.
```

The CSV must have the following columns (matching the `tlexport` format):

```
id,project,category,description,hours,date
```

> **Warning:** `tlimport` replaces all existing entries. Export first if you want to keep your current data.

You can also import via the API directly from the host:

```bash
curl -X POST http://localhost:8888/import -F "file=@timelog-2026-04-19.csv"
# {"imported": 217}
```

## Database

Your data lives at `./data/timelog.db` — a plain SQLite file bind-mounted from the host into the container. Back it up like any other file, or use `tlexport` to get a CSV snapshot. You can open it directly with any SQLite client if you ever need raw access.
