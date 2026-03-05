#!/usr/bin/env python3
"""
Content Triage Agent – CLI/UI entry point.
Run as a tool: -f (one-off file), -c (interactive console), -u (web UI).
Shows TRIAGE AGENT banner in lime green; pipeline animations; formatted result + JSON.
"""
import argparse
import json
import sys
from pathlib import Path

# Ensure code/src is on path
_code_dir = Path(__file__).resolve().parent
if str(_code_dir) not in sys.path:
    sys.path.insert(0, str(_code_dir))

# Lime green ANSI
LIME = "\033[92m"
RESET = "\033[0m"
BANNER = f"""
{LIME}
 _____ ____  ___    _    ____ _____      _    ____ _____ _   _ _____ 
 |_   _|  _ \|_ _|  / \  / ___| ____|    / \  / ___| ____| \ | |_   _|
   | | | |_) || |  / _ \| |  _|  _|     / _ \| |  _|  _| |  \| | | |  
   | | |  _ < | | / ___ \ |_| | |___   / ___ \ |_| | |___| |\  | | |  
   |_| |_| \_\___/_/   \_\____|_____| /_/   \_\____|_____|_| \_| |_|
{RESET}
"""

PIPELINE_STEPS = [
    ("validating", "Validating…"),
    ("idempotency", "Checking idempotency…"),
    ("empty_check", "Checking empty/noise…"),
    ("dedup", "Checking dedup…"),
    ("llm", "Calling LLM…"),
    ("routing", "Routing…"),
    ("done", "Done"),
]


def show_banner():
    print(BANNER)


def run_triage_with_progress(
    text: str,
    idempotency_key: str | None = None,
    progress_callback=None,
):
    """Run triage; call progress_callback(step) for each pipeline step. Returns (result_dict, sub_id, msg_id)."""
    from src.db.session import get_session_factory
    from src.services.triage import triage

    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        result_dict, sub_id, msg_id = triage(
            db,
            text,
            idempotency_key=idempotency_key,
            progress_callback=progress_callback,
        )
        return result_dict, sub_id, msg_id
    finally:
        db.close()


def format_result(result: dict) -> str:
    """Human-readable formatted result."""
    lines = [
        "--- Result ---",
        f"Classification: {result.get('classification', '')}",
        f"Actionability:  {result.get('actionability', '')}",
        f"Routing:        {result.get('routing_destination', '')}",
        f"Confidence:     {result.get('confidence', '')}",
        f"Language:       {result.get('detected_language', '')}",
        f"Summary:        {result.get('summary', '')}",
        f"Flags:          {result.get('flags', [])}",
        f"Tags:           {result.get('tags', [])}",
        "----------------",
    ]
    return "\n".join(lines)


def console_pipeline_callback(step: str, use_rich: bool = True):
    """Print pipeline step; if rich available, use spinner."""
    step_label = dict(PIPELINE_STEPS).get(step, step)
    if use_rich:
        try:
            from rich.console import Console
            from rich.spinner import Spinner

            console = Console()
            console.print(f"  [dim]{step_label}[/dim]")
        except ImportError:
            print(f"  {step_label}")
    else:
        print(f"  {step_label}")


def _print_step(step: str):
    label = dict(PIPELINE_STEPS).get(step, step)
    print(f"  {label}")


def mode_file(args):
    """-f path: one-off file, pipeline animation, result + JSON, exit."""
    show_banner()
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    text = path.read_text(encoding="utf-8", errors="replace")
    print("Running triage…")
    result_dict, sub_id, msg_id = run_triage_with_progress(text, progress_callback=_print_step)
    print("\n" + format_result(result_dict))
    print("\nJSON:")
    print(json.dumps({"submission_id": sub_id, "message_id": msg_id, "result": result_dict}, indent=2))


def mode_console(args):
    """-c: interactive loop, banner, pipeline steps, result + JSON, repeat."""
    show_banner()
    print("Enter text to triage (empty line or Ctrl+D to quit).\n")
    while True:
        try:
            line = input("Text> ").strip()
        except EOFError:
            break
        if not line:
            continue
        print("Running triage…")
        result_dict, sub_id, msg_id = run_triage_with_progress(line, progress_callback=_print_step)
        print("\n" + format_result(result_dict))
        print("\nJSON:")
        print(json.dumps({"submission_id": sub_id, "message_id": msg_id, "result": result_dict}, indent=2))
        print()


def mode_ui(args):
    """-u: start web UI (FastAPI + static page with TRIAGE AGENT header, pipeline, result, JSON)."""
    import uvicorn
    # Run the FastAPI app which will serve API + static UI
    # Ensure app mounts static and has UI route
    sys.argv = ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", str(args.port)]
    uvicorn.run("src.main:app", host="0.0.0.0", port=args.port, reload=False)


def main():
    parser = argparse.ArgumentParser(description="Content Triage Agent")
    parser.add_argument("-f", "--file", metavar="PATH", help="One-off: read text from file, triage, print result + JSON, exit")
    parser.add_argument("-c", "--console", action="store_true", help="Interactive console: prompt for text, show pipeline and result, repeat")
    parser.add_argument("-u", "--ui", action="store_true", help="Start web UI (text input, pipeline animation, result + JSON)")
    parser.add_argument("--port", type=int, default=8000, help="Port for -u mode (default 8000)")
    args = parser.parse_args()

    if args.ui:
        mode_ui(args)
        return
    if args.file:
        mode_file(args)
        return
    if args.console:
        mode_console(args)
        return
    # Default: console
    mode_console(args)


if __name__ == "__main__":
    main()
