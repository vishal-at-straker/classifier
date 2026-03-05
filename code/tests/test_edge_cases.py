"""Edge cases: empty, long input, invalid UTF-8, LLM error, DB behavior."""
from unittest.mock import patch

import pytest

from src.services.triage import triage, DEFAULT_RESULT


def test_empty_string_returns_EMPTY(db_session):
    result, sub_id, msg_id = triage(db_session, "")
    assert result["classification"] == "EMPTY"
    assert result["routing_destination"] == "DISCARD"


def test_whitespace_only_returns_EMPTY(db_session):
    result, _, _ = triage(db_session, "   \n\t  ")
    assert result["classification"] == "EMPTY"


def test_very_long_input_truncated(db_session):
    from src.config import get_settings
    settings = get_settings()
    long_text = "a" * (settings.submission_max_length + 1000)
    result, sub_id, msg_id = triage(db_session, long_text)
    assert result is not None
    assert sub_id is not None


def test_llm_returns_invalid_json_returns_default(db_session):
    choice = __import__("unittest.mock").mock.MagicMock()
    choice.message = __import__("unittest.mock").mock.MagicMock()
    choice.message.tool_calls = [
        __import__("unittest.mock").mock.MagicMock(
            function=__import__("unittest.mock").mock.MagicMock(
                name="submit_triage_result",
                arguments="not valid json {{{",
            )
        )
    ]
    response = __import__("unittest.mock").mock.MagicMock()
    response.choices = [choice]
    with patch("src.services.triage.litellm.completion", return_value=response):
        result, sub_id, msg_id = triage(db_session, "Real user text here")
    assert result["classification"] == DEFAULT_RESULT["classification"]
    assert sub_id is not None


def test_idempotency_same_key_returns_same_result(db_session):
    from unittest.mock import MagicMock
    import json
    tool_args = {
        "classification": "FEATURE_REQUEST",
        "actionability": "MEDIUM",
        "routing_destination": "PRODUCT_MANAGEMENT",
        "confidence": "high",
        "detected_language": "en",
        "summary": "Feature request.",
        "flags": [],
        "tags": ["feature"],
    }
    def mock_completion(*args, **kwargs):
        choice = MagicMock()
        choice.message = MagicMock()
        func = MagicMock()
        func.name = "submit_triage_result"
        func.arguments = json.dumps(tool_args)
        choice.message.tool_calls = [MagicMock(function=func)]
        r = MagicMock()
        r.choices = [choice]
        return r
    key = "idem-123"
    with patch("src.services.triage.litellm.completion", side_effect=mock_completion) as m:
        r1, s1, msg1 = triage(db_session, "Add dark mode", idempotency_key=key)
        r2, s2, msg2 = triage(db_session, "Add dark mode", idempotency_key=key)
    assert m.call_count == 1
    assert r1["classification"] == "FEATURE_REQUEST"
    assert r2["classification"] == "FEATURE_REQUEST"
    assert s1 == s2
    assert msg1 == msg2
