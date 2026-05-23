from pydantic import BaseModel, Field


class CellTemperatureRequest(BaseModel):
    """Request payload for the cell temperature endpoint."""

    g_poa_w_m2: float = Field(..., ge=0, description="Plane-of-array irradiance [W/m2]")
    t_amb_c: float = Field(..., description="Ambient temperature [C]")
    noct_c: float = Field(..., gt=0, description="Nominal operating cell temperature [C]")


class CellTemperatureResponse(CellTemperatureRequest):
    """Response payload for the cell temperature endpoint."""

    t_cell_c: float = Field(..., description="Cell temperature [C]")
