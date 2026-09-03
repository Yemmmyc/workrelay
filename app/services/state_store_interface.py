from __future__ import annotations

from typing import Protocol

from app.models.incident import Incident


class StateStore(Protocol):
    """Storage contract used by the WorkRelay workflow engine."""

    def create(self, incident: Incident) -> Incident:
        ...

    def get(self, incident_id: str) -> Incident | None:
        ...

    def update(self, incident: Incident) -> Incident:
        ...

    def list_all(self) -> list[Incident]:
        ...

    def delete(self, incident_id: str) -> bool:
        ...
