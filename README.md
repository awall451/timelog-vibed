# CLI Timelog App
<details>
<summary>Table of Contents</summary>

<!-- mtoc-start -->

* [How it works](#how-it-works)
* [Installation and pre-requisites](#installation-and-pre-requisites)
* [tlhelp](#tlhelp)
* [Functions](#functions)
  * [tlupdate](#tlupdate)
    * [tlupdate 'date'](#tlupdate-date)
  * [tlshow](#tlshow)
    * [tlshow subcommands](#tlshow-subcommands)
      * [tlshow today](#tlshow-today)
      * [tlshow yesterday](#tlshow-yesterday)
      * [tlshow last](#tlshow-last)
      * [tlshow project](#tlshow-project)
      * [tlshow category](#tlshow-category)
  * [tlexport](#tlexport)
  * [tlexec](#tlexec)

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

## tlhelp
If you ever get stuck or don't want to sift through this README, just type `tlhelp` in the terminal for the 'man' page. This will printout a 
help screen with explainations of all functions and subcommands.

![](.img/tlhelp.png)

Please, forgive me if the image is out of date. This is going to be an ever-evolving project, and "ain't nobody got time for that." 

![](.img/aint-nobody-got-time-for-that-kimberly-wilkins.gif)

Sheesh.

## Functions

The bash functions steal the show here. They make updating and viewing your timelog a breeze.

### tlupdate

`tlupdate` will be your bread & butter. Use this to submit a time entry for today's date.

![](.img/tlupdate.png)


#### tlupdate 'date'

Optionally with `tlupdate`, you can pass an arument for a specfic date you want to create an entry for! 
For example, if you want to submit an entry for Feb 03, 2026 - you can type `tlupdate 2026-02-03`. 
The syntax does matter here, and your command line will complain if the format is not YYYY-MM-DD (as all dates should be, but I digress).

![](.img/tlupdate_date.png)

### tlshow

The `tlshow` function shows all of your timelog entries on the `entries` table.

![](.img/tlshow.png)


#### tlshow subcommands

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

##### tlshow today

Use `tlshow today` to see only today's entries!

![](.img/tlshow_today.png)


##### tlshow yesterday

Use `tlshow yesterday` to see entries for the day before - or in SQL talk, `CURRENT_DATE - INTERVAL '1 DAY'`

![](.img/tlshow_yesterday.png)

##### tlshow last

Use `tlshow last` to see the last entry in the table. Useful to make sure the last entry you just submitted was correct!

![](.img/tlshow_last.png)

##### tlshow project

Use `tlshow project` to see all entries filtered by a specific project in the project column of the table. Syntax is 
`tlshow project <project_name>`. Don't forget to wrap the `<project_name>` in quotes if it is more than one word!

![](.img/tlshow_project.png)

##### tlshow category

Use `tlshow category` to see all entries filtered by a specific category in the category column of the table. Syntax is 
`tlshow category <category_name>`. Don't forget to wrap the `<category_name>` in quotes if it is more than one word!

![](.img/tlshow_category.png)


### tlexport

Use `tlexport` to export your entire timelog database to a CSV file!

![](.img/tlexport.png)

### tlexec

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
