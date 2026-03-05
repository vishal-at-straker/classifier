"""Dedup: same normalized_text returns cached submission; no second LLM call."""
from unittest.mock import patch, MagicMock
import json

import pytest

from src.services.triage import triage


@pytest.fixture
def mock_llm_bug_report():
    def _response(*args, **kwargs):
        choice = MagicMock()
        choice.message = MagicMock()
        func = MagicMock()
        func.name = "submit_triage_result"
        func.arguments = json.dumps({
            "classification": "BUG_REPORT",
            "actionability": "HIGH",
            "routing_destination": "ENGINEERING",
            "confidence": "high",
            "detected_language": "en",
            "summary": "Bug report.",
            "flags": ["urgent"],
            "tags": ["bug"],
        })
        choice.message.tool_calls = [MagicMock(function=func)]
        resp = MagicMock()
        resp.choices = [choice]
        return resp
    return _response


def test_dedup_same_text_returns_cached_no_second_llm(db_session, mock_llm_bug_report):
    text = "The login button doesn't work on mobile Safari"
    with patch("src.services.triage.litellm.completion", side_effect=mock_llm_bug_report) as m:
        result1, sub_id1, msg_id1 = triage(db_session, text)
        result2, sub_id2, msg_id2 = triage(db_session, text)
    assert m.call_count == 1
    assert result1["classification"] == "BUG_REPORT"
    assert result2["classification"] == "BUG_REPORT"
    assert sub_id1 == sub_id2


def test_dedup_normalized_same_returns_cached(db_session, mock_llm_bug_report):
    with patch("src.services.triage.litellm.completion", side_effect=mock_llm_bug_report) as m:
        result1, sub_id1, _ = triage(db_session, "Hello World")
        result2, sub_id2, _ = triage(db_session, "  hello   world  ")
    assert m.call_count == 1
    assert sub_id1 == sub_id2
    assert result1["classification"] == result2["classification"]
