import pytest
from pv_twin.models import PanelParameters
from pydantic import ValidationError


def test_panel_parameters_accept_valid_catalog_entry() -> None:
    panel = PanelParameters(
        panel_id="generic_poly_330",
        pmax_stc_w=330.0,
        voc_stc_v=45.6,
        isc_stc_a=9.2,
        vmpp_stc_v=37.2,
        impp_stc_a=8.88,
        gamma_pmax_per_c=-0.0045,
        beta_voc_per_c=-0.0035,
        alpha_isc_per_c=0.0006,
        noct_c=45.0,
        cells_in_series=72,
        technology="poli_PERC",
    )

    assert panel.panel_id == "generic_poly_330"
    assert panel.pmax_stc_w == 330.0


def test_panel_parameters_reject_positive_gamma() -> None:
    with pytest.raises(ValidationError):
        PanelParameters(
            panel_id="generic_poly_330",
            pmax_stc_w=330.0,
            voc_stc_v=45.6,
            isc_stc_a=9.2,
            vmpp_stc_v=37.2,
            impp_stc_a=8.88,
            gamma_pmax_per_c=0.0045,
            beta_voc_per_c=-0.0035,
            alpha_isc_per_c=0.0006,
            noct_c=45.0,
            cells_in_series=72,
            technology="poli_PERC",
        )
