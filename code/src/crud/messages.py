"""CRUD for messages table."""
from sqlalchemy.orm import Session

from src.db.models import Message


def create_message(
    db: Session,
    message_text: str,
    *,
    submission_id: int | None = None,
    team_id: int | None = None,
    user_id: int | None = None,
    idempotency_key: str | None = None,
) -> Message:
    """Insert a new message."""
    obj = Message(
        message=message_text,
        submission_id=submission_id,
        team_id=team_id,
        user_id=user_id,
        idempotency_key=idempotency_key,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_message_by_id(db: Session, message_id: int) -> Message | None:
    """Get message by primary key."""
    return db.query(Message).filter(Message.id == message_id).first()


def get_message_by_idempotency_key(
    db: Session, idempotency_key: str
) -> Message | None:
    """Find message by idempotency_key."""
    return (
        db.query(Message)
        .filter(Message.idempotency_key == idempotency_key)
        .first()
    )


def update_message_submission_id(
    db: Session, message_id: int, submission_id: int
) -> Message | None:
    """Set submission_id on a message."""
    msg = get_message_by_id(db, message_id)
    if msg is None:
        return None
    msg.submission_id = submission_id
    db.commit()
    db.refresh(msg)
    return msg
