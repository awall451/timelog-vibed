# CLI Timelog App
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
  * [`tlexec`](#tlexec)

<!-- mtoc-end -->

</details>

Tired of living with an intern timelog project that accidentally became production software?  
Started a new company with an even worse time tracking application than you could have ever imagined?  
Tired of having to use your freaking mouse?!

Well - look no further. This CLI Timelog App is your one-way ticket to time efficiency!

## How it works

This application is very basic, and designed to run locally on your system in a docker container! 
It will work in any Linux, Mac, or Windows (WSL2) environment. There is a single PostgreSQL container, 
and some `bash` functions to source in your `~/.bashrc` file. *That's it!* 

## Installation and pre-requisites

Before installing, decide first if you want to use the default username and password. 
The username and password are hard coded in `compose.yml`, but feel free to change them. However, if you do change the username, 
you will need to modify this username in `timelog_functions.sh`! You can do this with sed easily:
```bash
# ---- Replace <username> with the POSTGRES_USER value set in compose.yml
sed -i 's/admin/<username>/g' timelog_functions.sh
```

Pre-requisites:
* Docker
* Docker compose

To install:
* Clone this repository to your local filesystem.
* Add functions to your `~/.bashrc` (run this command from within the repo directory, or give full path)
```bash
readlink -f timelog_functions.sh | xargs echo "source $1" >> ~/.bashrc

# ----- Re-source your bashrc for functions to work in your current shell
. ~/.bashrc
```
* Modify username & password if desired (mentioned above)
* Run `docker compose up -d`

*That's it!*

When starting the container for the first time, docker will create a local volume called `pgdata`. This 
is where your database lives on your host, so don't mess it up! First time startup will create the table 
by running the SQL statments in `create-table.sql`.

## `tlhelp`
If you ever get stuck or don't want to sift through this README, just type `tlhelp` in the terminal for the 'man' page. This will printout a 
help screen with explainations of all functions and subcommands.

![](.img/tlhelp.png)

Please, forgive me if the image is out of date. This is going to be an ever-evolving project, and "ain't nobody got time for that." 

![](.img/aint-nobody-got-time-for-that-kimberly-wilkins.gif)

Sheesh.

## Functions

The bash functions steal the show here. They make updating and viewing your timelog a breeze.

### `tlupdate`

`tlupdate` will be your bread & butter. Use this to submit a time entry for today's date.

![](.img/tlupdate.png)


#### `tlupdate [YYYY-MM-DD]`

Optionally with `tlupdate`, you can pass an arument for a specfic date you want to create an entry for! 
For example, if you want to submit an entry for Feb 03, 2026 - you can type `tlupdate 2026-02-03`. 
The syntax does matter here, and your command line will complain if the format is not YYYY-MM-DD (as all dates should be, but I digress).

![](.img/tlupdate_date.png)

### `tlshow`

The `tlshow` function shows all of your timelog entries on the `entries` table.

![](.img/tlshow.png)


The `tlshow` function also has several subcommands to help filter down to specific types of entries.

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main on  (us-west-2) took 0s
 ╰─λ tlshow .
Unknown subcommand: .
Usage:
  tlshow
  tlshow last
  tlshow today
  tlshow yesterday
  tlshow project <projectname>
  tlshow category <categoryname>
```

#### `tlshow today`

Use `tlshow today` to see only today's entries!

![](.img/tlshow_today.png)


#### `tlshow yesterday`

Use `tlshow yesterday` to see entries for the day before - or in SQL talk, `CURRENT_DATE - INTERVAL '1 DAY'`

![](.img/tlshow_yesterday.png)

#### `tlshow last`

Use `tlshow last` to see the last entry in the table. Useful to make sure the last entry you just submitted was correct!

![](.img/tlshow_last.png)

#### `tlshow projects`

Use `tlshow projects` to see a list of all projects in the entries table. 

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$] on  (us-west-2) took 0s
 ╰─λ tlshow projects
Nebula Kart
Personal Growth
Starfall Odyssey
Studio Ops
Studio Website
```

#### `tlshow project <project_name>`

Use `tlshow project` to see all entries filtered by a specific project in the project column of the table. Syntax is 
`tlshow project <project_name>`. Don't forget to wrap the `<project_name>` in quotes if it is more than one word!

![](.img/tlshow_project.png)

#### `tlshow categories`

Use `tlshow categories` to see a list of all categories in the entries table. 

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$] on  (us-west-2) took 0s
 ╰─λ tlshow categories
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

