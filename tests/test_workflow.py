from app.models.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.agent.coordinator import IncidentCoordinator
from app.services.state_store import LocalStateStore
from app.workflows.incident_workflow import IncidentWorkflow
from app.workflows.registry import select_workflow

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

def test_workflow_resolves_incident(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Payment API failure",
        description="Payment requests are returning HTTP 500 errors.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
    )

    workflow = IncidentWorkflow(store)
    result = workflow.start(incident)

    assert result.status == IncidentStatus.RESOLVED
    assert result.current_step == "incident_resolved"
    assert result.workflow == "high_severity_incident"
    assert result.resolution is not None


def test_workflow_retries_and_resolves(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Payment API failure",
        description="Payment requests are returning HTTP 500 errors.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
        metadata={
            "force_verification_failure": True,
        },
    )

    workflow = IncidentWorkflow(store)

    # First verification fails. Change the simulation before retry.
    result = workflow.start(incident)

    assert result.status == IncidentStatus.ESCALATED
    assert result.retry_count == 1


def test_critical_incident_escalates_without_retry(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Critical service failure",
        description="Critical service is unavailable.",
        service="core-api",
        severity=IncidentSeverity.CRITICAL,
        metadata={
            "force_remediation_failure": True,
        },
    )

    workflow = IncidentWorkflow(store)
    result = workflow.start(incident)

    assert result.status == IncidentStatus.ESCALATED
    assert result.retry_count == 0
    assert result.escalation_reason is not None

def test_workflow_retries_and_recovers(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Temporary payment failure",
        description="Payment service briefly failed.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
        metadata={
            "fail_remediation_once": True,
        },
    )

    workflow = IncidentWorkflow(store)
    result = workflow.start(incident)

    assert result.status == IncidentStatus.RESOLVED
    assert result.retry_count == 1
    assert result.current_step == "incident_resolved_after_retry"
    assert len(result.metadata["retries"]) == 1

def test_workflow_persists_final_state(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="API outage",
        description="API is unavailable.",
        service="core-api",
        severity=IncidentSeverity.MEDIUM,
    )

    workflow = IncidentWorkflow(store)
    workflow.start(incident)

    saved = store.get(incident.id)

    assert saved is not None
    assert saved.status == IncidentStatus.RESOLVED
    assert saved.current_step == "incident_resolved"
    assert saved.workflow == "standard_incident"
    assert saved.resolution is not None

def test_coordinator_routes_and_executes_incident(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Payment API failure",
        description="Payment requests are returning HTTP 500 errors.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
    )

    coordinator = IncidentCoordinator(store)
    result = coordinator.handle(incident)

    assert result.status == IncidentStatus.RESOLVED
    assert result.workflow == "high_severity_incident"

    coordination = result.metadata["coordination"]

    assert coordination["decision_provider"] == "LocalDecisionProvider"
    assert "HIGH" in coordination["reasoning"]


def test_coordinator_preserves_failure_and_escalates(tmp_path):
    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Critical service failure",
        description="Core API remediation failed.",
        service="core-api",
        severity=IncidentSeverity.CRITICAL,
        metadata={
            "force_remediation_failure": True,
        },
    )

    coordinator = IncidentCoordinator(store)
    result = coordinator.handle(incident)

    assert result.status == IncidentStatus.ESCALATED
    assert result.workflow == "critical_incident"
    assert result.retry_count == 0
    assert result.escalation_reason is not None


def test_coordinator_uses_injected_decision_provider(tmp_path):
    class StubDecisionProvider:
        def decide(self, incident):
            from app.agent.decision import CoordinationDecision
            from app.workflows.registry import get_workflow

            return CoordinationDecision(
                workflow=get_workflow("standard_incident"),
                reasoning="Test decision provider selected standard workflow.",
            )

    store = LocalStateStore(tmp_path / "incidents.json")

    incident = Incident(
        title="Test incident",
        description="Testing coordinator dependency injection.",
        service="test-service",
        severity=IncidentSeverity.CRITICAL,
    )

    coordinator = IncidentCoordinator(
        store,
        decision_provider=StubDecisionProvider(),
    )

    result = coordinator.handle(incident)

    assert result.status == IncidentStatus.RESOLVED
    assert result.workflow == "standard_incident"
    assert (
        result.metadata["coordination"]["decision_provider"]
        == "StubDecisionProvider"
    )

def test_gemini_decision_provider_rejects_unknown_workflow():
    from types import SimpleNamespace

    from app.agent.decision import GeminiDecisionProvider

    provider = GeminiDecisionProvider()

    provider.session_service = SimpleNamespace(
        create_session=lambda **kwargs: SimpleNamespace(
            id="test-session"
        )
    )

    provider.runner = SimpleNamespace(
        run=lambda **kwargs: iter(
            [
                SimpleNamespace(
                    content=SimpleNamespace(
                        parts=[
                            SimpleNamespace(
                                text=(
                                    '{"workflow":"invented_workflow",'
                                    '"reasoning":"Invalid test workflow."}'
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    incident = Incident(
        title="Test incident",
        description="Testing invalid Gemini workflow handling.",
        service="test-service",
        severity=IncidentSeverity.HIGH,
    )

    try:
        provider.decide(incident)
        assert False, "Expected invalid workflow to be rejected"
    except ValueError as exc:
        assert "Gemini selected an unknown workflow" in str(exc)

def test_gemini_decision_provider_returns_valid_workflow():
    from types import SimpleNamespace

    from app.agent.decision import GeminiDecisionProvider

    provider = GeminiDecisionProvider()

    provider.session_service = SimpleNamespace(
        create_session=lambda **kwargs: SimpleNamespace(
            id="test-session"
        )
    )

    provider.runner = SimpleNamespace(
        run=lambda **kwargs: iter(
            [
                SimpleNamespace(
                    content=SimpleNamespace(
                        parts=[
                            SimpleNamespace(
                                text=(
                                    '{"workflow":"high_severity_incident",'
                                    '"reasoning":"HIGH severity requires '
                                    'cautious coordination."}'
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    incident = Incident(
        title="Payment API failure",
        description="Payment requests are returning HTTP 500 errors.",
        service="payment-api",
        severity=IncidentSeverity.HIGH,
    )

    result = provider.decide(incident)

    assert result.workflow.name == "high_severity_incident"
    assert (
        result.reasoning
        == "HIGH severity requires cautious coordination."
    )
