from fastapi import FastAPI

app = FastAPI(title="ms-analyse")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Expose a simple health endpoint for service monitoring."""
    return {"status": "ok"}
