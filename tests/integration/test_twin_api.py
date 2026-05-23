from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_panels() -> None:
    response = client.get("/api/v1/twin/panels")

    assert response.status_code == 200
    panels = response.json()
    assert len(panels) >= 2
    assert {panel["panel_id"] for panel in panels} >= {"generic_poly_330", "jinko_tiger_neo_580"}


def test_get_panel_by_id() -> None:
    response = client.get("/api/v1/twin/panels/generic_poly_330")

    assert response.status_code == 200
    panel = response.json()
    assert panel["panel_id"] == "generic_poly_330"
    assert panel["pmax_stc_w"] == 330.0


def test_get_panel_by_id_returns_404_for_missing_panel() -> None:
    response = client.get("/api/v1/twin/panels/missing_panel")

    assert response.status_code == 404


def test_calculate_cell_temperature() -> None:
    response = client.post(
        "/api/v1/twin/cell-temperature",
        json={"g_poa_w_m2": 1000.0, "t_amb_c": 25.0, "noct_c": 45.0},
    )

    assert response.status_code == 200
    assert response.json() == {
        "g_poa_w_m2": 1000.0,
        "t_amb_c": 25.0,
        "noct_c": 45.0,
        "t_cell_c": 56.25,
    }


def test_calculate_cell_temperature_rejects_invalid_payload() -> None:
    response = client.post(
        "/api/v1/twin/cell-temperature",
        json={"g_poa_w_m2": -1.0, "t_amb_c": 25.0, "noct_c": 45.0},
    )

    assert response.status_code == 422
