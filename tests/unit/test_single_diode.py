import pytest
from pv_twin.models import PanelCatalogRepository
from pv_twin.simulator import SolarPanelTwin, get_cec_cell_type

G_POA_MATRIX_W_M2 = [200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0]
T_CELL_MATRIX_C = [-10.0, 25.0, 50.0, 80.0]


def test_solar_panel_twin_calculates_stc_iv_curve() -> None:
    panel = PanelCatalogRepository().get_by_id("generic_poly_330")
    twin = SolarPanelTwin(panel)

    result = twin.get_iv_curve(g_poa_w_m2=1000.0, t_cell_c=25.0, n_points=50)

    assert result.panel_id == "generic_poly_330"
    assert abs(result.p_mpp_w - panel.pmax_stc_w) / panel.pmax_stc_w <= 0.05
    assert result.v_oc_v > result.v_mpp_v
    assert result.i_sc_a > result.i_mpp_a
    assert result.p_mpp_w > 0
    assert len(result.points) == 50
    assert result.points[0].v_v == pytest.approx(0.0)
    assert result.points[-1].v_v == pytest.approx(result.v_oc_v)


def test_solar_panel_twin_rejects_low_irradiance() -> None:
    panel = PanelCatalogRepository().get_by_id("generic_poly_330")
    twin = SolarPanelTwin(panel)

    with pytest.raises(ValueError, match="g_poa_w_m2"):
        twin.get_iv_curve(g_poa_w_m2=9.0, t_cell_c=25.0)


def test_solar_panel_twin_rejects_temperature_outside_valid_range() -> None:
    panel = PanelCatalogRepository().get_by_id("generic_poly_330")
    twin = SolarPanelTwin(panel)

    with pytest.raises(ValueError, match="t_cell_c"):
        twin.get_iv_curve(g_poa_w_m2=1000.0, t_cell_c=86.0)


def test_solar_panel_twin_rejects_invalid_point_count() -> None:
    panel = PanelCatalogRepository().get_by_id("generic_poly_330")
    twin = SolarPanelTwin(panel)

    with pytest.raises(ValueError, match="n_points"):
        twin.get_iv_curve(g_poa_w_m2=1000.0, t_cell_c=25.0, n_points=9)


@pytest.mark.parametrize(
    ("technology", "expected_cell_type"),
    [
        ("poli_PERC", "polySi"),
        ("TOPCon", "monoSi"),
        ("HPBC", "monoSi"),
        ("PERC", "monoSi"),
        ("HJT", "monoSi"),
    ],
)
def test_get_cec_cell_type_maps_supported_technologies(
    technology: str,
    expected_cell_type: str,
) -> None:
    assert get_cec_cell_type(technology) == expected_cell_type


def test_get_cec_cell_type_rejects_unknown_technology() -> None:
    with pytest.raises(ValueError, match="Unsupported panel technology"):
        get_cec_cell_type("unknown")


@pytest.mark.parametrize(
    "panel_id",
    [
        "canadian_hiku7_600",
        "generic_poly_330",
        "ja_solar_jam72d40_570",
        "jinko_tiger_neo_580",
        "longi_himo_x6_580",
        "risen_rsm144_550",
        "trina_vertex_splus_420",
    ],
)
def test_all_catalog_panels_reconstruct_stc_power(panel_id: str) -> None:
    panel = PanelCatalogRepository().get_by_id(panel_id)
    result = SolarPanelTwin(panel).get_iv_curve(g_poa_w_m2=1000.0, t_cell_c=25.0)

    assert abs(result.p_mpp_w - panel.pmax_stc_w) / panel.pmax_stc_w <= 0.05
    assert result.v_oc_v > result.v_mpp_v
    assert result.i_sc_a > result.i_mpp_a
    assert result.p_mpp_w > 0


def test_physical_validation_matrix_for_all_catalog_panels() -> None:
    catalog = PanelCatalogRepository()

    for panel in catalog.list_all():
        twin = SolarPanelTwin(panel)
        previous_power_w = 0.0
        for g_poa_w_m2 in G_POA_MATRIX_W_M2:
            result = twin.get_iv_curve(g_poa_w_m2=g_poa_w_m2, t_cell_c=25.0, n_points=40)
            assert result.p_mpp_w > previous_power_w
            assert result.v_oc_v > result.v_mpp_v
            assert result.i_sc_a > result.i_mpp_a
            assert all(point.p_w >= 0 for point in result.points)
            previous_power_w = result.p_mpp_w

        cool_result = twin.get_iv_curve(g_poa_w_m2=1000.0, t_cell_c=-10.0, n_points=40)
        hot_result = twin.get_iv_curve(g_poa_w_m2=1000.0, t_cell_c=80.0, n_points=40)
        assert hot_result.p_mpp_w < cool_result.p_mpp_w

        for g_poa_w_m2 in G_POA_MATRIX_W_M2:
            for t_cell_c in T_CELL_MATRIX_C:
                result = twin.get_iv_curve(
                    g_poa_w_m2=g_poa_w_m2,
                    t_cell_c=t_cell_c,
                    n_points=40,
                )
                assert result.p_mpp_w > 0
                assert result.v_oc_v > result.v_mpp_v
                assert result.i_sc_a > result.i_mpp_a
