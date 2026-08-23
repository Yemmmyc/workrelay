from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    CLASSIFYING = "CLASSIFYING"
    INVESTIGATING = "INVESTIGATING"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class IncidentAction(BaseModel):
    name: str
    description: str = ""
    status: ActionStatus = ActionStatus.PENDING
    result: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class Incident(BaseModel):
    id: str = Field(default_factory=lambda: f"INC-{uuid4().hex[:8].upper()}")
    title: str
    description: str
    service: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.OPEN

    current_step: str = "incident_received"
    workflow: str | None = None

    actions: list[IncidentAction] = Field(default_factory=list)

    resolution: str | None = None
    escalation_reason: str | None = None

    retry_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def touch(self) -> None:
        """Update the incident modification timestamp."""
        self.updated_at = datetime.now(timezone.utc)
