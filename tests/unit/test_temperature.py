import pytest
from pv_twin.simulator import (
    get_cell_temperature,
    get_cell_temperature_faiman,
    get_cell_temperature_sandia,
)


def test_get_cell_temperature_uses_ross_noct_model() -> None:
    assert get_cell_temperature(g_poa_w_m2=1000.0, t_amb_c=25.0, noct_c=45.0) == 56.25


def test_get_cell_temperature_rejects_negative_irradiance() -> None:
    with pytest.raises(ValueError, match="g_poa_w_m2"):
        get_cell_temperature(g_poa_w_m2=-1.0, t_amb_c=25.0, noct_c=45.0)


def test_get_cell_temperature_rejects_invalid_noct() -> None:
    with pytest.raises(ValueError, match="noct_c"):
        get_cell_temperature(g_poa_w_m2=1000.0, t_amb_c=25.0, noct_c=0.0)


def test_get_cell_temperature_faiman_reduces_temperature_with_wind() -> None:
    low_wind_t_cell_c = get_cell_temperature_faiman(
        g_poa_w_m2=900.0,
        t_amb_c=28.0,
        wind_speed_m_s=0.5,
    )
    high_wind_t_cell_c = get_cell_temperature_faiman(
        g_poa_w_m2=900.0,
        t_amb_c=28.0,
        wind_speed_m_s=4.0,
    )

    assert high_wind_t_cell_c < low_wind_t_cell_c


def test_get_cell_temperature_faiman_rejects_negative_wind() -> None:
    with pytest.raises(ValueError, match="wind_speed_m_s"):
        get_cell_temperature_faiman(g_poa_w_m2=900.0, t_amb_c=28.0, wind_speed_m_s=-0.1)


def test_get_cell_temperature_sandia_returns_finite_tropical_temperature() -> None:
    t_cell_c = get_cell_temperature_sandia(
        g_poa_w_m2=900.0,
        t_amb_c=30.0,
        wind_speed_m_s=2.0,
    )

    assert 30.0 < t_cell_c < 90.0
