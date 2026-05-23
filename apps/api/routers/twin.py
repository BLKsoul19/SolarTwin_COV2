from fastapi import APIRouter, HTTPException
from pv_twin.models import PanelCatalogRepository, PanelNotFoundError, PanelParameters
from pv_twin.simulator import get_cell_temperature

from apps.api.schemas.twin import CellTemperatureRequest, CellTemperatureResponse

router = APIRouter(prefix="/api/v1/twin", tags=["twin"])


def get_panel_catalog() -> PanelCatalogRepository:
    return PanelCatalogRepository()


@router.get("/panels", response_model=list[PanelParameters])
def list_panels() -> list[PanelParameters]:
    return get_panel_catalog().list_all()


@router.get("/panels/{panel_id}", response_model=PanelParameters)
def get_panel(panel_id: str) -> PanelParameters:
    try:
        return get_panel_catalog().get_by_id(panel_id)
    except PanelNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/cell-temperature", response_model=CellTemperatureResponse)
def calculate_cell_temperature(request: CellTemperatureRequest) -> CellTemperatureResponse:
    t_cell_c = get_cell_temperature(
        g_poa_w_m2=request.g_poa_w_m2,
        t_amb_c=request.t_amb_c,
        noct_c=request.noct_c,
    )
    return CellTemperatureResponse(
        g_poa_w_m2=request.g_poa_w_m2,
        t_amb_c=request.t_amb_c,
        noct_c=request.noct_c,
        t_cell_c=t_cell_c,
    )
