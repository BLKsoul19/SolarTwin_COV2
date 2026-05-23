from pv_twin.kpi import capacity_utilization_factor, performance_ratio, specific_yield


def test_performance_ratio() -> None:
    assert performance_ratio(e_ac_kwh=1500.0, p_stc_kwp=1.0, h_poa_kwh_m2=2000.0) == 0.75


def test_capacity_utilization_factor() -> None:
    assert capacity_utilization_factor(e_ac_kwh=120.0, p_stc_kwp=1.0, hours=1000.0) == 0.12


def test_specific_yield() -> None:
    assert specific_yield(e_ac_kwh=990.0, p_stc_kwp=3.0) == 330.0
