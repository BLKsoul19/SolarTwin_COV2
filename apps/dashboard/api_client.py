"""Cliente HTTP cacheado para los endpoints FastAPI de SolarTwin."""

from __future__ import annotations

import time
from typing import Any

import httpx
import streamlit as st

from apps.dashboard.config import API_BASE_URL, REQUEST_TIMEOUT


@st.cache_data(ttl=30, show_spinner=False)
def api_health() -> dict[str, Any]:
    """GET /health — verifica estado del servidor."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json(), "latency_ms": resp.elapsed.total_seconds() * 1000}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "latency_ms": None}


@st.cache_data(ttl=60, show_spinner=False)
def api_list_panels() -> dict[str, Any]:
    """GET /api/v1/twin/panels — lista todos los paneles del catálogo."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": []}


@st.cache_data(ttl=60, show_spinner=False)
def api_get_panel(panel_id: str) -> dict[str, Any]:
    """GET /api/v1/twin/panels/{panel_id} — detalles de un panel específico."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}}


@st.cache_data(ttl=10, show_spinner=False)
def api_cell_temperature(
    g_poa_w_m2: float,
    t_amb_c: float,
    noct_c: float,
) -> dict[str, Any]:
    """POST /api/v1/twin/cell-temperature — modelo Ross-NOCT."""
    try:
        resp = httpx.post(
            f"{API_BASE_URL}/api/v1/twin/cell-temperature",
            json={"g_poa_w_m2": g_poa_w_m2, "t_amb_c": t_amb_c, "noct_c": noct_c},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}}


@st.cache_data(ttl=10, show_spinner=False)
def api_iv_curve(
    panel_id: str,
    g_poa_w_m2: float,
    t_cell_c: float,
    n_points: int = 100,
) -> dict[str, Any]:
    """GET /api/v1/twin/panels/{panel_id}/iv — curva I-V (SDM/CEC)."""
    try:
        t0 = time.perf_counter()
        resp = httpx.get(
            f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}/iv",
            params={"g_poa_w_m2": g_poa_w_m2, "t_cell_c": t_cell_c, "n_points": n_points},
            timeout=REQUEST_TIMEOUT,
        )
        latency = (time.perf_counter() - t0) * 1000
        resp.raise_for_status()
        return {"ok": True, "data": resp.json(), "latency_ms": round(latency, 1)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}, "latency_ms": None}


@st.cache_data(ttl=10, show_spinner=False)
def api_pv_curve(
    panel_id: str,
    g_poa_w_m2: float,
    t_cell_c: float,
    n_points: int = 100,
) -> dict[str, Any]:
    """GET /api/v1/twin/panels/{panel_id}/pv — curva P-V (SDM/CEC)."""
    try:
        resp = httpx.get(
            f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}/pv",
            params={"g_poa_w_m2": g_poa_w_m2, "t_cell_c": t_cell_c, "n_points": n_points},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}}

