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
  echo "Greetings!"
  echo
  echo "What project did you work on?"
  read -r project
  echo
  echo -e "Category?\nSome options: Timelog, Vulnerability/Security, SCRUM, Product, Automation"
  read -r category
  echo
  echo "Give a brief description of the work..."
  read -r description
  echo
  echo "How many hours?"
  read -r hours
  echo

  docker exec -i timelog \
    psql -U admin -d timelog <<EOF
INSERT INTO entries (project, category, description, hours)
VALUES ('$project', '$category', '$description', $hours);
EOF
}
