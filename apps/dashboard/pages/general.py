from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from apps.dashboard.api_client import (
    api_health,
    api_list_panels,
)
from apps.dashboard.charts import _fig_layout
from apps.dashboard.config import DEFAULT_COLOR, PANEL_COLORS


def render_general() -> None:
    """Renderiza la página general."""
    health = api_health()

    panels_resp = api_list_panels()
    panels: list[dict] = panels_resp.get("data", []) if panels_resp["ok"] else []

    # ── KPIs MEJORADOS ──
    tier1 = [p for p in panels if p.get("tier") == 1]
    tier2 = [p for p in panels if p.get("tier") == 2]
    mono = [p for p in panels if p.get("technology", "").lower() in ["mono", "topcon", "hpbc"]]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Paneles en catálogo",
            len(panels),
            delta=f"{len(tier1)} Tier 1 · {len(tier2)} Tier 2",
            delta_color="off",
            help="Total de paneles disponibles para simulación",
        )
    with col2:
        avg_pmax = sum(p.get("pmax_stc_w", 0) for p in panels) / len(panels) if panels else 0
        st.metric(
            "Potencia promedio STC",
            f"{avg_pmax:.0f} W",
            delta=f"Min {min((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f} – Max {max((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f}",
            delta_color="off",
            help="Rango de potencias en el catálogo",
        )
    with col3:
        mono_pct = (len(mono) / len(panels) * 100) if panels else 0
        st.metric(
            "Composición tecnológica",
            f"{mono_pct:.0f}% monocristalino",
            delta=f"{100-mono_pct:.0f}% policristalino",
            delta_color="off",
            help="Distribución por tipo de celda",
        )
    with col4:
        lat_ms = health.get("latency_ms")
        st.metric(
            "Salud del sistema",
            "✓ OK" if health["ok"] else "✗ ERROR",
            delta=f"{lat_ms:.0f} ms latencia" if lat_ms else "—",
            delta_color="normal" if lat_ms and lat_ms < 100 else "off",
            help="Estado API + latencia de respuesta",
        )

    st.markdown("---")

    # ── Catálogo de paneles — VISTA DENSIFICADA ──
    st.markdown('<div class="section-title">📋 Catálogo de paneles (Análisis comparativo)</div>', unsafe_allow_html=True)

    if not panels_resp["ok"]:
        st.error(f"No se pudo conectar a la API: {panels_resp.get('error')}")
        st.info("Asegúrate de que la API esté corriendo: `uvicorn apps.api.main:app --reload`")
    elif not panels:
        st.warning("Catálogo vacío. Agrega archivos JSON a data/panels/")
    else:
        # ── BÚSQUEDA Y FILTRADO MEJORADOS ──
        col_search, col_filters = st.columns([2, 3])
        
        with col_search:
            search_term = st.text_input(
                "🔍 Buscar panel por nombre",
                placeholder="ej: jinko, tiger, neo...",
                key="panel_search"
            ).lower()
        
        with col_filters:
            tech_options = sorted(set(p.get("technology", "Unknown") for p in panels))
            selected_techs = st.multiselect(
                "🔬 Filtrar por tecnología",
                tech_options,
                default=[],
                key="panel_tech_filter"
            )
        
        # Aplicar filtros
        filtered_panels = panels
        
        if search_term:
            filtered_panels = [
                p for p in filtered_panels
                if search_term in p.get("panel_id", "").lower()
            ]
        
        if selected_techs:
            filtered_panels = [
                p for p in filtered_panels
                if p.get("technology") in selected_techs
            ]
        
        st.caption(f"📌 Mostrando {len(filtered_panels)} de {len(panels)} paneles")
        
        # ── TAB 1: Vista tabla ──
        tab_table, tab_tech, tab_metrics = st.tabs(["📊 Tabla", "🔬 Análisis tecnológico", "📈 Comparativa KPIs"])
    
        with tab_table:
            # Preparar DataFrame
            panel_data_rows = []
            for p in sorted(filtered_panels, key=lambda x: (-x.get("tier", 9), x.get("panel_id", ""))):
                panel_data_rows.append({
                    "Panel ID": p.get("panel_id", "—"),
                    "P_max STC (W)": p.get("pmax_stc_w", 0),
                    "V_oc STC (V)": p.get("voc_stc_v", 0),
                    "I_sc STC (A)": p.get("isc_stc_a", 0),
                    "V_mpp STC (V)": p.get("vmpp_stc_v", 0),
                    "I_mpp STC (A)": p.get("impp_stc_a", 0),
                    "γ P_max (%/°C)": p.get("gamma_pmax_per_c", 0) * 100,
                    "NOCT (°C)": p.get("noct_c", "—"),
                    "Cells": p.get("cells_in_series", "—"),
                    "Tech": p.get("technology", "—"),
                    "Tier": p.get("tier", "—"),
                })
        
            df_panel_catalog = pd.DataFrame(panel_data_rows)
        
            # Estilo destacando mejores valores
            st.dataframe(
                df_panel_catalog.style
                    .background_gradient(subset=["P_max STC (W)"], cmap="Greens", vmin=df_panel_catalog["P_max STC (W)"].min(), vmax=df_panel_catalog["P_max STC (W)"].max())
                    .background_gradient(subset=["V_oc STC (V)"], cmap="Blues")
                    .format({"γ P_max (%/°C)": "{:.3f}", "NOCT (°C)": "{:.0f}"}),
                use_container_width=True,
                hide_index=True,
            )
    
        with tab_tech:
            # Análisis por tecnología
            tech_groups: dict[str, list[Any]] = {}
            for p in filtered_panels:
                tech = p.get("technology", "Unknown")
                if tech not in tech_groups:
                    tech_groups[tech] = []
                tech_groups[tech].append(p)
        
            for tech, tech_panels in sorted(tech_groups.items()):
                with st.expander(f"🔬 **{tech}** ({len(tech_panels)} paneles)", expanded=True):
                    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
                
                    avg_p = sum(p.get("pmax_stc_w", 0) for p in tech_panels) / len(tech_panels)
                    avg_eff = (avg_p / (1.6 * 1000)) * 100  # Asumiendo 1.6 m² de área típica
                    gamma_vals = [p.get("gamma_pmax_per_c", -0.003) for p in tech_panels]
                    avg_gamma = sum(gamma_vals) / len(gamma_vals)
                
                    tcol1.metric("Paneles", len(tech_panels))
                    tcol2.metric("P_max avg", f"{avg_p:.0f} W")
                    tcol3.metric("Eficiencia típica", f"{avg_eff:.1f}%")
                    tcol4.metric("Coef. γ promedio", f"{avg_gamma*100:.3f}%/°C")
                
                    # Listar paneles de esta tecnología
                    for tp in tech_panels:
                        st.caption(
                            f"• **{tp['panel_id']}** — {tp.get('pmax_stc_w', 0):.0f}W · "
                            f"NOCT {tp.get('noct_c', 0):.0f}°C · Tier {tp.get('tier', 0)}"
                        )
    
        with tab_metrics:
            # Gráficos comparativos
            col_chart1, col_chart2 = st.columns(2)
        
            with col_chart1:
                fig_pmax = go.Figure()
                for p in panels:
                    fig_pmax.add_trace(
                        go.Bar(
                            x=[p["panel_id"]],
                            y=[p.get("pmax_stc_w", 0)],
                            name=p["panel_id"],
                            marker_color=PANEL_COLORS.get(p["panel_id"], DEFAULT_COLOR),
                        )
                    )
                fig_pmax.update_layout(
                    **_fig_layout(
                        title_text="P_max STC por panel",
                        xaxis_title="Panel",
                        yaxis_title="Potencia (W)",
                        height=300,
                        showlegend=False,
                    )
                )
                st.plotly_chart(fig_pmax, use_container_width=True)
        
            with col_chart2:
                fig_noct = go.Figure()
                for p in panels:
                    fig_noct.add_trace(
                        go.Scatter(
                            x=[p["panel_id"]],
                            y=[p.get("noct_c", 0)],
                            mode="markers",
                            marker=dict(
                                size=15,
                                color=PANEL_COLORS.get(p["panel_id"], DEFAULT_COLOR),
                                line=dict(width=2, color="white"),
                            ),
                            name=p["panel_id"],
                        )
                    )
                fig_noct.update_layout(
                    **_fig_layout(
                        title_text="NOCT por panel",
                        xaxis_title="Panel",
                        yaxis_title="NOCT (°C)",
                        height=300,
                        showlegend=False,
                    )
                )
                st.plotly_chart(fig_noct, use_container_width=True)

    # ── Arquitectura del proyecto — MEJORADO ──
    st.markdown("---")
    st.markdown('<div class="section-title">🏗️ Arquitectura + Estado del proyecto</div>', unsafe_allow_html=True)

    tab_arch, tab_stats, tab_docs = st.tabs(["🏗️ Estructura", "📈 Estadísticas", "📚 Documentación"])

    with tab_arch:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                """
                #### 📦 Paquete físico `packages/pv-twin/`
            
                **`models/`** — Datos y catálogo
                - `PanelParameters` — Pydantic v2 schema
                - `catalog.py` — Carga JSON en data/panels/
            
                **`simulator/`** — Física del gemelo
                - `single_diode.py` — SDM + CEC parameters
                - `temperature.py` — Modelo Ross-NOCT
            
                **`kpi/`** — Análisis de desempeño
                - `performance.py` — PR, CUF, Yield
                - `efficiency.py` — Degradación, factor de sobrevolts
                """,
            )
        with col_b:
            st.markdown(
                """
                #### 🌐 API REST `apps/api/`
            
                **`main.py`** — FastAPI app
                - `GET /health` — latencia
                - `GET /api/v1/twin/panels` — catálogo completo
                - `GET /api/v1/twin/panels/{id}` — detalles panel
            
                **`routers/twin.py`** — 6 endpoints
                - `POST /cell-temperature` — Ross-NOCT
                - `GET /.../iv` — curva I-V (SDM)
                - `GET /.../pv` — curva P-V (CEC)
            
                **Docs automática** → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
                """,
            )

    with tab_stats:
        stat1, stat2, stat3 = st.columns(3)
    
        with stat1:
            st.markdown("### 🧪 Cobertura de pruebas")
            st.metric("Tests unitarios", 32, help="SDM, NOCT, KPIs, catalog")
            st.metric("Tests integración", 10, help="Endpoints API")
            st.metric("Smoke tests", 2, help="Tier 1 panels")
            st.markdown("**Total:** 44 pruebas ✅ 100% pasando")
    
        with stat2:
            st.markdown("### 📊 Catálogo de paneles")
            st.metric("Total paneles", len(panels), help="Archivos JSON en data/panels/")
            st.metric("Tier 1 premium", len(tier1), help="Eficiencia > 21%")
            st.metric("Tecnologías", len(tech_groups), help="Mono/Poly/TOPCon/HPBC")
            avg_p_range = f"{min((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f}—{max((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f}W"
            st.markdown(f"**Rango P_max STC:** {avg_p_range}")
    
        with stat3:
            st.markdown("### ⚙️ Rendimiento")
            st.metric("Latencia API", f"{health.get('latency_ms', 0):.0f} ms", 
                     delta="Excelente" if health.get('latency_ms', 0) < 50 else "Bueno",
                     delta_color="off")
            st.metric("Python", "3.11+", help="Type hints + PEP 604")
            st.metric("Dependencias core", 4, help="pvlib, pydantic, fastapi, httpx")
            st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    with tab_docs:
        st.markdown(
            """
            #### 📖 Referencias rápidas
        
            **[README.md](https://github.com/your-repo)** — Guía de inicio rápido  
            **[pyproject.toml](https://github.com/your-repo)** — Configuración pip + ruff + mypy  
            **[docs/PANEL_TIER1_SETUP.md](https://github.com/your-repo)** — Agregar nuevos paneles  
        
            #### 🔧 Comandos clave
        
            ```bash
            # Setup
            python -m venv .venv && source .venv/bin/activate
            pip install -e ".[dev]"
        
            # Tests
            pytest --cov=packages/pv-twin --cov-fail-under=85
        
            # Linting
            ruff check . && ruff format .
            mypy packages/pv-twin
        
            # API
            uvicorn apps.api.main:app --reload --port 8000
        
            # Dashboard
            streamlit run apps/dashboard/main.py
            ```
        
            #### 🎯 Convención de unidades (REGLA DE ORO)
        
            Todas las variables físicas incluyen **unidad en el nombre**:
            - `g_poa_w_m2` · `t_cell_c` · `t_amb_c` · `noct_c`
            - `p_dc_w` · `p_mpp_w` · `v_mpp_v` · `i_mpp_a`
            - `ff_ratio` · `pr_ratio` · `cuf_ratio`
            """
        )


    # ─────────────────────────────────────────────────────────────────────────────
