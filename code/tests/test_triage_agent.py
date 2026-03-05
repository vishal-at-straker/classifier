"""Tests for triage agent: tool call args, fallback when no tool call."""
import json
from unittest.mock import patch, MagicMock

import pytest

from src.crud.submissions import normalize_text
from src.services.triage import (
    triage,
    DEFAULT_RESULT,
    STEP_DONE,
)


@pytest.fixture
def mock_litellm_tool_call():
    """LiteLLM returns a tool call with submit_triage_result args."""
    def _make_response(tool_args: dict):
        choice = MagicMock()
        choice.message = MagicMock()
        func = MagicMock()
        func.name = "submit_triage_result"
        func.arguments = json.dumps(tool_args)
        choice.message.tool_calls = [MagicMock(function=func)]
        response = MagicMock()
        response.choices = [choice]
        return response

    return _make_response


def test_normalize_text():
    assert normalize_text("  Hello   World  ") == "hello world"
    assert normalize_text("") == ""
    assert normalize_text("UPPER") == "upper"


def test_triage_empty_returns_EMPTY(db_session):
    result_dict, sub_id, msg_id = triage(db_session, "")
    assert result_dict["classification"] == "EMPTY"
    assert result_dict["actionability"] == "NONE"
    assert result_dict["routing_destination"] == "DISCARD"
    assert sub_id is not None
    assert msg_id is not None


def test_triage_noise_returns_NOISE(db_session):
    result_dict, sub_id, msg_id = triage(db_session, "?????")
    assert result_dict["classification"] == "NOISE"
    assert result_dict["routing_destination"] == "DISCARD"


def test_triage_llm_tool_call_stored(mock_litellm_tool_call, db_session):
    tool_args = {
        "classification": "BUG_REPORT",
        "actionability": "HIGH",
        "routing_destination": "ENGINEERING",
        "confidence": "high",
        "detected_language": "en",
        "summary": "Login button broken on mobile Safari.",
        "flags": ["urgent"],
        "tags": ["bug"],
    }
    with patch("src.services.triage.litellm.completion", return_value=mock_litellm_tool_call(tool_args)):
        result_dict, sub_id, msg_id = triage(db_session, "The login button doesn't work on mobile Safari")
    assert result_dict["classification"] == "BUG_REPORT"
    assert result_dict["routing_destination"] == "ENGINEERING"
    assert result_dict["summary"] == "Login button broken on mobile Safari."
    assert sub_id is not None
    assert msg_id is not None


def test_triage_llm_failure_returns_default(db_session):
    with patch("src.services.triage.litellm.completion", side_effect=Exception("API error")):
        result_dict, sub_id, msg_id = triage(db_session, "Some real text here")
    assert result_dict["classification"] == DEFAULT_RESULT["classification"]
    assert result_dict["routing_destination"] == "DISCARD"
    assert sub_id is not None


def test_triage_llm_no_tool_call_returns_default(db_session):
    choice = MagicMock()
    choice.message = MagicMock()
    choice.message.tool_calls = []
    response = MagicMock()
    response.choices = [choice]
    with patch("src.services.triage.litellm.completion", return_value=response):
        result_dict, sub_id, msg_id = triage(db_session, "Some text")
    assert result_dict["classification"] == DEFAULT_RESULT["classification"]
