"""Seed teams and placeholder users. Idempotent: safe to run multiple times."""
import sys
from pathlib import Path

# Ensure code/src is on path when run as script
_code_dir = Path(__file__).resolve().parent.parent.parent
if str(_code_dir) not in sys.path:
    sys.path.insert(0, str(_code_dir))

from src.db.session import init_db, get_session_factory
from src.db.models import Team, User


TEAMS = [
    {"name": "ENGINEERING", "email": "engineering@example.com"},
    {"name": "CUSTOMER_SUPPORT", "email": "support@example.com"},
    {"name": "PRODUCT_MANAGEMENT", "email": "product@example.com"},
    {"name": "FEEDBACK", "email": "feedback@example.com"},
    {"name": "ESCALATION", "email": "escalation@example.com"},
    {"name": "LOCALIZATION", "email": "localization@example.com"},
    {"name": "DISCARD", "email": "discard@example.com"},
]

USERS = [
    {"name": "Placeholder User 1", "email": "user1@example.com"},
    {"name": "Placeholder User 2", "email": "user2@example.com"},
]


def run_seed():
    init_db()
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        for t in TEAMS:
            existing = db.query(Team).filter(Team.name == t["name"]).first()
            if not existing:
                db.add(Team(name=t["name"], email=t["email"]))
        for u in USERS:
            existing = (
                db.query(User)
                .filter(User.email == u["email"])
                .first()
            )
            if not existing:
                db.add(User(name=u["name"], email=u["email"]))
        db.commit()
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
