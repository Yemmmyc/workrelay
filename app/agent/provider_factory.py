from __future__ import annotations

import os

from app.agent.decision import (
    DecisionProvider,
    GeminiDecisionProvider,
    LocalDecisionProvider,
)


def create_decision_provider() -> DecisionProvider:
    """
    Create the configured WorkRelay decision provider.

    Defaults to the deterministic local provider so WorkRelay remains
    runnable without Gemini credentials or external network access.
    """
    provider_name = os.getenv(
        "WORKRELAY_DECISION_PROVIDER",
        "local",
    ).strip().lower()

    if provider_name == "local":
        return LocalDecisionProvider()

    if provider_name == "gemini":
        return GeminiDecisionProvider()

    raise ValueError(
        "Unsupported WORKRELAY_DECISION_PROVIDER: "
        f"{provider_name}. Expected 'local' or 'gemini'."
    )
