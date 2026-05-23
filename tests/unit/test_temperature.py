import pytest
from pv_twin.simulator import get_cell_temperature


def test_get_cell_temperature_uses_ross_noct_model() -> None:
    assert get_cell_temperature(g_poa_w_m2=1000.0, t_amb_c=25.0, noct_c=45.0) == 56.25


def test_get_cell_temperature_rejects_negative_irradiance() -> None:
    with pytest.raises(ValueError, match="g_poa_w_m2"):
        get_cell_temperature(g_poa_w_m2=-1.0, t_amb_c=25.0, noct_c=45.0)


def test_get_cell_temperature_rejects_invalid_noct() -> None:
    with pytest.raises(ValueError, match="noct_c"):
        get_cell_temperature(g_poa_w_m2=1000.0, t_amb_c=25.0, noct_c=0.0)
