from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.workflows.registry import select_workflow
from app.services.state_store import LocalStateStore


def test_workflow_selection():
    assert (
        select_workflow(IncidentSeverity.LOW).name
        == "standard_incident"
    )

    assert (
        select_workflow(IncidentSeverity.MEDIUM).name
        == "standard_incident"
    )

    assert (
        select_workflow(IncidentSeverity.HIGH).name
        == "high_severity_incident"
    )

    assert (
        select_workflow(IncidentSeverity.CRITICAL).name
        == "critical_incident"
    )


def test_state_store_create_and_get(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Payment API failure",
        description="Payment requests are returning HTTP 500 errors.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
    )

    store.create(incident)

    retrieved = store.get(incident.id)

    assert retrieved is not None
    assert retrieved.id == incident.id
    assert retrieved.service == "payment-api"
    assert retrieved.severity == IncidentSeverity.HIGH


def test_state_store_update(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Database latency",
        description="Database response time is elevated.",
        service="database",
    )

    store.create(incident)

    incident.current_step = "investigation_started"
    incident.status = IncidentStatus.INVESTIGATING

    store.update(incident)

    retrieved = store.get(incident.id)

    assert retrieved is not None
    assert retrieved.current_step == "investigation_started"
    assert retrieved.status == "INVESTIGATING"


def test_state_store_list(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    for index in range(3):
        store.create(
            Incident(
                title=f"Incident {index}",
                description="Test incident",
                service="test-service",
            )
        )

    incidents = store.list_all()

    assert len(incidents) == 3
