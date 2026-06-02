from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pv_twin.models import PanelCatalogRepository, PanelNotFoundError, PanelParameters
from pv_twin.simulator import (
    IVCurveResult,
    SolarPanelTwin,
    get_cell_temperature,
    get_cell_temperature_faiman,
)

from apps.api.schemas.twin import (
    CellTemperatureFaimanRequest,
    CellTemperatureFaimanResponse,
    CellTemperatureRequest,
    CellTemperatureResponse,
    IVCurvePointResponse,
    IVCurveResponse,
    PVCurvePointResponse,
    PVCurveResponse,
)

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


@router.post("/cell-temperature/faiman", response_model=CellTemperatureFaimanResponse)
def calculate_cell_temperature_faiman(
    request: CellTemperatureFaimanRequest,
) -> CellTemperatureFaimanResponse:
    t_cell_c = get_cell_temperature_faiman(
        g_poa_w_m2=request.g_poa_w_m2,
        t_amb_c=request.t_amb_c,
        wind_speed_m_s=request.wind_speed_m_s,
        u0=request.u0,
        u1=request.u1,
    )
    return CellTemperatureFaimanResponse(
        g_poa_w_m2=request.g_poa_w_m2,
        t_amb_c=request.t_amb_c,
        wind_speed_m_s=request.wind_speed_m_s,
        u0=request.u0,
        u1=request.u1,
        t_cell_c=t_cell_c,
    )


@router.get("/panels/{panel_id}/iv", response_model=IVCurveResponse)
def get_iv_curve(
    panel_id: str,
    g_poa_w_m2: Annotated[float, Query(ge=10.0, le=1400.0)],
    t_cell_c: Annotated[float, Query(ge=-10.0, le=85.0)],
    n_points: Annotated[int, Query(ge=10, le=500)] = 100,
) -> IVCurveResponse:
    result = _calculate_iv_curve(
        panel_id=panel_id,
        g_poa_w_m2=g_poa_w_m2,
        t_cell_c=t_cell_c,
        n_points=n_points,
    )
    return _to_iv_response(result)


@router.get("/panels/{panel_id}/pv", response_model=PVCurveResponse)
def get_pv_curve(
    panel_id: str,
    g_poa_w_m2: Annotated[float, Query(ge=10.0, le=1400.0)],
    t_cell_c: Annotated[float, Query(ge=-10.0, le=85.0)],
    n_points: Annotated[int, Query(ge=10, le=500)] = 100,
) -> PVCurveResponse:
    result = _calculate_iv_curve(
        panel_id=panel_id,
        g_poa_w_m2=g_poa_w_m2,
        t_cell_c=t_cell_c,
        n_points=n_points,
    )
    return _to_pv_response(result)


def _calculate_iv_curve(
    panel_id: str,
    g_poa_w_m2: float,
    t_cell_c: float,
    n_points: int,
) -> IVCurveResult:
    try:
        panel = get_panel_catalog().get_by_id(panel_id)
        return SolarPanelTwin(panel).get_iv_curve(
            g_poa_w_m2=g_poa_w_m2,
            t_cell_c=t_cell_c,
            n_points=n_points,
        )
    except PanelNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


def _to_iv_response(result: IVCurveResult) -> IVCurveResponse:
    return IVCurveResponse(
        panel_id=result.panel_id,
        g_poa_w_m2=result.g_poa_w_m2,
        t_cell_c=result.t_cell_c,
        v_oc_v=result.v_oc_v,
        i_sc_a=result.i_sc_a,
        v_mpp_v=result.v_mpp_v,
        i_mpp_a=result.i_mpp_a,
        p_mpp_w=result.p_mpp_w,
        points=[
            IVCurvePointResponse(v_v=point.v_v, i_a=point.i_a, p_w=point.p_w)
            for point in result.points
        ],
    )


def _to_pv_response(result: IVCurveResult) -> PVCurveResponse:
    return PVCurveResponse(
        panel_id=result.panel_id,
        g_poa_w_m2=result.g_poa_w_m2,
        t_cell_c=result.t_cell_c,
        v_oc_v=result.v_oc_v,
        i_sc_a=result.i_sc_a,
        v_mpp_v=result.v_mpp_v,
        i_mpp_a=result.i_mpp_a,
        p_mpp_w=result.p_mpp_w,
        points=[PVCurvePointResponse(v_v=point.v_v, p_w=point.p_w) for point in result.points],
    )
