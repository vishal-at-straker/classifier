"""
Load triage system prompt from YAML (prompts/triage_system.yaml).
Builds a single system prompt string from structured prompt + instructions.
"""
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _prompt_dir(settings: Any) -> Path:
    """Resolve prompts directory (code/prompts or project root prompts/)."""
    p = Path(settings.prompts_dir)
    if p.exists():
        return p
    # When run from code/, prompts_dir may be code/prompts (missing); use project root
    return Path(__file__).resolve().parent.parent.parent.parent / "prompts"


def load_triage_prompt_from_yaml(settings: Any) -> str | None:
    """
    Load prompts/triage_system.yaml and return assembled system prompt string.
    Returns None if YAML missing or invalid.
    """
    if yaml is None:
        return None
    prompt_path = _prompt_dir(settings) / "triage_system.yaml"
    if not prompt_path.exists():
        return None
    try:
        raw = prompt_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except Exception:
        return None
    if not data or "prompt" not in data:
        return None
    prompt = data["prompt"]
    parts = []

    role = prompt.get("role", "").strip()
    if role:
        parts.append(role)

    rules = prompt.get("rules", [])
    if rules:
        parts.append("\nRules:")
        for r in rules:
            parts.append(f"- {r}")

    cats = prompt.get("classification_categories", {})
    if cats:
        parts.append("\nClassification categories:")
        for k, v in (cats.items() if isinstance(cats, dict) else []):
            parts.append(f"{k}: {v}")

    levels = prompt.get("actionability_levels", {})
    if levels:
        parts.append("\nActionability levels:")
        for k, v in (levels.items() if isinstance(levels, dict) else []):
            parts.append(f"{k}: {v}")

    routes = prompt.get("routing_destinations", {})
    if routes:
        parts.append("\nRouting destinations:")
        for k, v in (routes.items() if isinstance(routes, dict) else []):
            parts.append(f"{k}: {v}")

    tool_instr = prompt.get("tool_instruction", "").strip()
    if tool_instr:
        parts.append("\n" + tool_instr)

    return "\n".join(parts) if parts else None
