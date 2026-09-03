from __future__ import annotations

from app.agent.decision import (
    DecisionProvider,
    LocalDecisionProvider,
)
from app.models.incident import Incident
from app.services.state_store import LocalStateStore
from app.workflows.incident_workflow import IncidentWorkflow


class IncidentCoordinator:
    """
    Coordinates incident handling from intake through workflow execution.

    The coordinator is the boundary between decision-making and the
    deterministic workflow engine.

    Today:
        LocalDecisionProvider

    Later:
        Gemini + Google ADK decision provider
    """

    def __init__(
        self,
        state_store: LocalStateStore,
        decision_provider: DecisionProvider | None = None,
    ) -> None:
        self.state_store = state_store
        self.decision_provider = (
            decision_provider
            if decision_provider is not None
            else LocalDecisionProvider()
        )
        self.workflow_engine = IncidentWorkflow(state_store)

    def handle(self, incident: Incident) -> Incident:
        """
        Accept an incident, determine its workflow, and execute it.
        """

        decision = self.decision_provider.decide(incident)

        incident.workflow = decision.workflow.name
        incident.record_event(
            "WORKFLOW_SELECTED",
            step="workflow_selected",
            details={
                "workflow": decision.workflow.name,
                "decision_provider": self.decision_provider.__class__.__name__,
                "reasoning": decision.reasoning,
            },
        )

        incident.metadata["coordination"] = {
            "reasoning": decision.reasoning,
            "decision_provider": self.decision_provider.__class__.__name__,
        }

        if self.state_store.get(incident.id) is None:
            self.state_store.create(incident)
        else:
            self.state_store.update(incident)

        return self.workflow_engine.start(
            incident,
            workflow=decision.workflow,
        )
