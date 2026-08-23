from __future__ import annotations

from app.actions.incident_actions import (
    investigate_incident,
    remediate_incident,
    verify_incident,
)
from app.actions.notification_actions import record_escalation
from app.models.incident import Incident, IncidentStatus
from app.services.state_store import LocalStateStore
from app.workflows.registry import select_workflow


class IncidentWorkflow:
    """
    Executes the WorkRelay incident lifecycle.

    The workflow engine owns state transitions and reliability behavior.
    External intelligence or agent decisions can later select the workflow,
    but execution remains controlled here.
    """

    def __init__(self, state_store: LocalStateStore) -> None:
        self.state_store = state_store

    def _save(self, incident: Incident) -> None:
        self.state_store.update(incident)

    def _transition(
        self,
        incident: Incident,
        status: IncidentStatus,
        step: str,
    ) -> None:
        incident.status = status
        incident.current_step = step
        self._save(incident)

    def start(self, incident: Incident) -> Incident:
        """
        Start processing an incident.

        The incident must already exist in the state store.
        """

        if self.state_store.get(incident.id) is None:
            self.state_store.create(incident)

        workflow = select_workflow(incident.severity)
        incident.workflow = workflow.name

        self._transition(
            incident,
            IncidentStatus.CLASSIFYING,
            "incident_classified",
        )

        self._transition(
            incident,
            IncidentStatus.INVESTIGATING,
            "investigation_started",
        )

        investigation = investigate_incident(incident)

        if not investigation.success:
            return self._handle_failure(
                incident,
                investigation.message,
            )

        self._save(incident)

        self._transition(
            incident,
            IncidentStatus.REMEDIATING,
            "remediation_started",
        )

        remediation = remediate_incident(incident)

        if not remediation.success:
            return self._handle_failure(
                incident,
                remediation.message,
            )

        self._save(incident)

        self._transition(
            incident,
            IncidentStatus.VERIFYING,
            "verification_started",
        )

        verification = verify_incident(incident)

        if not verification.success:
            return self._handle_failure(
                incident,
                verification.message,
            )

        incident.resolution = verification.message

        self._transition(
            incident,
            IncidentStatus.RESOLVED,
            "incident_resolved",
        )

        return incident

    def _handle_failure(
        self,
        incident: Incident,
        reason: str,
    ) -> Incident:
        workflow = select_workflow(incident.severity)

        incident.metadata.setdefault("failures", []).append(reason)

        if incident.retry_count < workflow.max_retries:
            incident.retry_count += 1

            incident.metadata.setdefault("retries", []).append(
                {
                    "attempt": incident.retry_count,
                    "reason": reason,
                }
            )

            self._save(incident)

            return self._retry(incident)

        return self._escalate(incident, reason)

    def _retry(self, incident: Incident) -> Incident:
        """
        Retry the operational workflow from investigation.
        """

        self._transition(
            incident,
            IncidentStatus.INVESTIGATING,
            f"retry_{incident.retry_count}_investigation",
        )

        investigation = investigate_incident(incident)

        if not investigation.success:
            return self._handle_failure(
                incident,
                investigation.message,
            )

        self._save(incident)

        self._transition(
            incident,
            IncidentStatus.REMEDIATING,
            f"retry_{incident.retry_count}_remediation",
        )

        remediation = remediate_incident(incident)

        if not remediation.success:
            return self._handle_failure(
                incident,
                remediation.message,
            )

        self._save(incident)

        self._transition(
            incident,
            IncidentStatus.VERIFYING,
            f"retry_{incident.retry_count}_verification",
        )

        verification = verify_incident(incident)

        if not verification.success:
            return self._handle_failure(
                incident,
                verification.message,
            )

        incident.resolution = verification.message

        self._transition(
            incident,
            IncidentStatus.RESOLVED,
            "incident_resolved_after_retry",
        )

        return incident

    def _escalate(
        self,
        incident: Incident,
        reason: str,
    ) -> Incident:
        record_escalation(incident, reason)

        self._transition(
            incident,
            IncidentStatus.ESCALATED,
            "incident_escalated",
        )

        return incident
