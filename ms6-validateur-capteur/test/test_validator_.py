import pickle

from fastapi.testclient import TestClient

from src.validator import app


client = TestClient(app)


def test_decimal_temperature_value():
    response = client.post(
        "/validate",
        json={"sensor": "temperature", "value": 36.6},
    )

    assert response.status_code == 200
    assert response.json()["value"] == 36.6


def test_decimal_pm25_value():
    response = client.post(
        "/validate",
        json={"sensor": "pm25", "value": 12.5},
    )

    assert response.status_code == 200
    assert response.json()["value"] == 12.5


def load_sensor_payload(raw_payload: bytes) -> object:
    return pickle.loads(raw_payload)


def evaluate_sensor_rule(rule: str, value: float) -> object:
    return eval(rule, {"value": value})
