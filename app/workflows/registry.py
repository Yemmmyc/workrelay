from __future__ import annotations

from dataclasses import dataclass

from app.models.incident import IncidentSeverity


@dataclass(frozen=True)
class WorkflowDefinition:
    name: str
    description: str
    max_retries: int
    escalation_enabled: bool


WORKFLOWS: dict[str, WorkflowDefinition] = {
    "standard_incident": WorkflowDefinition(
        name="standard_incident",
        description="Investigate and remediate a standard operational incident.",
        max_retries=1,
        escalation_enabled=True,
    ),
    "high_severity_incident": WorkflowDefinition(
        name="high_severity_incident",
        description="Rapidly investigate and remediate a high-severity incident.",
        max_retries=1,
        escalation_enabled=True,
    ),
    "critical_incident": WorkflowDefinition(
        name="critical_incident",
        description="Handle a critical incident with immediate escalation capability.",
        max_retries=0,
        escalation_enabled=True,
    ),
}


def select_workflow(severity: IncidentSeverity) -> WorkflowDefinition:
    if severity == IncidentSeverity.CRITICAL:
        return WORKFLOWS["critical_incident"]

    if severity == IncidentSeverity.HIGH:
        return WORKFLOWS["high_severity_incident"]

    return WORKFLOWS["standard_incident"]


def get_workflow(name: str) -> WorkflowDefinition:
    try:
        return WORKFLOWS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown workflow: {name}") from exc
