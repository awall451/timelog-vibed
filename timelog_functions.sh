#!/usr/bin/env bash

alias timelog='docker exec -it timelog psql -U admin -d timelog'

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
    project )
      if [[ -z "$1" ]]; then
        echo "Error: project name required"
        echo "Usage: tlshow project <projectname>"
        return 1
      fi

      docker exec timelog psql -U admin -d timelog \
        -c "SELECT * FROM entries WHERE project = '$1';"
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
      echo "  tlshow today"
      echo "  tlshow project <projectname>"
      echo "  tlshow category <categoryname>"
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
