from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel

from app.models.incident import Incident
from app.workflows.registry import WorkflowDefinition, select_workflow


class GeminiCoordinationResponse(BaseModel):
    workflow: str
    reasoning: str


@dataclass(frozen=True)
class CoordinationDecision:
    workflow: WorkflowDefinition
    reasoning: str


class DecisionProvider(Protocol):
    """
    Interface for determining how an incident should be handled.

    Different decision providers can satisfy this interface without changing
    the coordinator or deterministic workflow engine.
    """

    def decide(self, incident: Incident) -> CoordinationDecision:
        ...


class LocalDecisionProvider:
    """
    Deterministic decision provider for local development and testing.

    This implementation performs no network calls and requires no credentials.
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


class GeminiDecisionProvider:
    """
    Gemini + Google ADK decision provider.

    Gemini is responsible only for recommending the incident workflow.
    Actual incident execution remains under the deterministic workflow engine.
    """

    APP_NAME = "workrelay"
    USER_ID = "workrelay-system"

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
    ) -> None:
        from google.adk.agents import Agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService

        from app.agent.prompts import COORDINATION_SYSTEM_PROMPT

        self.model = model

        self.agent = Agent(
            name="workrelay_coordinator",
            model=model,
            instruction=COORDINATION_SYSTEM_PROMPT,
            output_schema=GeminiCoordinationResponse,
        )

        self.session_service = InMemorySessionService()

        self.runner = Runner(
            app_name=self.APP_NAME,
            agent=self.agent,
            session_service=self.session_service,
        )

    def decide(self, incident: Incident) -> CoordinationDecision:
        from google.genai import types

        session = self.session_service.create_session(
            app_name=self.APP_NAME,
            user_id=self.USER_ID,
        )

        incident_payload = {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "service": incident.service,
            "severity": incident.severity.value,
        }

        message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        "Analyze this incident and select the appropriate "
                        "WorkRelay workflow.\n\n"
                        f"{incident_payload}"
                    )
                )
            ],
        )

        events = self.runner.run(
            user_id=self.USER_ID,
            session_id=session.id,
            new_message=message,
        )

        response_text = None

        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text = part.text

        if not response_text:
            raise RuntimeError(
                "Gemini ADK returned no decision response."
            )

        response = GeminiCoordinationResponse.model_validate_json(
            response_text
        )

        from app.workflows.registry import get_workflow

        try:
            workflow = get_workflow(response.workflow)
        except ValueError as exc:
            raise ValueError(
                f"Gemini selected an unknown workflow: {response.workflow}"
            ) from exc

        return CoordinationDecision(
            workflow=workflow,
            reasoning=response.reasoning,
        )
