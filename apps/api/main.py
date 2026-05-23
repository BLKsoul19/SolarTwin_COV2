from fastapi import FastAPI
from pv_twin import __version__

app = FastAPI(title="SolarTwin CO API", version=__version__)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "solartwin-co"}


@app.get("/api/v1/twin/panels")
def list_panels() -> list[dict[str, str]]:
    return [
        {
            "panel_id": "generic_poly_330",
            "model": "330W poli",
            "technology": "poli_PERC",
        }
    ]
