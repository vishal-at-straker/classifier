# Content Triage Agent

A content triage service that classifies text submissions via an LLM (LiteLLM), deduplicates by normalized text, persists to SQLite, and routes to team endpoints. Includes a TRIAGE AGENT CLI/UI with pipeline animations and formatted JSON output.

## Features

- **Classification**: BUG_REPORT, FEATURE_REQUEST, COMPLAINT, POSITIVE_FEEDBACK, SUPPORT_REQUEST, CANCELLATION, NON_ENGLISH, NOISE, EMPTY
- **Actionability**: HIGH, MEDIUM, LOW, NONE
- **Routing**: ENGINEERING, CUSTOMER_SUPPORT, PRODUCT_MANAGEMENT, FEEDBACK, ESCALATION, LOCALIZATION, DISCARD
- **LLM tool-based**: Structured output via `submit_triage_result` tool (no free-form JSON parsing)
- **Dedup**: Same normalized text returns cached result; no duplicate LLM calls
- **Idempotency**: Optional `idempotency_key` returns cached result when present
- **Rate limiting**: Per-IP limit on `POST /submissions`
- **Observability**: Request/correlation ID (X-Request-ID), structured logging
- **Input sanitization**: Submission text is stripped of leading/trailing whitespace and internal runs of spaces before triage
- **Resilience**: Database failures return 503 with a safe message; no internal details leaked

## How to run

All steps are from the **`code`** directory. Open a terminal and `cd code` first.

### Prerequisites

- Python 3.10+
- pip or pipenv

### 1. Setup (install and seed)

Run once to install dependencies and seed the database:

```bash
cd code
./setup.sh
```

### 2. Environment

Copy `.env.example` to `.env` and set values (see [Environment variables](#environment-variables)). Do not commit `.env` or secrets.

```bash
cd code
cp .env.example .env
# Edit .env and set at least DATABASE_URL, LITELLM_MODEL, and LITELLM_API_KEY (or your provider key).
```

### 3. Run

Start the service or the console with the bash script. **`run.sh` checks that `.env` exists and that required env variables are set** (e.g. `DATABASE_URL`, `LITELLM_MODEL`). If not, it exits with an error asking you to update the `.env` file.

```bash
cd code
./run.sh -u    # Start the service (API + Web UI). Then open http://localhost:8000
./run.sh -c    # Run interactive console (prompt for text, pipeline animation, result + JSON)
```

- **`./run.sh -u`**: Serves API + Web UI at http://localhost:8000 (pipeline animation, formatted result, JSON; multiple submissions).
- **`./run.sh -c`**: Interactive TRIAGE AGENT console (lime green banner); multiple submissions; pipeline steps and formatted result + JSON.
- **File mode (`-f`)**: Run manually when you want to triage a file once:
  ```bash
  cd code
  python run_triage.py -f path/to/file.txt
  ```

### Manual: API server only

```bash
cd code
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- API: [http://localhost:8000](http://localhost:8000)  
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)  
- UI: [http://localhost:8000/](http://localhost:8000/)

## How to test

```bash
cd code
PYTHONPATH=. pytest tests/ -v
```

Tests cover: triage agent (tool call, fallback), dedup by normalized text, edge cases (empty, long input, invalid JSON, idempotency), rate limit (429 after N requests).

## Environment variables

Documented in `.env.example`. Summary:


| Variable                    | Description                                                         |
| --------------------------- | ------------------------------------------------------------------- |
| `DATABASE_URL`              | SQLite connection string (default: `sqlite:///./classifier.db`)     |
| `LITELLM_MODEL`             | Model for LiteLLM (e.g. `gpt-4o-mini`)                              |
| `LITELLM_API_KEY`           | Provider API key (do not commit; use secret manager in prod)        |
| `LITELLM_API_BASE`          | Optional custom API base URL (e.g. OpenAI-compatible endpoint)      |
| `CUSTOM_LLM_PROVIDER`       | LiteLLM provider (default: `openai`)                                |
| `LITELLM_TEMPERATURE`       | Model temperature (default: `0`)                                   |
| `LITELLM_API_VERSION`       | Optional API version when using custom provider                     |
| `LOG_LEVEL`                 | e.g. `INFO`, `DEBUG`                                                |
| `ENVIRONMENT`               | `dev`, `test`, or `prod`                                            |
| `RATE_LIMIT_REQUESTS`       | Max requests per window (default: 60)                               |
| `RATE_LIMIT_WINDOW_SECONDS` | Window in seconds (default: 60)                                     |
| `SUBMISSION_MAX_LENGTH`     | Max submission length (default: 10000)                             |
| `TEAM_*_URL`                | Optional team API base URLs                                         |


## API

- **POST /submissions**  
Body: `{ "text": "…", "idempotency_key": "optional-key" }`  
Returns: `{ "submission_id", "message_id", "result": { "classification", "actionability", "routing_destination", "confidence", "detected_language", "summary", "flags", "tags" } }`

## Project layout

```
classifier/
├── code/
│   ├── src/          # main, config, db, crud, services, routers, schemas, tools
│   ├── static/       # Web UI for -u mode
│   ├── tests/
│   ├── setup.sh      # First-time: ./setup.sh (install + seed)
│   ├── run.sh        # After .env: ./run.sh -c (console) or ./run.sh -u (UI)
│   └── run_triage.py # CLI/UI entry (-f, -c, -u)
├── prompts/          # triage_system.yaml (prompt + instructions), planning_and_spec.md
├── docs/             # overview.md, changelog.md
├── Pipfile
├── requirements.txt
├── .env.example
└── README.md
```

## Contributing

1. Run tests before submitting changes.
2. Follow existing code style and structure.
3. Document new env vars in `.env.example`.

## Reporting bugs / suggesting features

Open an issue with a clear description and steps to reproduce (for bugs).