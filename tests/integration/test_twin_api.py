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


def test_get_panel_iv_curve() -> None:
    response = client.get(
        "/api/v1/twin/panels/generic_poly_330/iv",
        params={"g_poa_w_m2": 1000.0, "t_cell_c": 25.0, "n_points": 25},
    )

    assert response.status_code == 200
    curve = response.json()
    assert curve["panel_id"] == "generic_poly_330"
    assert abs(curve["p_mpp_w"] - 330.0) / 330.0 <= 0.05
    assert curve["v_oc_v"] > curve["v_mpp_v"]
    assert curve["i_sc_a"] > curve["i_mpp_a"]
    assert len(curve["points"]) == 25
    assert {"v_v", "i_a", "p_w"} <= set(curve["points"][0])


def test_get_panel_pv_curve() -> None:
    response = client.get(
        "/api/v1/twin/panels/generic_poly_330/pv",
        params={"g_poa_w_m2": 1000.0, "t_cell_c": 25.0, "n_points": 25},
    )

    assert response.status_code == 200
    curve = response.json()
    assert curve["panel_id"] == "generic_poly_330"
    assert len(curve["points"]) == 25
    assert {"v_v", "p_w"} <= set(curve["points"][0])
    assert "i_a" not in curve["points"][0]


def test_get_panel_iv_curve_returns_404_for_missing_panel() -> None:
    response = client.get(
        "/api/v1/twin/panels/missing_panel/iv",
        params={"g_poa_w_m2": 1000.0, "t_cell_c": 25.0},
    )

    assert response.status_code == 404


def test_get_panel_iv_curve_rejects_invalid_query() -> None:
    response = client.get(
        "/api/v1/twin/panels/generic_poly_330/iv",
        params={"g_poa_w_m2": 9.0, "t_cell_c": 25.0},
    )

    assert response.status_code == 422
