"""CRUD for teams table."""
from sqlalchemy.orm import Session

from src.db.models import Team


def get_team_by_id(db: Session, team_id: int) -> Team | None:
    """Get team by primary key."""
    return db.query(Team).filter(Team.id == team_id).first()


def get_team_by_name(db: Session, name: str) -> Team | None:
    """Get team by name (e.g. ENGINEERING)."""
    return db.query(Team).filter(Team.name == name).first()


def get_all_teams(db: Session) -> list[Team]:
    """Return all teams."""
    return db.query(Team).all()
