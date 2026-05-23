def get_cell_temperature(g_poa_w_m2: float, t_amb_c: float, noct_c: float) -> float:
    """Calculate PV cell temperature with the Ross NOCT model."""
    if g_poa_w_m2 < 0:
        raise ValueError("g_poa_w_m2 must be greater than or equal to 0")
    if noct_c <= 0:
        raise ValueError("noct_c must be greater than 0")
    return t_amb_c + g_poa_w_m2 * (noct_c - 20.0) / 800.0