Use `tlshow category` to see all entries filtered by a specific category in the category column of the table. Syntax is 
`tlshow category <category_name>`. Don't forget to wrap the `<category_name>` in quotes if it is more than one word!

![](.img/tlshow_category.png)

#### `tlshow month <YYYY-MM>`

Use `tlshow month` to see all entries filtered by the provided month. Syntax is 
`tlshow month <YYYY-MM>`. 

![](.img/tlshow_month.png)

### `tlsum`

The `tlsum` function shows the total sum of hours for all timelog entries on the `entries` table.

![](.img/tlsum.png)

The `tlsum` function also has several subcommands to filter down what sum you are looking to achieve.

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$] on  (us-west-2) took 0s
[🔴] × tlsum .
Unknown subcommand: .
Usage:
  tlsum
  tlsum today
  tlsum yesterday
  tlsum projects [YYYY-MM]
  tlsum project <projectname>
  tlsum categories [YYYY-MM]
  tlsum category <categoryname>
  tlsum month <YYYY-MM>
```

#### `tlsum today`

Use `tlsum today` to see only the sum of today's entries! This is helpful when you are filling out timelog for the day, and are trying to hit your 8 
hours without having to do all the math in your head (or on your fingers!).

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$!?] on  (us-west-2) took 0s
 ╰─λ tlsum today
Total hours: 1.00
```

#### `tlsum yesterday`

Use `tlsum yesterday` to see the sum of all entries for the day before - or in SQL talk, `CURRENT_DATE - INTERVAL '1 DAY'`

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$!?] on  (us-west-2) took 0s
 ╰─λ tlsum yesterday
Total hours: 4.00
```

#### `tlsum projects [YYYY-MM]`

Use `tlsum projects` to see the sum of hours you have in each distinct project. 
This will help give you full perspective of what projects your time is going into. 
Optionally - pass the year and month (YYYY-MM) as a second argumet to see only the sum of that project for a specific month.

![](.img/tlsum_projects.png)

#### `tlsum project <project_name>`

Use `tlsum project` to see the sum of all hours for a specific project name. Syntax is 
`tlsum project <project_name>`. Don't forget to wrap the `<project_name>` in quotes if it is more than one word!

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$!?] on  (us-west-2) 
[🧱] × tlsum project 'Nebula Kart'
Total hours: 54.50
```

#### `tlsum categories [YYYY-MM]`

Use `tlsum categories` to see the sum of all hours for each distinct category. 
This will help give you full perspective of what categories your time is going into. 
Optionally - pass the year and month (YYYY-MM) as a second argumet to see only the sum of that category for a specific month.

![](.img/tlsum_categories.png)

#### `tlsum category <category_name>`

Use `tlsum category` to see the sum of all hours for a specific category. Syntax is 
`tlsum category <category_name>`. Don't forget to wrap the `<category_name>` in quotes if it is more than one word!

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$!?] on  (us-west-2) took 0s
 ╰─λ tlsum category 'Code Review'
Total hours: 4.00
```

#### `tlsum month <YYYY-MM>`

Use `tlsum month` to see the sum of all hours filtered by the provided month. Syntax is 
`tlsum month <YYYY-MM>`. 

```bash
 ╭─dillon@garuda in repo: cli-timelog on  main [$!?] on  (us-west-2) took 0s
 ╰─λ tlsum month 2026-01
Total hours: 47.50
```

### `tlexport`

Use `tlexport` to export your entire timelog database to a CSV file!

![](.img/tlexport.png)

### `tlexec`

The `tlexec` alias gives you quick access inside the database 
to directly run SQL Queries.
```bash
 ╭─dillon@garuda in repo: cli-timelog on  main on  (us-west-2) took 0s
 ╰─λ tlexec
psql (16.12 (Debian 16.12-1.pgdg13+1))
Type "help" for help.

timelog=#
```

![Timelog function.](.img/tlexec.png)
