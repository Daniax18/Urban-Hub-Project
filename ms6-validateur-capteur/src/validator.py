from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="MS6 Validateur Capteur")


class SensorData(BaseModel):
    sensor: str = Field(..., min_length=1)
    value: float


THRESHOLDS = {
    "co2": {"moderate": 800, "critical": 1000, "unit": "ppm"},
    "temperature": {"moderate": 35, "critical": 40, "unit": "C"},
    "noise": {"moderate": 70, "critical": 85, "unit": "dB"},
    "pm25": {"moderate": 25, "critical": 590, "unit": "ug/m"},
    "humidity_air": {"moderate": 10, "critical": 40, "unit": "%"},
}


def classify(sensor: str, value: float) -> dict:
    thresholds = THRESHOLDS.get(sensor)
    timestamp = datetime.now(timezone.utc).isoformat()

    if thresholds is None:
        return {
            "valid": False,
            "level": "unknown",
            "sensor": sensor,
            "value": value,
            "threshold": None,
            "timestamp": timestamp,
        }

    if value >= thresholds["critical"]:
        level = "critical"
        threshold = thresholds["critical"]
    elif value >= thresholds["moderate"]:
        level = "moderate"
        threshold = thresholds["critical"]
    else:
        level = "normal"
        threshold = thresholds["moderate"]

    return {
        "valid": True,
        "level": level,
        "sensor": sensor,
        "value": value,
        "threshold": threshold,
        "timestamp": timestamp,
    }


@app.post("/validate")
def validate_sensor_data(payload: SensorData) -> dict:
    return classify(payload.sensor, payload.value)
