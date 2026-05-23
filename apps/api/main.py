from fastapi import FastAPI
from pv_twin import __version__

from apps.api.routers.twin import router as twin_router

app = FastAPI(title="SolarTwin CO API", version=__version__)
app.include_router(twin_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "solartwin-co"}
