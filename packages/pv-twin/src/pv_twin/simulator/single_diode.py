from dataclasses import dataclass
from functools import cached_property
from typing import Any, cast

import numpy as np
from pvlib import pvsystem
from pvlib.ivtools.sdm import fit_cec_sam

from pv_twin.models import PanelParameters

TECHNOLOGY_TO_CEC_CELL_TYPE: dict[str, str] = {
    "TOPCon": "monoSi",
    "HPBC": "monoSi",
    "PERC": "monoSi",
    "HJT": "monoSi",
    "poli_PERC": "polySi",
}


@dataclass(frozen=True)
class CECParameters:
    """CEC single diode model parameters at STC."""

    i_l_ref_a: float
    i_o_ref_a: float
    r_s_ohm: float
    r_sh_ref_ohm: float
    a_ref_v: float
    adjust_pct: float
    alpha_sc_a_per_c: float


@dataclass(frozen=True)
class IVCurvePoint:
    """Single point in an I-V curve."""

    v_v: float
    i_a: float
    p_w: float


@dataclass(frozen=True)
class IVCurveResult:
    """Calculated I-V curve and key operating points."""

    panel_id: str
    g_poa_w_m2: float
    t_cell_c: float
    v_oc_v: float
    i_sc_a: float
    v_mpp_v: float
    i_mpp_a: float
    p_mpp_w: float
    points: list[IVCurvePoint]


def get_cec_cell_type(technology: str) -> str:
    """Map SolarTwin technology labels to SAM/CEC cell type labels."""
    try:
        return TECHNOLOGY_TO_CEC_CELL_TYPE[technology]
    except KeyError as error:
        raise ValueError(f"Unsupported panel technology: {technology}") from error


class SolarPanelTwin:
    """Single module digital twin based on the CEC single diode model."""

    def __init__(self, panel: PanelParameters) -> None:
        self.panel = panel

    def get_iv_curve(
        self,
        g_poa_w_m2: float,
        t_cell_c: float,
        n_points: int = 100,
    ) -> IVCurveResult:
        """Calculate the I-V curve for a panel under POA irradiance and cell temperature."""
        self._validate_curve_inputs(
            g_poa_w_m2=g_poa_w_m2,
            t_cell_c=t_cell_c,
            n_points=n_points,
        )
        photocurrent, saturation_current, resistance_series, resistance_shunt, nnsvth = (
            self._calcparams_cec(g_poa_w_m2=g_poa_w_m2, t_cell_c=t_cell_c)
        )
        solution = pvsystem.singlediode(
            photocurrent,
            saturation_current,
            resistance_series,
            resistance_shunt,
            nnsvth,
            method="lambertw",
        )

        v_oc_v = self._solution_float(solution, "v_oc")
        i_sc_a = self._solution_float(solution, "i_sc")
        v_mpp_v = self._solution_float(solution, "v_mp")
        i_mpp_a = self._solution_float(solution, "i_mp")
        p_mpp_w = self._solution_float(solution, "p_mp")
        voltage_values = np.linspace(0.0, v_oc_v, n_points)
        current_values_raw = pvsystem.i_from_v(
            voltage_values,
            photocurrent,
            saturation_current,
            resistance_series,
            resistance_shunt,
            nnsvth,
            method="lambertw",
        )
        current_values = np.maximum(np.asarray(current_values_raw, dtype=float), 0.0)
        power_values = voltage_values * current_values

        if not np.all(np.isfinite(current_values)) or not np.all(np.isfinite(power_values)):
            raise RuntimeError("SDM curve calculation produced non-finite values")

        points = [
            IVCurvePoint(v_v=float(v_v), i_a=float(i_a), p_w=float(p_w))
            for v_v, i_a, p_w in zip(voltage_values, current_values, power_values, strict=True)
        ]
        return IVCurveResult(
            panel_id=self.panel.panel_id,
            g_poa_w_m2=g_poa_w_m2,
            t_cell_c=t_cell_c,
            v_oc_v=v_oc_v,
            i_sc_a=i_sc_a,
            v_mpp_v=v_mpp_v,
            i_mpp_a=i_mpp_a,
            p_mpp_w=p_mpp_w,
            points=points,
        )

    @cached_property
    def cec_parameters(self) -> CECParameters:
        """Fit CEC SDM parameters from catalog STC values."""
        alpha_sc_a_per_c = self.panel.isc_stc_a * self.panel.alpha_isc_per_c
        beta_voc_v_per_c = self.panel.voc_stc_v * self.panel.beta_voc_per_c
        gamma_pmp_pct_per_c = self.panel.gamma_pmax_per_c * 100.0
        try:
            i_l_ref_a, i_o_ref_a, r_s_ohm, r_sh_ref_ohm, a_ref_v, adjust_pct = fit_cec_sam(
                celltype=get_cec_cell_type(self.panel.technology),
                v_mp=self.panel.vmpp_stc_v,
                i_mp=self.panel.impp_stc_a,
                v_oc=self.panel.voc_stc_v,
                i_sc=self.panel.isc_stc_a,
                alpha_sc=alpha_sc_a_per_c,
                beta_voc=beta_voc_v_per_c,
                gamma_pmp=gamma_pmp_pct_per_c,
                cells_in_series=self.panel.cells_in_series,
            )
        except ImportError as error:
            raise RuntimeError("NREL-PySAM is required to fit CEC parameters") from error
        except RuntimeError as error:
            raise RuntimeError(f"CEC parameter fit failed for {self.panel.panel_id}") from error

        return CECParameters(
            i_l_ref_a=float(i_l_ref_a),
            i_o_ref_a=float(i_o_ref_a),
            r_s_ohm=float(r_s_ohm),
            r_sh_ref_ohm=float(r_sh_ref_ohm),
            a_ref_v=float(a_ref_v),
            adjust_pct=float(adjust_pct),
            alpha_sc_a_per_c=alpha_sc_a_per_c,
        )

    def _calcparams_cec(
        self,
        g_poa_w_m2: float,
        t_cell_c: float,
    ) -> tuple[Any, Any, Any, Any, Any]:
        cec = self.cec_parameters
        return cast(
            tuple[Any, Any, Any, Any, Any],
            pvsystem.calcparams_cec(
                effective_irradiance=g_poa_w_m2,
                temp_cell=t_cell_c,
                alpha_sc=cec.alpha_sc_a_per_c,
                a_ref=cec.a_ref_v,
                I_L_ref=cec.i_l_ref_a,
                I_o_ref=cec.i_o_ref_a,
                R_sh_ref=cec.r_sh_ref_ohm,
                R_s=cec.r_s_ohm,
                Adjust=cec.adjust_pct,
            ),
        )

    @staticmethod
    def _solution_float(solution: dict[str, Any], key: str) -> float:
        return float(solution[key])

    @staticmethod
    def _validate_curve_inputs(g_poa_w_m2: float, t_cell_c: float, n_points: int) -> None:
        if not 10.0 <= g_poa_w_m2 <= 1400.0:
            raise ValueError("g_poa_w_m2 must be between 10 and 1400")
        if not -10.0 <= t_cell_c <= 85.0:
            raise ValueError("t_cell_c must be between -10 and 85")
        if not 10 <= n_points <= 500:
            raise ValueError("n_points must be between 10 and 500")
