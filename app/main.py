from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")

    @app.get("/", include_in_schema=False)
    async def home(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={},
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
