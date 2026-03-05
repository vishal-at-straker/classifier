"""Pydantic schemas for submission API."""
from pydantic import BaseModel, Field


class SubmissionRequest(BaseModel):
    """Request body for POST /submissions."""

    text: str = Field(..., min_length=0, max_length=100_000)
    idempotency_key: str | None = Field(None, max_length=256)


class TriageResult(BaseModel):
    """Triage result (classification, routing, etc.)."""

    classification: str
    actionability: str
    routing_destination: str
    confidence: str
    detected_language: str
    summary: str
    flags: list[str]
    tags: list[str]


class SubmissionResponse(BaseModel):
    """Response for POST /submissions."""

    submission_id: int | None
    message_id: int | None
    result: TriageResult
