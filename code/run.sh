#!/usr/bin/env bash
# Content Triage Agent – run after setup.sh and updating .env.
# Usage:
#   ./run.sh -u       Start API + Web UI (service). Then open http://localhost:8000
#   ./run.sh -c       Run interactive console (multiple submissions, pipeline + JSON)
#   -f (file mode)    Run manually: python run_triage.py -f path/to/file.txt
#
# Run this script from the code/ directory. Requires .env with required variables set.

set -e
CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$CODE_DIR"
export PYTHONPATH="$CODE_DIR"

# Require .env to exist
if [ ! -f .env ]; then
  echo "Error: .env file not found. Copy .env.example to .env and set your variables (e.g. DATABASE_URL, LITELLM_MODEL, LITELLM_API_KEY)." >&2
  exit 1
fi

# Require key env vars to be set (no empty values)
set -a
source .env 2>/dev/null || true
set +a
if [ -z "${DATABASE_URL}" ]; then
  echo "Error: DATABASE_URL is not set in .env. Need to update .env file." >&2
  exit 1
fi
if [ -z "${LITELLM_MODEL}" ]; then
  echo "Error: LITELLM_MODEL is not set in .env. Need to update .env file." >&2
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "Usage: ./run.sh -c | -u"
  echo "  -c    Interactive console (prompt for text, pipeline animation, result + JSON)"
  echo "  -u    Start service (API + Web UI) at http://localhost:8000"
  echo ""
  echo "For one-off file triage, run manually: python run_triage.py -f path/to/file.txt"
  exit 0
fi

if command -v pipenv &>/dev/null; then
  exec pipenv run python run_triage.py "$@"
else
  exec python run_triage.py "$@"
fi
