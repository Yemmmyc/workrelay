from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from app.models.incident import Incident


class LocalStateStore:
    """
    Local JSON-backed state store for WorkRelay development.

    This interface is intentionally isolated from the workflow engine so
    that it can later be replaced by a Firestore-backed implementation
    without changing workflow logic.
    """

    def __init__(self, path: str | Path = "data/incidents.json") -> None:
        self.path = Path(path)
        self._lock = Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _read_all(self) -> dict[str, dict]:
        try:
            content = self.path.read_text(encoding="utf-8")

            if not content.strip():
                return {}

            return json.loads(content)

        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_all(self, records: dict[str, dict]) -> None:
        self.path.write_text(
            json.dumps(records, indent=2),
            encoding="utf-8",
        )

    def create(self, incident: Incident) -> Incident:
        with self._lock:
            records = self._read_all()

            if incident.id in records:
                raise ValueError(
                    f"Incident {incident.id} already exists."
                )

            records[incident.id] = incident.model_dump(mode="json")
            self._write_all(records)

        return incident

    def get(self, incident_id: str) -> Incident | None:
        with self._lock:
            records = self._read_all()

        record = records.get(incident_id)

        if record is None:
            return None

        return Incident.model_validate(record)

    def update(self, incident: Incident) -> Incident:
        with self._lock:
            records = self._read_all()

            if incident.id not in records:
                raise KeyError(
                    f"Incident {incident.id} does not exist."
                )

            incident.touch()
            records[incident.id] = incident.model_dump(mode="json")
            self._write_all(records)

        return incident

    def list_all(self) -> list[Incident]:
        with self._lock:
            records = self._read_all()

        return [
            Incident.model_validate(record)
            for record in records.values()
        ]

    def delete(self, incident_id: str) -> bool:
        with self._lock:
            records = self._read_all()

            if incident_id not in records:
                return False

            del records[incident_id]
            self._write_all(records)

        return True
