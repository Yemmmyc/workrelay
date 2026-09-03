from __future__ import annotations

from google.cloud import firestore

from app.models.incident import Incident
from app.services.state_store_interface import StateStore


class FirestoreStateStore(StateStore):
    """Firestore-backed implementation of the WorkRelay StateStore."""

    def __init__(
        self,
        client: firestore.Client | None = None,
        collection: str = "incidents",
    ) -> None:
        self.client = client or firestore.Client()
        self.collection = self.client.collection(collection)

    def create(self, incident: Incident) -> Incident:
        document = self.collection.document(incident.id)
        document.create(incident.model_dump(mode="json"))
        return incident

    def get(self, incident_id: str) -> Incident | None:
        document = self.collection.document(incident_id).get()

        if not document.exists:
            return None

        return Incident.model_validate(document.to_dict())

    def update(self, incident: Incident) -> Incident:
        document = self.collection.document(incident.id)

        if not document.get().exists:
            raise KeyError(
                f"Incident {incident.id} does not exist."
            )

        incident.touch()
        document.set(incident.model_dump(mode="json"))
        return incident

    def list_all(self) -> list[Incident]:
        return [
            Incident.model_validate(document.to_dict())
            for document in self.collection.stream()
        ]

    def delete(self, incident_id: str) -> bool:
        document = self.collection.document(incident_id)

        if not document.get().exists:
            return False

        document.delete()
        return True
