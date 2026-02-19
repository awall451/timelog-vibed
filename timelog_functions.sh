#!/usr/bin/env bash

alias tlexec='docker exec -it timelog psql -U admin -d timelog'

tlshow() {
  subcommand="$1"
  shift

  case "$subcommand" in
    "" )
      # No args → show all
      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries;"
      ;;
    today )
      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries WHERE date = CURRENT_DATE;"
      ;;
    yesterday )
      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries WHERE date = (CURRENT_DATE - INTERVAL '1 DAY');"
      ;;
    last )
      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries ORDER BY id DESC LIMIT 1;"
      ;;
    projects )
      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT DISTINCT project FROM entries ORDER BY project;"
      ;;
    project )
      if [[ -z "$1" ]]; then
        echo "Error: project name required"
        echo "Usage: tlshow project <projectname>"
        return 1
      fi

      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries WHERE project = '$1';"
      ;;
    categories )
      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT DISTINCT category FROM entries ORDER BY category;"
      ;;
    category )
      if [[ -z "$1" ]]; then
        echo "Error: category name required"
        echo "Usage: tlshow category <categoryname>"
        return 1
      fi

      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries WHERE category = '$1';"
      ;;
    * )
      echo "Unknown subcommand: $subcommand"
      echo "Usage:"
      echo "  tlshow"
      echo "  tlshow last"
      echo "  tlshow today"
      echo "  tlshow yesterday"
      echo "  tlshow project <projectname>"
      echo "  tlshow category <categoryname>"
      return 1
      ;;
  esac
}

tlsum() {
  subcommand="$1"
  shift

  case "$subcommand" in
    "" )
      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT 'Total hours: ' || SUM(hours) AS result FROM entries;"
      ;;
    today )
      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT 'Total hours: ' || SUM(hours) AS result FROM entries WHERE date = CURRENT_DATE;"
      ;;
    yesterday )
      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT 'Total hours: ' || SUM(hours) AS result FROM entries WHERE (date = CURRENT_DATE - INTERVAL '1 DAY');"
      ;;
    projects )
      docker exec timelog psql -U admin -d timelog \
        -c 'SELECT project AS "Project Name", SUM(hours) AS "Hours" FROM entries GROUP BY project ORDER BY "Hours" DESC;'
      ;;
    project )
      if [[ -z "$1" ]]; then
        echo "Error: project name required"
        echo "Usage: tlsum project <projectname>"
        return 1
      fi

      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT 'Total hours: ' || SUM(hours) AS result FROM entries WHERE project = '$1';"
      ;;
    categories )
      docker exec timelog psql -U admin -d timelog \
        -c 'SELECT category AS "Category Name", SUM(hours) AS "Hours" FROM entries GROUP BY category ORDER BY "Hours" DESC;'
      ;;
    category )
      if [[ -z "$1" ]]; then
        echo "Error: category name required"
        echo "Usage: tlsum category <categoryname>"
        return 1
      fi

      docker exec timelog psql -U admin -d timelog -tA \
        -c "SELECT 'Total hours: ' || SUM(hours) AS result FROM entries WHERE category = '$1';"
      ;;
    * )
      echo "Unknown subcommand: $subcommand"
      echo "Usage:"
      echo "  tlsum"
      echo "  tlsum today"
      echo "  tlsum yesterday"
      echo "  tlsum projects"
      echo "  tlsum project <projectname>"
      echo "  tlsum categories"
      echo "  tlsum category <categoryname>"
      return 1
      ;;
  esac
}

tlupdate() {
  entry_date="$1"

  # Optional date validation
  if [[ -n "$entry_date" ]]; then
    if [[ ! "$entry_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
      echo "Error: date must be in YYYY-MM-DD format"
      echo "Usage: tlupdate [YYYY-MM-DD]"
      return 1
    fi
    if ! date -d "$entry_date" >/dev/null 2>&1; then
      echo "Error: invalid date: $entry_date"
      return 1
    fi
  fi

  echo "Greetings!"
  echo
  echo "What project did you work on?"
  read -r project
  echo
  echo -e "Category?\nSome options: Timelog, Vulnerability/Security, SCRUM, Product, Automation..."
  read -r category
  echo
  echo "Give a brief description of the work..."
  read -r description
  echo
  echo "How many hours?"
  read -r hours
  echo

  # ----- Basic hours validation (positive number, allows decimals)
  if [[ ! "$hours" =~ ^[0-9]+([.][0-9]+)?$ ]] || awk "BEGIN{exit !($hours>0)}"; then
    :
  else
    echo "Error: hours must be a positive number"
    return 1
  fi

  # ----- Escape single quotes for SQL strings
  project=${project//\'/\'\'}
  category=${category//\'/\'\'}
  description=${description//\'/\'\'}

  if [[ -z "$entry_date" ]]; then
    # ----- No date provided → let DEFAULT CURRENT_DATE handle it
    docker exec -i timelog \
      psql -U admin -d timelog <<EOF
INSERT INTO entries (project, category, description, hours)
VALUES ('$project', '$category', '$description', $hours);
EOF
  else
    # ----- Date provided → explicitly set it
    docker exec -i timelog \
      psql -U admin -d timelog <<EOF
INSERT INTO entries (project, category, description, hours, date)
VALUES ('$project', '$category', '$description', $hours, DATE '$entry_date');
EOF
  fi
}

# ----- CSV Export Function
tlexport() {
  today=$(date +%Y-%m-%d)
  filename="timelog-${today}.csv"

  echo "Exporting entries table to ${filename}..."

  docker exec -i timelog \
    psql -U admin -d timelog \
    -c "\copy entries TO STDOUT WITH CSV HEADER" \
    > "$filename"

  if [[ $? -eq 0 ]]; then
    echo "Export complete: $filename"
  else
    echo "Export failed."
    return 1
  fi
}

# ----- Help page
tlhelp() {
  local BOLD RESET
  BOLD=$(printf '\033[1m')
  RESET=$(printf '\033[0m')

  cat <<EOF
cli-timelog
Track work entries in a local Postgres timelog database (via Docker).

${BOLD}USAGE${RESET}
  tlhelp
  tlshow [subcommand]
  tlupdate [YYYY-MM-DD]
  tlexport
  tlexec

${BOLD}AVAILABLE COMMANDS${RESET}
  tlhelp      Show this help page

  tlshow      Display entries (all, filtered, or recent)
              Subcommands:
                (none)                 Show all entries
                today                  Show entries for today (CURRENT_DATE)
                yesterday              Show entries for yesterday
                last                   Show the most recent entry
                project <name>         Show entries for a project
                category <name>        Show entries for a category

  tlupdate    Add a new entry (interactive prompts)
              Optionally supply the work date:
                tlupdate               Uses the table default date (CURRENT_DATE)
                tlupdate YYYY-MM-DD    Sets the entry date explicitly

  tlexport    Export entries table to a dated CSV in the current directory
              Output: timelog-YYYY-MM-DD.csv

  tlexec      Open an interactive psql session (alias)
              Runs: docker exec -it timelog psql -U admin -d timelog

${BOLD}EXAMPLES${RESET}
  tlshow
  tlshow last
  tlshow today
  tlshow yesterday
  tlshow project "Timelog App"
  tlshow category "Meeting"

  tlupdate
  tlupdate 2026-02-06

  tlexport
  ls timelog-*.csv

EOF
}
