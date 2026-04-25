import os

os.environ["DATABASE_URL"] = "sqlite:///./test_ms_analyse.db"

from fastapi.testclient import TestClient

from src.main import app

def test_healthcheck_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_traffic_analysis_returns_dashboard_and_outputs() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/traffic/analyze",
            json={
                "sensorId": "sensor-1",
                "zoneId": "zone-A",
                "windowStart": "2026-04-11T10:00:00Z",
                "windowEnd": "2026-04-11T10:00:15Z",
                "vehicles": [
                    {"speedKmh": 45, "vehicleType": "car"},
                    {"speedKmh": 40, "vehicleType": "truck"},
                    {"speedKmh": 20, "vehicleType": "car"},
                ],
                "vehicleCount": 3,
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["input"]["zoneId"] == "zone-A"
        assert len(payload["outputs"]) == 6
        assert payload["outputs"][0]["destination"] == "dashboard"
        assert payload["outputs"][0]["payload"]["averageSpeedKmh"] == 35.0
        assert payload["outputs"][1]["channel"] == "alert_queue"
        assert payload["outputs"][5]["channel"] == "analysis.traffic.kpi"


def test_dashboard_endpoint_returns_latest_analysis() -> None:
    with TestClient(app) as client:
        client.post(
            "/traffic/analyze",
            json={
                "sensorId": "sensor-2",
                "zoneId": "zone-B",
                "windowStart": "2026-04-11T10:00:00Z",
                "windowEnd": "2026-04-11T10:00:30Z",
                "vehicles": [
                    {"speedKmh": 60, "vehicleType": "car"},
                ],
                "vehicleCount": 1,
            },
        )

        response = client.get("/traffic/dashboard")

        assert response.status_code == 200
        assert response.json()["items"][0]["zoneId"] == "zone-B"
