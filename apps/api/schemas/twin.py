from pydantic import BaseModel, Field


class CellTemperatureRequest(BaseModel):
    """Request payload for the cell temperature endpoint."""

    g_poa_w_m2: float = Field(..., ge=0, description="Plane-of-array irradiance [W/m2]")
    t_amb_c: float = Field(..., description="Ambient temperature [C]")
    noct_c: float = Field(..., gt=0, description="Nominal operating cell temperature [C]")


class CellTemperatureResponse(CellTemperatureRequest):
    """Response payload for the cell temperature endpoint."""

    t_cell_c: float = Field(..., description="Cell temperature [C]")


class IVCurvePointResponse(BaseModel):
    """Single point in an I-V response."""

    v_v: float = Field(..., description="Voltage [V]")
    i_a: float = Field(..., description="Current [A]")
    p_w: float = Field(..., description="Power [W]")


class PVCurvePointResponse(BaseModel):
    """Single point in a P-V response."""

    v_v: float = Field(..., description="Voltage [V]")
    p_w: float = Field(..., description="Power [W]")


class IVCurveResponse(BaseModel):
    """I-V curve response with key SDM operating points."""

    panel_id: str
    g_poa_w_m2: float
    t_cell_c: float
    v_oc_v: float
    i_sc_a: float
    v_mpp_v: float
    i_mpp_a: float
    p_mpp_w: float
    points: list[IVCurvePointResponse]


class PVCurveResponse(BaseModel):
    """P-V curve response with key SDM operating points."""

    panel_id: str
    g_poa_w_m2: float
    t_cell_c: float
    v_oc_v: float
    i_sc_a: float
    v_mpp_v: float
    i_mpp_a: float
    p_mpp_w: float
    points: list[PVCurvePointResponse]
