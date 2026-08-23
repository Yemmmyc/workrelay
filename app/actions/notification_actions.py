from __future__ import annotations

from datetime import datetime, timezone

from app.models.incident import Incident


def record_escalation(
    incident: Incident,
    reason: str,
) -> str:
    """
    Record a local escalation event.

    The production implementation can later publish this event through
    Pub/Sub and notify an appropriate operational channel.
    """

    incident.escalation_reason = reason

    incident.metadata.setdefault("notifications", []).append(
        {
            "type": "escalation",
            "message": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    return f"Incident {incident.id} escalated: {reason}"
