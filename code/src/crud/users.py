"""CRUD for users table."""
from sqlalchemy.orm import Session

from src.db.models import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get user by primary key."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    *,
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
) -> User:
    """Insert a new user."""
    obj = User(name=name, email=email, phone=phone)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
