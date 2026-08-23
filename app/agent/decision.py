from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.models.incident import Incident
from app.workflows.registry import WorkflowDefinition, select_workflow


@dataclass(frozen=True)
class CoordinationDecision:
    workflow: WorkflowDefinition
    reasoning: str


class DecisionProvider(Protocol):
    """
    Interface for determining how an incident should be handled.

    The local implementation is deterministic. A future Gemini + ADK
    implementation can satisfy this same interface without changing the
    workflow engine or coordinator.
    """

    def decide(self, incident: Incident) -> CoordinationDecision:
        ...


class LocalDecisionProvider:
    """
    Deterministic decision provider for local development and testing.

    This intentionally contains no network calls, credentials, Gemini,
    ADK, or Google Cloud dependencies.
    """

    def decide(self, incident: Incident) -> CoordinationDecision:
        workflow = select_workflow(incident.severity)

        return CoordinationDecision(
            workflow=workflow,
            reasoning=(
                f"Incident severity {incident.severity.value} "
                f"routes to the {workflow.name} workflow."
            ),
        )
