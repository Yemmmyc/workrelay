from __future__ import annotations

from fastapi import FastAPI

from app.agent.coordinator import IncidentCoordinator
from app.agent.provider_factory import create_decision_provider
from app.api import create_routes
from app.services.state_store_factory import create_state_store


def create_app() -> FastAPI:
    app = FastAPI(
        title="WorkRelay",
        description="Automated operational incident coordination system.",
        version="0.1.0",
    )

    store = create_state_store()
    decision_provider = create_decision_provider()

    coordinator = IncidentCoordinator(
        store,
        decision_provider=decision_provider,
    )

    create_routes(
        app,
        store,
        coordinator,
    )

    return app


app = create_app()
