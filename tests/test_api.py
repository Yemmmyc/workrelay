from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "workrelay",
    }


def test_create_incident():
    response = client.post(
        "/incidents",
        json={
            "title": "Payment API failure",
            "description": "Payment requests are returning HTTP 500 errors.",
            "service": "payment-api",
            "severity": "HIGH",
        },
    )

    assert response.status_code == 200

    data = response.json()
    incident = data["incident"]

    assert incident["service"] == "payment-api"
    assert incident["severity"] == "HIGH"
    assert incident["status"] == "RESOLVED"
    assert incident["workflow"] == "high_severity_incident"


def test_get_missing_incident():
    response = client.get("/incidents/INC-NOTFOUND")

    assert response.status_code == 404


def test_list_incidents():
    response = client.get("/incidents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_app_returns_fastapi_app():
    from fastapi import FastAPI
    from app.main import create_app

    test_app = create_app()

    assert isinstance(test_app, FastAPI)


def test_create_app_has_expected_routes():
    from app.main import create_app

    test_app = create_app()

    routes = {
        route.path
        for route in test_app.routes
    }

    assert "/health" in routes
    assert "/incidents" in routes
    assert "/incidents/{incident_id}" in routes


def test_create_app_with_local_provider(monkeypatch):
    from app.main import create_app

    monkeypatch.setenv(
        "WORKRELAY_DECISION_PROVIDER",
        "local",
    )

    test_app = create_app()
    test_client = TestClient(test_app)

    response = test_client.post(
        "/incidents",
        json={
            "title": "Local provider test",
            "description": "Testing application factory configuration.",
            "service": "test-api",
            "severity": "HIGH",
        },
    )

    assert response.status_code == 200

    incident = response.json()["incident"]

    assert incident["workflow"] == "high_severity_incident"
    assert (
        incident["metadata"]["coordination"]["decision_provider"]
        == "LocalDecisionProvider"
    )

def test_operations_console():
    response = client.get("/")

    assert response.status_code == 200
    assert "<title>WorkRelay — Incident Command Center</title>" in response.text
    assert "Create Incident" in response.text


def test_operations_console_static_css():
    response = client.get("/static/style.css")

    assert response.status_code == 200
    assert ":root" in response.text
    assert "--bg:" in response.text
    assert "--panel:" in response.text
