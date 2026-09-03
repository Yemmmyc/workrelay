from app.models.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.services.firestore_state_store import FirestoreStateStore


class FakeDocumentSnapshot:
    def __init__(self, data=None, exists=True):
        self._data = data
        self.exists = exists

    def to_dict(self):
        return self._data


class FakeDocument:
    def __init__(self, documents, document_id):
        self.documents = documents
        self.document_id = document_id

    def create(self, data):
        if self.document_id in self.documents:
            raise ValueError("already exists")
        self.documents[self.document_id] = data

    def get(self):
        if self.document_id not in self.documents:
            return FakeDocumentSnapshot(exists=False)

        return FakeDocumentSnapshot(
            self.documents[self.document_id],
            exists=True,
        )

    def set(self, data):
        self.documents[self.document_id] = data

    def delete(self):
        self.documents.pop(self.document_id, None)


class FakeCollection:
    def __init__(self):
        self.documents = {}

    def document(self, document_id):
        return FakeDocument(self.documents, document_id)

    def stream(self):
        return [
            FakeDocumentSnapshot(data, exists=True)
            for data in self.documents.values()
        ]


class FakeClient:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = FakeCollection()

        return self.collections[name]


def make_incident():
    return Incident(
        title="Payment API failure",
        description="Payment requests are failing.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
    )


def test_firestore_store_create_and_get():
    client = FakeClient()
    store = FirestoreStateStore(client=client)

    incident = make_incident()

    store.create(incident)

    result = store.get(incident.id)

    assert result is not None
    assert result.id == incident.id
    assert result.title == incident.title
    assert result.service == incident.service


def test_firestore_store_update():
    client = FakeClient()
    store = FirestoreStateStore(client=client)

    incident = make_incident()
    store.create(incident)

    incident.status = IncidentStatus.INVESTIGATING
    store.update(incident)

    result = store.get(incident.id)

    assert result is not None
    assert result.status.value == "INVESTIGATING"


def test_firestore_store_list_all():
    client = FakeClient()
    store = FirestoreStateStore(client=client)

    first = make_incident()
    second = make_incident()

    store.create(first)
    store.create(second)

    results = store.list_all()

    assert len(results) == 2
    assert {item.id for item in results} == {first.id, second.id}


def test_firestore_store_delete():
    client = FakeClient()
    store = FirestoreStateStore(client=client)

    incident = make_incident()
    store.create(incident)

    assert store.delete(incident.id) is True
    assert store.get(incident.id) is None
    assert store.delete(incident.id) is False
