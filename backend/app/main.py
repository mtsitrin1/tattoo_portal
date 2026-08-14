from fastapi import FastAPI

app = FastAPI(title="Tattoo Portal API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
