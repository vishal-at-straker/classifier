"""Route submission to the appropriate team. Stub: log only; later HTTP to team URLs."""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Map routing_destination to team name for logging
DESTINATION_TO_TEAM = {
    "ENGINEERING": "ENGINEERING",
    "CUSTOMER_SUPPORT": "CUSTOMER_SUPPORT",
    "PRODUCT_MANAGEMENT": "PRODUCT_MANAGEMENT",
    "FEEDBACK": "FEEDBACK",
    "ESCALATION": "ESCALATION",
    "LOCALIZATION": "LOCALIZATION",
    "DISCARD": "DISCARD",
}


def route_to_team(
    submission_id: int,
    routing_destination: str,
    payload: dict[str, Any],
) -> None:
    """
    Route a submission to the team for the given destination.
    Stub: log only. Later: HTTP POST to team URL from config.
    """
    team = DESTINATION_TO_TEAM.get(
        routing_destination, routing_destination
    )
    logger.info(
        "Routed to %s (submission_id=%s)",
        team,
        submission_id,
    )
    # TODO: if settings.team_*_url, POST payload to that URL
