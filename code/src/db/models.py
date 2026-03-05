"""SQLAlchemy models for submissions, teams, users, messages."""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class Submission(Base):
    """Triage result for a piece of content. Dedup by normalized_text."""

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=False, index=True, unique=True)
    classification = Column(String(64), nullable=False)
    actionability = Column(String(32), nullable=False)
    routing_destination = Column(String(64), nullable=False)
    confidence = Column(String(32), nullable=False)
    detected_language = Column(String(8), nullable=False)
    summary = Column(Text, nullable=False)
    flags = Column(JSON, nullable=False)
    tags = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    messages = relationship("Message", back_populates="submission")


class Team(Base):
    """Team for routing (e.g. ENGINEERING, CUSTOMER_SUPPORT)."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=True)
    phone = Column(String(64), nullable=True)
    slack_channel = Column(String(128), nullable=True)
    slack_channel_id = Column(String(64), nullable=True)
    slack_channel_name = Column(String(128), nullable=True)
    slack_channel_type = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)


class User(Base):
    """User (e.g. for messages)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True)
    phone = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)


class Message(Base):
    """Incoming message; links to submission after triage."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(
        Integer, ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True
    )
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    message = Column(Text, nullable=False)
    idempotency_key = Column(String(256), nullable=True, unique=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    submission = relationship("Submission", back_populates="messages")
