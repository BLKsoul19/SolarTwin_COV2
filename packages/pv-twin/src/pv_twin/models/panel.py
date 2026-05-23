from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PanelParameters(BaseModel):
    """Parametros STC de un modulo FV del catalogo SolarTwin CO."""

    panel_id: str
    pmax_stc_w: float = Field(..., gt=0, description="Potencia maxima STC [W]")
    voc_stc_v: float = Field(..., gt=0, description="Tension Voc STC [V]")
    isc_stc_a: float = Field(..., gt=0, description="Corriente Isc STC [A]")
    vmpp_stc_v: float = Field(..., gt=0, description="Tension Vmpp STC [V]")
    impp_stc_a: float = Field(..., gt=0, description="Corriente Impp STC [A]")
    gamma_pmax_per_c: float = Field(..., lt=0, description="Coeficiente Pmax [1/C]")
    beta_voc_per_c: float = Field(..., lt=0, description="Coeficiente Voc [1/C]")
    alpha_isc_per_c: float = Field(..., gt=0, description="Coeficiente Isc [1/C]")
    noct_c: float = Field(..., gt=0, description="NOCT [C]")
    cells_in_series: int = Field(..., gt=0, description="Celdas en serie")
    technology: Literal["TOPCon", "HPBC", "PERC", "HJT", "poli_PERC"]
    tier: Literal[1, 2] = 1

    @field_validator("panel_id")
    @classmethod
    def panel_id_must_be_normalized(cls, value: str) -> str:
        if value != value.lower() or " " in value:
            raise ValueError("panel_id debe estar en minusculas y sin espacios")
        return value
