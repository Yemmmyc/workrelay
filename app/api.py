from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent.coordinator import IncidentCoordinator
from app.models.incident import Incident, IncidentSeverity
from app.services.state_store import LocalStateStore


app = FastAPI(
    title="WorkRelay",
    description="Automated operational incident coordination system.",
    version="0.1.0",
)


class IncidentRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    service: str = Field(min_length=1)
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    metadata: dict = Field(default_factory=dict)


class IncidentResponse(BaseModel):
    incident: Incident


store = LocalStateStore()
coordinator = IncidentCoordinator(store)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "workrelay",
    }


@app.post("/incidents", response_model=IncidentResponse)
def create_incident(request: IncidentRequest) -> IncidentResponse:
    incident = Incident(
        title=request.title,
        description=request.description,
        service=request.service,
        severity=request.severity,
        metadata=request.metadata,
    )

    result = coordinator.handle(incident)

    return IncidentResponse(incident=result)


@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str) -> IncidentResponse:
    incident = store.get(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found.",
        )

    return IncidentResponse(incident=incident)


@app.get("/incidents", response_model=list[Incident])
def list_incidents() -> list[Incident]:
    return store.list_all()
