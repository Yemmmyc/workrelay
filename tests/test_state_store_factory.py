import pytest

from app.services.state_store import LocalStateStore
from app.services.state_store_factory import create_state_store


def test_state_store_factory_defaults_to_local(monkeypatch, tmp_path):
    monkeypatch.delenv("WORKRELAY_STATE_STORE", raising=False)

    monkeypatch.chdir(tmp_path)

    store = create_state_store()

    assert isinstance(store, LocalStateStore)


def test_state_store_factory_selects_local(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKRELAY_STATE_STORE", "local")

    monkeypatch.chdir(tmp_path)

    store = create_state_store()

    assert isinstance(store, LocalStateStore)


def test_state_store_factory_rejects_unknown_store(monkeypatch):
    monkeypatch.setenv("WORKRELAY_STATE_STORE", "invalid")

    with pytest.raises(ValueError, match="Unsupported WORKRELAY_STATE_STORE"):
        create_state_store()
