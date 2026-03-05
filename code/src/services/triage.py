"""
Triage service: empty check, idempotency, dedup by normalized_text,
LLM with tools, tool handler (insert submission, update message, route), fallback.
"""
import json
import logging
from pathlib import Path
from typing import Any, Callable

# Pipeline step names for progress callback
STEP_VALIDATING = "validating"
STEP_IDEMPOTENCY = "idempotency"
STEP_EMPTY_CHECK = "empty_check"
STEP_DEDUP = "dedup"
STEP_LLM = "llm"
STEP_ROUTING = "routing"
STEP_DONE = "done"

from sqlalchemy.orm import Session
import litellm

from src.config import get_settings
from src.crud.submissions import (
    create_submission,
    get_submission_by_normalized_text,
    normalize_text,
)
from src.crud.messages import (
    create_message,
    get_message_by_idempotency_key,
    update_message_submission_id,
)
from src.services.prompt_loader import load_triage_prompt_from_yaml
from src.services.tool_schema import TOOLS
from src.tools.router import route_to_team

logger = logging.getLogger(__name__)


def sanitize_submission_text(text: str | None) -> str:
    """Strip leading/trailing whitespace and collapse internal runs of spaces."""
    if text is None:
        return ""
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())


# Default result when input is empty/noise or LLM fails
DEFAULT_RESULT = {
    "classification": "NOISE",
    "actionability": "NONE",
    "routing_destination": "DISCARD",
    "confidence": "none",
    "detected_language": "en",
    "summary": "Unclassifiable or empty submission.",
    "flags": ["noise"],
    "tags": ["noise"],
}


def _load_system_prompt() -> str:
    """Load triage system prompt from prompts/triage_system.yaml (or .txt fallback)."""
    settings = get_settings()
    from_yaml = load_triage_prompt_from_yaml(settings)
    if from_yaml:
        return from_yaml
    path = Path(settings.prompts_dir) / "triage_system.txt"
    if not path.exists():
        path = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "triage_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "You are a content triage agent. Analyze the text and call submit_triage_result with classification, actionability, routing_destination, confidence, detected_language, summary, flags, tags."


def _is_empty_or_noise(text: str) -> bool:
    """True if submission is empty or clearly noise (no actionable content)."""
    if not text or not isinstance(text, str):
        return True
    t = text.strip()
    if not t:
        return True
    # Only punctuation/whitespace/emoji-like
    if len(t) <= 3 and not t.replace("?", "").replace("!", "").replace(".", "").strip():
        return True
    return False


def _execute_tool_handler(
    db: Session,
    message_id: int,
    text: str,
    normalized: str,
    tool_args: dict[str, Any],
    progress_callback: Callable[[str], None] | None = None,
) -> tuple[dict[str, Any], int]:
    """
    On LLM tool call: insert submission, update message.submission_id, route, return params.
    """
    sub = create_submission(
        db=db,
        text=text,
        normalized_text=normalized,
        classification=tool_args.get("classification", "NOISE"),
        actionability=tool_args.get("actionability", "NONE"),
        routing_destination=tool_args.get("routing_destination", "DISCARD"),
        confidence=tool_args.get("confidence", "none"),
        detected_language=tool_args.get("detected_language", "en"),
        summary=tool_args.get("summary", ""),
        flags=tool_args.get("flags") or [],
        tags=tool_args.get("tags") or [],
    )
    update_message_submission_id(db, message_id, sub.id)
    if progress_callback:
        progress_callback(STEP_ROUTING)
    route_to_team(sub.id, sub.routing_destination, tool_args)
    return (
        {
            "classification": sub.classification,
            "actionability": sub.actionability,
            "routing_destination": sub.routing_destination,
            "confidence": sub.confidence,
            "detected_language": sub.detected_language,
            "summary": sub.summary,
            "flags": sub.flags,
            "tags": sub.tags,
        },
        sub.id,
    )


def _call_llm(text: str) -> dict[str, Any] | None:
    """
    Call LiteLLM with tools. Return tool call args if submit_triage_result was called, else None.
    """
    settings = get_settings()
    system_prompt = _load_system_prompt()
    try:
        completion_kw: dict[str, Any] = {
            "model": settings.litellm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this submission and call the tool with the triage result:\n\n{text}"},
            ],
            "tools": TOOLS,
            "tool_choice": {"type": "function", "function": {"name": "submit_triage_result"}},
            "temperature": settings.litellm_temperature,
        }
        if settings.litellm_api_base:
            completion_kw["api_base"] = settings.litellm_api_base
        if settings.litellm_api_key:
            completion_kw["api_key"] = settings.litellm_api_key
        if settings.custom_llm_provider:
            completion_kw["custom_llm_provider"] = settings.custom_llm_provider
        if settings.litellm_api_version:
            completion_kw["api_version"] = settings.litellm_api_version
        response = litellm.completion(**completion_kw)
    except Exception as e:
        logger.warning("LLM call failed: %s", e)
        return None

    choice = response.choices[0] if response.choices else None
    if not choice or not getattr(choice, "message", None):
        return None
    msg = choice.message
    tool_calls = getattr(msg, "tool_calls", None) or []
    for tc in tool_calls:
        name = getattr(tc, "function", None) and getattr(tc.function, "name", None)
        if name == "submit_triage_result":
            args_str = getattr(tc.function, "arguments", None) or "{}"
            try:
                return json.loads(args_str)
            except json.JSONDecodeError:
                logger.warning("Invalid tool args JSON: %s", args_str)
                return None
    return None


