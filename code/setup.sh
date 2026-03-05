#!/usr/bin/env bash
# Content Triage Agent – install dependencies and seed the database.
# Run from the code/ directory. After this, update .env and then run ./run.sh

set -e
CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$CODE_DIR"

echo "Installing packages..."
if command -v pipenv &>/dev/null; then
  pipenv install
else
  pip install -r requirements.txt
fi

echo "Seeding database..."
export PYTHONPATH="$CODE_DIR"
python -m src.db.seed

echo "Setup complete. Next: copy .env.example to .env, set your env variables, then run ./run.sh -c or ./run.sh -u"
