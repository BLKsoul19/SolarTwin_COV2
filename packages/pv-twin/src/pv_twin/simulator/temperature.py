from typing import Literal

from pvlib import temperature


def get_cell_temperature(g_poa_w_m2: float, t_amb_c: float, noct_c: float) -> float:
    """Calculate PV cell temperature with the Ross NOCT model."""
    if g_poa_w_m2 < 0:
        raise ValueError("g_poa_w_m2 must be greater than or equal to 0")
    if noct_c <= 0:
        raise ValueError("noct_c must be greater than 0")
    return t_amb_c + g_poa_w_m2 * (noct_c - 20.0) / 800.0


def get_cell_temperature_faiman(
    g_poa_w_m2: float,
    t_amb_c: float,
    wind_speed_m_s: float,
    u0: float = 25.0,
    u1: float = 6.84,
) -> float:
    """Calculate cell temperature with the Faiman wind-dependent model."""
    if g_poa_w_m2 < 0:
        raise ValueError("g_poa_w_m2 must be greater than or equal to 0")
    if wind_speed_m_s < 0:
        raise ValueError("wind_speed_m_s must be greater than or equal to 0")
    heat_loss_w_m2_c = u0 + u1 * wind_speed_m_s
    if heat_loss_w_m2_c <= 0:
        raise ValueError("u0 + u1 * wind_speed_m_s must be greater than 0")
    return t_amb_c + g_poa_w_m2 / heat_loss_w_m2_c


def get_cell_temperature_sandia(
    g_poa_w_m2: float,
    t_amb_c: float,
    wind_speed_m_s: float,
    mounting: Literal[
        "open_rack_glass_glass",
        "close_mount_glass_glass",
        "open_rack_glass_polymer",
        "insulated_back_glass_polymer",
    ] = "open_rack_glass_glass",
) -> float:
    """Calculate cell temperature with the Sandia/SAPM temperature model."""
    if g_poa_w_m2 < 0:
        raise ValueError("g_poa_w_m2 must be greater than or equal to 0")
    if wind_speed_m_s < 0:
        raise ValueError("wind_speed_m_s must be greater than or equal to 0")
    params = temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"][mounting]
    t_cell_c = temperature.sapm_cell(
        poa_global=g_poa_w_m2,
        temp_air=t_amb_c,
        wind_speed=wind_speed_m_s,
        **params,
    )
    return float(t_cell_c)
