"""CRUD for submissions table."""
from sqlalchemy.orm import Session

from src.db.models import Submission


def normalize_text(text: str) -> str:
    """Normalize for dedup: strip, lower, collapse whitespace."""
    if not text or not isinstance(text, str):
        return ""
    return " ".join(text.strip().lower().split())


def create_submission(
    db: Session,
    text: str,
    normalized_text: str,
    classification: str,
    actionability: str,
    routing_destination: str,
    confidence: str,
    detected_language: str,
    summary: str,
    flags: list,
    tags: list,
) -> Submission:
    """Insert a new submission."""
    obj = Submission(
        text=text,
        normalized_text=normalized_text,
        classification=classification,
        actionability=actionability,
        routing_destination=routing_destination,
        confidence=confidence,
        detected_language=detected_language,
        summary=summary,
        flags=flags or [],
        tags=tags or [],
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_submission_by_normalized_text(
    db: Session, normalized_text: str
) -> Submission | None:
    """Find submission by normalized_text for dedup."""
    return (
        db.query(Submission)
        .filter(Submission.normalized_text == normalized_text)
        .first()
    )


def get_submission_by_id(db: Session, submission_id: int) -> Submission | None:
    """Get submission by primary key."""
    return db.query(Submission).filter(Submission.id == submission_id).first()


def list_submissions_paginated(
    db: Session,
    page: int = 1,
    per_page: int = 10,
) -> tuple[list[Submission], int]:
    """
    List submissions in descending order (newest first). Returns (items, total_count).
    """
    total = db.query(Submission).count()
    offset = max(0, (page - 1) * per_page)
    items = (
        db.query(Submission)
        .order_by(Submission.id.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return items, total
