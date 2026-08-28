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
