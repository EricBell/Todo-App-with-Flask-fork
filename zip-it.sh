#!/bin/bash

# Usage: ./zip-it.sh preedit|da|sonnet

case "$1" in
  preedit)
    ZIPFILE="preedit_codebase.zip"
    ;;
  beetle)
    ZIPFILE="postedit_codebase_beetle.zip"
    ;;
  sonnet)
    ZIPFILE="postedit_codebase_sonnet.zip"
    ;;
  rewrite)
    ZIPFILE="rewrite_codebase.zip"
    ;;
  *)
    echo "Usage: $0 {preedit|beetle|sonnet|rewrite}"
    exit 1
    ;;
esac

# zip -r "$ZIPFILE" . -x ".venv/*" ".venv" ".git/*" ".git" "*/__pycache__/*" "__pycache__" "zip-it.sh" "clean.sh" "tests/*" "tests"
zip -r "$ZIPFILE" . -x "*.venv/*" "*.git/*" "*__pycache__/*" "*__pycache__" "zip-it.sh" "clean.sh" "tests/*" "tests" "run-tests-in-docker.sh"