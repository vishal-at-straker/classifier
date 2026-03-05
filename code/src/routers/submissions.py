"""POST /submissions: validate, call triage service, return JSON."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db.session import get_session_factory
from src.schemas.submission import SubmissionRequest, SubmissionResponse, TriageResult
from src.services.triage import triage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions", tags=["submissions"])


def get_db():
    """Yield a DB session for the request."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=SubmissionResponse)
def post_submission(
    request: Request,
    body: SubmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Submit text for triage. Returns classification, routing, and IDs.
    Optional idempotency_key returns cached result if present.
    """
    settings = request.app.state.settings
    # Sanitize: strip leading/trailing and collapse internal spaces
    text = " ".join((body.text or "").strip().split())
    if len(text) > settings.submission_max_length:
        raise HTTPException(
            400,
            detail=f"Text exceeds max length {settings.submission_max_length}",
        )
    try:
        result_dict, submission_id, message_id = triage(
            db,
            text,
            idempotency_key=body.idempotency_key,
        )
    except SQLAlchemyError as e:
        logger.exception("Database error during triage")
        raise HTTPException(
            503,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e
    return SubmissionResponse(
        submission_id=submission_id,
        message_id=message_id,
        result=TriageResult(**result_dict),
    )