def triage(
    db: Session,
    text: str,
    *,
    idempotency_key: str | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> tuple[dict[str, Any], int | None, int | None]:
    """
    Run triage on text. Returns (result_dict, submission_id, message_id).
    - If idempotency_key and existing message: return cached submission result.
    - If empty/noise: return default result, optionally create message/submission.
    - If normalized_text seen: return cached submission, update message.
    - Else: create message, call LLM with tools, run tool handler, return params.
    """
    def _step(name: str) -> None:
        if progress_callback:
            progress_callback(name)

    text = sanitize_submission_text(text)
    settings = get_settings()
    _step(STEP_VALIDATING)
    # Truncate if needed
    if len(text) > settings.submission_max_length:
        text = text[: settings.submission_max_length]
    normalized = normalize_text(text)

    _step(STEP_IDEMPOTENCY)
    # Idempotency: existing message with this key
    if idempotency_key:
        existing_msg = get_message_by_idempotency_key(db, idempotency_key)
        if existing_msg and existing_msg.submission_id:
            sub = existing_msg.submission
            _step(STEP_DONE)
            return (
                {
                    "classification": sub.classification,
                    "actionability": sub.actionability,
                    "routing_destination": sub.routing_destination,
                    "confidence": sub.confidence,
                    "detected_language": sub.detected_language,
                    "summary": sub.summary,
                    "flags": sub.flags,
                    "tags": sub.tags,
                },
                sub.id,
                existing_msg.id,
            )
        if existing_msg:
            # Message exists but no submission yet; we'll create/attach below (use this message_id)
            pass

    _step(STEP_EMPTY_CHECK)
    # Empty or noise: return default, optionally insert message + submission
    if _is_empty_or_noise(text):
        default_sub = create_submission(
            db=db,
            text=text,
            normalized_text=normalized or "(empty)",
            classification="EMPTY" if not text or not text.strip() else "NOISE",
            actionability="NONE",
            routing_destination="DISCARD",
            confidence="none",
            detected_language="en",
            summary="Empty or unclassifiable submission.",
            flags=["empty"] if not text or not text.strip() else ["noise"],
            tags=["empty"] if not text or not text.strip() else ["noise"],
        )
        msg = create_message(
            db,
            text,
            submission_id=default_sub.id,
            idempotency_key=idempotency_key,
        )
        _step(STEP_DONE)
        return (
            {
                "classification": default_sub.classification,
                "actionability": default_sub.actionability,
                "routing_destination": default_sub.routing_destination,
                "confidence": default_sub.confidence,
                "detected_language": default_sub.detected_language,
                "summary": default_sub.summary,
                "flags": default_sub.flags,
                "tags": default_sub.tags,
            },
            default_sub.id,
            msg.id,
        )

    _step(STEP_DEDUP)
    # Dedup: already have submission for this normalized text
    existing_sub = get_submission_by_normalized_text(db, normalized)
    if existing_sub:
        if idempotency_key:
            existing_msg = get_message_by_idempotency_key(db, idempotency_key)
            if existing_msg:
                update_message_submission_id(db, existing_msg.id, existing_sub.id)
                _step(STEP_DONE)
                return (
                    {
                        "classification": existing_sub.classification,
                        "actionability": existing_sub.actionability,
                        "routing_destination": existing_sub.routing_destination,
                        "confidence": existing_sub.confidence,
                        "detected_language": existing_sub.detected_language,
                        "summary": existing_sub.summary,
                        "flags": existing_sub.flags,
                        "tags": existing_sub.tags,
                    },
                    existing_sub.id,
                    existing_msg.id,
                )
        msg = create_message(
            db,
            text,
            submission_id=existing_sub.id,
            idempotency_key=idempotency_key,
        )
        _step(STEP_DONE)
        return (
            {
                "classification": existing_sub.classification,
                "actionability": existing_sub.actionability,
                "routing_destination": existing_sub.routing_destination,
                "confidence": existing_sub.confidence,
                "detected_language": existing_sub.detected_language,
                "summary": existing_sub.summary,
                "flags": existing_sub.flags,
                "tags": existing_sub.tags,
            },
            existing_sub.id,
            msg.id,
        )

    # New submission: create message first (no submission_id yet)
    if idempotency_key:
        existing_msg = get_message_by_idempotency_key(db, idempotency_key)
        if existing_msg:
            message = existing_msg
        else:
            message = create_message(db, text, idempotency_key=idempotency_key)
    else:
        message = create_message(db, text)

    _step(STEP_LLM)
    # Call LLM with tools
    tool_args = _call_llm(text)
    if not tool_args:
        # Fallback: insert default submission and attach to message
        default_sub = create_submission(
            db=db,
            text=text,
            normalized_text=normalized,
            classification=DEFAULT_RESULT["classification"],
            actionability=DEFAULT_RESULT["actionability"],
            routing_destination=DEFAULT_RESULT["routing_destination"],
            confidence=DEFAULT_RESULT["confidence"],
            detected_language=DEFAULT_RESULT["detected_language"],
            summary=DEFAULT_RESULT["summary"],
            flags=DEFAULT_RESULT["flags"],
            tags=DEFAULT_RESULT["tags"],
        )
        update_message_submission_id(db, message.id, default_sub.id)
        _step(STEP_DONE)
        return (
            dict(DEFAULT_RESULT),
            default_sub.id,
            message.id,
        )

    # Execute tool handler: insert submission, update message, route
    result, submission_id = _execute_tool_handler(
        db, message.id, text, normalized, tool_args, progress_callback
    )
    _step(STEP_DONE)
    return (result, submission_id, message.id)