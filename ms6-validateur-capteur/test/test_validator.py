from fastapi.testclient import TestClient

from src.validator import app

client = TestClient(app)

def test_normal():
    response = client.post("/validate", json={"sensor": "co2", "value": 500})

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["level"] == "normal"
    assert data["sensor"] == "co2"
    assert data["value"] == 500
    assert data["threshold"] == 800
    assert "timestamp" in data


def test_moderate():
    response = client.post(
        "/validate",
        json={"sensor": "temperature", "value": 37},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["level"] == "moderate"
    assert data["sensor"] == "temperature"
    assert data["value"] == 37
    assert data["threshold"] == 40
    assert "timestamp" in data


def test_critical():
    response = client.post("/validate", json={"sensor": "noise", "value": 85})

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["level"] == "critical"
    assert data["sensor"] == "noise"
    assert data["value"] == 85
    assert data["threshold"] == 85
    assert "timestamp" in data


def test_unknown():
    response = client.post(
        "/validate",
        json={"sensor": "wind", "value": 12},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["level"] == "unknown"
    assert data["sensor"] == "wind"
    assert data["value"] == 12
    assert data["threshold"] is None
    assert "timestamp" in data
