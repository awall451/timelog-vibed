# CLI Timelog App

Tired of terrible user interface timelog applications?  
Started a new company with an even worse time tracking application than you could ever imagine?  
Tired of having to use your freaking mouse?!

Well - look no further. This CLI Timelog App is your one-way ticket to time efficiency!

## How it works

This application is very basic, and designed to run locally on your system in a docker container! 
It will work in any Linux, Mac, or Windows (WSL2) environment. There is a single PostgreSQL container, 
and some `bash` functions to source in your `~/.bashrc` file. *That's it!* 

## Installation and pre-requisites

Before installing, decide first if you want to use the default username and password. 
The username and password are hard coded, but feel free to change them. However, if you do change the username, 
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

## Functions

The bash functions steal the show here. They make updating and viewing your timelog a breeze.

### timelog

The first one is a basic alias. The `timelog` alias gives you quick access inside the database 
to directly run SQL Queries.
```bash
dillon@spartan:/opt/timelog$ timelog
psql (16.12 (Debian 16.12-1.pgdg13+1))
Type "help" for help.

timelog=# 
```

### tlshow

The `tlshow` function shows all of your timelog entries on the `entries` table.

#### tlshow subcommands

The `tlshow` function also has subcommands to help filter down to specific types of entries.
```bash
dillon@SLB-1H85255ZKY:~/lab/timelog-database$ tlshow .
Unknown subcommand: .
Usage:
  tlshow
  tlshow today
  tlshow project <projectname>
  tlshow category <categoryname>
```

##### tlshow today

Use `tlshow today` to see only today's entries!

##### tlshow project

##### tlshow category

