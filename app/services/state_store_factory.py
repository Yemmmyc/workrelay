from __future__ import annotations

import os

from app.services.firestore_state_store import FirestoreStateStore
from app.services.state_store import LocalStateStore
from app.services.state_store_interface import StateStore


def create_state_store() -> StateStore:
    """
    Create the configured WorkRelay state store.

    Defaults to the local JSON store so WorkRelay remains runnable
    without Google Cloud credentials or external network access.
    """
    store_name = os.getenv(
        "WORKRELAY_STATE_STORE",
        "local",
    ).strip().lower()

    if store_name == "local":
        return LocalStateStore()

    if store_name == "firestore":
        return FirestoreStateStore()

    raise ValueError(
        "Unsupported WORKRELAY_STATE_STORE: "
        f"{store_name}. Expected 'local' or 'firestore'."
    )
