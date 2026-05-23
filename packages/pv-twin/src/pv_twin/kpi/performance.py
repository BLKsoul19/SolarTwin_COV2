def performance_ratio(
    e_ac_kwh: float,
    p_stc_kwp: float,
    h_poa_kwh_m2: float,
    g_ref_w_m2: float = 1000.0,
) -> float:
    """Calcula PR = Yf / Yr segun IEC 61724-1."""
    yf_h = e_ac_kwh / p_stc_kwp
    yr_h = h_poa_kwh_m2 / (g_ref_w_m2 / 1000.0)
    return yf_h / yr_h


def capacity_utilization_factor(e_ac_kwh: float, p_stc_kwp: float, hours: float) -> float:
    """Calcula CUF = E_AC / (P_STC * horas)."""
    return e_ac_kwh / (p_stc_kwp * hours)


def specific_yield(e_ac_kwh: float, p_stc_kwp: float) -> float:
    """Calcula el yield especifico [kWh/kWp]."""
    return e_ac_kwh / p_stc_kwp
