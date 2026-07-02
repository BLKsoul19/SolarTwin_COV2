# SolarTwin CO - Estrategia de Integración Dashboard
## Análisis Técnico y Propuesta de Arquitectura

**Fecha**: 2026-05-25  
**Sprint**: Post-Sprint 2  
**Alcance**: MVP Dashboard integrado con núcleo de simulación física

---

## 1. Estado Actual de la Plataforma

### 1.1 Capacidades del Backend

#### API REST (FastAPI)
```
Endpoint                                    Datos            Status
─────────────────────────────────────────────────────────────────
GET /health                                 Status API       ✅
GET /api/v1/twin/panels                     Lista paneles    ✅
GET /api/v1/twin/panels/{panel_id}          Parámetros STC   ✅
POST /api/v1/twin/cell-temperature          T_cell (NOCT)    ✅
GET /api/v1/twin/panels/{panel_id}/iv       Curva I-V        ✅
GET /api/v1/twin/panels/{panel_id}/pv       Curva P-V        ✅
```

#### Modelos Disponibles
```python
PanelParameters
├─ panel_id: str
├─ pmax_stc_w: float
├─ voc_stc_v, isc_stc_a
├─ vmpp_stc_v, impp_stc_a
├─ gamma_pmax_per_c, beta_voc_per_c, alpha_isc_per_c
├─ noct_c: float
├─ technology: str
└─ tier: int

IVCurveResponse
├─ panel_id: str
├─ g_poa_w_m2, t_cell_c
├─ v_oc_v, i_sc_a, v_mpp_v, i_mpp_a, p_mpp_w
└─ points: list[IVCurvePoint]  # [(v_v, i_a, p_w), ...]

PVCurveResponse
├─ panel_id: str
├─ g_poa_w_m2, t_cell_c
├─ Parámetros operacionales
└─ points: list[PVCurvePoint]  # [(v_v, p_w), ...]
```

#### Datos en Catálogo
```
Paneles disponibles: 3
├─ generic_poly_330 (Tier 2, poli-PERC, 330W)
├─ jinko_tiger_neo_580 (Tier 1, TOPCon, 580W)
└─ longi_himo_x6_580 (Tier 1, HPBC, 580W)
```

---

## 2. Análisis de Opciones de Frontend

### 2.1 Opción A: Streamlit (RECOMENDADO para MVP)

| Aspecto | Evaluación |
|---------|-----------|
| **Setup** | ✅ Ultra rápido (~2 horas) |
| **Curva aprendizaje** | ✅ Python puro, sin JavaScript |
| **Visualizaciones** | ✅ Plotly, Matplotlib, Altair integrados |
| **Interactividad** | ⚠️ Básica (widgets, callbacks limitados) |
| **Escalabilidad** | ⚠️ No ideal para 1000+ usuarios simultáneos |
| **Personalización CSS** | ❌ Limitada |
| **Producción** | ⚠️ Requireable (Streamlit Cloud, Docker) |
| **Tiempo implementación** | ✅ 1-2 sprints |
| **Mantención** | ✅ Fácil (mismo lenguaje backend) |

**Caso de uso**: MVP interno, demostración de cliente, dashboards de análisis

**Ventajas**:
```python
import streamlit as st
import plotly.graph_objects as go

# Código mínimo para visualización profesional
response = requests.get("http://localhost:8000/api/v1/twin/panels/{panel}/iv")
data = response.json()

fig = go.Figure()
fig.add_trace(go.Scatter(x=[p['v_v'] for p in data['points']],
                         y=[p['i_a'] for p in data['points']]))
st.plotly_chart(fig)
```

---

### 2.2 Opción B: React + TypeScript (Para Producción)

| Aspecto | Evaluación |
|---------|-----------|
| **Setup** | ⚠️ Complejo (Vite, tsconfig, eslint) |
| **Curva aprendizaje** | ⚠️ TypeScript + React (más tiempo) |
| **Visualizaciones** | ✅ Recharts, Plotly.js, D3.js |
| **Interactividad** | ✅ Excelente (estado complejo, animaciones) |
| **Escalabilidad** | ✅ Ideal para miles de usuarios |
| **Personalización CSS** | ✅ Ilimitada (TailwindCSS, Emotion) |
| **Producción** | ✅ Deployment profesional |
| **Tiempo implementación** | ❌ 2-3 sprints |
| **Mantención** | ⚠️ Requiere desarrollador frontend |

**Caso de uso**: Plataforma SaaS, aplicación web escalable, multi-tenant

**Arquitectura**:
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── SimulationPanel.tsx
│   │   └── ComparisonView.tsx
│   ├── components/
│   │   ├── IVCurveChart.tsx
│   │   ├── PVCurveChart.tsx
│   │   └── ParameterControls.tsx
│   ├── hooks/
│   │   └── useSolarTwinAPI.ts
│   └── main.tsx
├── vite.config.ts
└── tailwind.config.js
```

---

### 2.3 Opción C: Jupyter Notebook (Solo experimentación)

| Aspecto | Evaluación |
|---------|-----------|
| **Setup** | ✅ Trivial |
| **Visualizaciones** | ✅ Excelente (matplotlib, plotly) |
| **Interactividad** | ⚠️ Widgets limitados |
| **Producción** | ❌ No apto |
| **Colaboración** | ✅ Git-friendly con nbstripout |

**Caso de uso**: Análisis exploratorio, papers académicos

---

## 3. Propuesta: MVP Dashboard con Streamlit

### 3.1 Rationale

```
Objetivo Sprint 3:  Validar concepto de dashboard
Timeline:           1-2 sprints
Usuarios iniciales: 10-50 (interno + demostración)
Recursos:           1 desarrollador Full-Stack (ya existe)
Riesgo técnico:     Bajo (tech stack conocido)
```

**Decisión**: Streamlit MVP + React para Sprint 5 (post-producción)

---

### 3.2 Estructura Propuesta

```
SolarTwin_COV2/
├── apps/
│   ├── api/              (FastAPI - backend físico) ← YA EXISTE
│   ├── dashboard/        (Streamlit - frontend MVP) ← NUEVO
│   │   ├── pages/
│   │   │   ├── home.py
│   │   │   ├── simulation.py
│   │   │   ├── comparison.py
│   │   │   └── analysis.py
│   │   ├── components/
│   │   │   ├── charts.py
│   │   │   ├── inputs.py
│   │   │   └── stats.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── .streamlit/config.toml
│   └── web/              (React - frontend Sprint 5) ← FUTURO
│       └── ...
├── docs/
│   └── DASHBOARD_ARCHITECTURE.md
└── ...
```

---

## 4. Componentes del Dashboard MVP

### 4.1 Página Home - Overview

```
┌─────────────────────────────────────────────────────────┐
│  SolarTwin CO - Digital Twin Dashboard                  │
│  Gemelo Digital Fotovoltaico para Colombia              │
└─────────────────────────────────────────────────────────┘

Métricas KPI (3 columnas)
┌──────────────┬──────────────┬──────────────┐
│ Paneles      │ API Status   │ Last Update  │
│ 3 Tier 1-2   │ ✅ Online    │ 2 min ago    │
└──────────────┴──────────────┴──────────────┘

Cuadrícula de Paneles Disponibles
┌──────────────────────────────────┐
│ Panel                Tier  Pmax   │
├──────────────────────────────────┤
│ jinko_tiger_neo_580  1    580W   │ → Click para simular
│ longi_himo_x6_580    1    580W   │ → Click para simular
│ generic_poly_330     2    330W   │ → Click para simular
└──────────────────────────────────┘

Estado del Sistema (Gauges)
┌────────────────┬────────────────┐
│ API Response   │ Data Quality   │
│ 42 ms ✅      │ 95% ✅        │
└────────────────┴────────────────┘
```

### 4.2 Página Simulation - Calulator

```
Panel Selector (Sidebar)
├─ Panel ID (dropdown)
├─ Irradiancia POA (slider, 10-1400 W/m²)
├─ Temperatura célula (slider, -10 a 85°C)
└─ Resolución curva (slider, 10-500 puntos)

Visualización Principal (2 columnas)

Izquierda - Curva I-V:
┌─────────────────────────────┐
│ I-V Curve (Plotly)          │
│ ┌───────────────────────────┐│
│ │                           ││
│ │  I (A)                    ││
│ │  ↑                        ││
│ │  │     /‾‾‾‾‾‾\          ││
│ │  │    /         \         ││
│ │  │___/___________\___→ V  ││
│ │                           ││
│ └───────────────────────────┘│
│ MPP: 43.5V × 13.34A = 580W   │
└─────────────────────────────┘

Derecha - Curva P-V:
┌─────────────────────────────┐
│ P-V Curve (Plotly)          │
│ ┌───────────────────────────┐│
│ │ P (W)                     ││
│ │ ↑                         ││
│ │ │        /‾‾‾‾‾\          ││
│ │ │       /       \         ││
│ │ │______/         \___→ V  ││
│ │                           ││
│ └───────────────────────────┘│
│ Peak Power: 580W @ 43.5V     │
└─────────────────────────────┘

Tabla de Parámetros (Abajo)
┌────────────────────────────────────────────┐
│ Parámetro          Valor      Unidad       │
├────────────────────────────────────────────┤
│ Voc                52.0       V            │
│ Isc                14.3       A            │
│ Vmpp               43.5       V            │
│ Impp               13.34      A            │
│ Pmax               580.0      W            │
│ G_POA              1000.0     W/m²         │
│ T_cell             53.8       °C           │
│ Temp Coefficient   -0.29      %/°C         │
└────────────────────────────────────────────┘
```

### 4.3 Página Comparison - Comparador

```
Multi-Panel Selector
├─ Panel 1: [dropdown]
├─ Panel 2: [dropdown]
├─ Panel 3: [dropdown]

Controles Comunes
├─ Irradiancia: [slider]
├─ Temperatura: [slider]

Gráficos Comparativos (3 columnas)

Columna 1: Curva I-V (todos paneles)
Columna 2: Curva P-V (todos paneles)
Columna 3: Matriz de comparación

Matriz Comparativa (Tabla)
┌────────────┬──────────┬──────────┬──────────┐
│ Parámetro  │ Panel 1  │ Panel 2  │ Panel 3  │
├────────────┼──────────┼──────────┼──────────┤
│ Pmax       │ 580W     │ 580W     │ 330W     │
│ Voc        │ 52.0V    │ 51.6V    │ 45.6V    │
│ Isc        │ 14.3A    │ 14.48A   │ 9.2A     │
│ γ          │ -0.29%   │ -0.26%   │ -0.45%   │
│ Eff @STC   │ ~22%     │ ~23%     │ ~20%     │
└────────────┴──────────┴──────────┴──────────┘
```

### 4.4 Página Analysis - Análisis

```
Selector de Escenario
├─ Clima: [Seco, Templado, Tropical]
├─ Altitud: [1000m, 1500m, 2000m]
├─ Cobertura nubosa: [0%, 50%, 100%]

Simulación de Día Típico
┌──────────────────────────────────┐
│ Radiación Horaria (Típica)       │
│ ┌──────────────────────────────┐ │
│ │ Irr                          │ │
│ │ (W/m²)                       │ │
│ │ 1200┤      ╱╲                │ │
│ │      │    ╱  ╲              │ │
│ │  800├  ╱      ╲             │ │
│ │      │╱        ╲            │ │
│ │    0┼──────────── Hora →    │ │
│ │   06 08 10 12 14 16 18      │ │
│ └──────────────────────────────┘ │
└──────────────────────────────────┘

Generación Esperada Diaria
├─ Peak Irradiance: 950 W/m²
├─ Peak Power: 565 W (JinkoSolar)
├─ Daily Yield: 4.2 kWh/m²
└─ Pérdida térmica: -6.5% vs STC

Modelo NOCT - Temperatura Horaria
┌──────────────────────────────────┐
│ Temperatura Célula (°C)          │
│ ┌──────────────────────────────┐ │
│ │ T_cell                       │ │
│ │ (°C)                         │ │
│ │  60┤      ╱╲                 │ │
│ │    │    ╱  ╲                │ │
│ │  35├  ╱      ╲              │ │
│ │    │╱        ╲              │ │
│ │  20┼──────────── Hora →     │ │
│ │   06 08 10 12 14 16 18      │ │
│ └──────────────────────────────┘ │
└──────────────────────────────────┘

Eficiencia vs Temperatura
┌──────────────────────────────────┐
│ Panel Efficiency Loss (%)        │
│ ┌──────────────────────────────┐ │
│ │ Loss (%)  vs T_cell          │ │
│ │     0┤                        │ │
│ │   -2├      ╱                 │ │
│ │   -4├    ╱                   │ │
│ │   -6├  ╱                     │ │
│ │   -8├╱                       │ │
│ │  -10┼────────────────────→   │ │
│ │    25  35  45  55  65        │ │
│ └──────────────────────────────┘ │
└──────────────────────────────────┘
```

### 4.5 Página About - Información

```
Versión del Sistema
├─ SolarTwin CO: v0.1.0
├─ API Version: v1
├─ Backend: FastAPI + pvlib
├─ Frontend: Streamlit

Paneles Disponibles
├─ Tier 1: 2 paneles (580W)
├─ Tier 2: 1 panel (330W)
└─ Total: 3 paneles

Especificaciones Técnicas
├─ Modelo: Single Diode Model (CEC 5-parámetros)
├─ Temperatura: Ross-NOCT
├─ Radiación: GHI → POA (transposición)
└─ Localización: Eje Cafetero, Colombia

Documentación
├─ NOCT_MODEL_PHYSICS.md
├─ PANEL_TIER1_SETUP.md
└─ README.md

Contacto
└─ GitHub: BLKsoul19/SolarTwin_COV2
```

---

## 5. Ruta de Implementación

### 5.1 Sprint 3 (Semana 1-2: Streamlit MVP)

```
Hito 1: Setup básico (4-6 horas)
├─ Crear estructura de carpetas
├─ Setup config Streamlit
├─ Conexión a API backend
└─ Home page con KPIs

Hito 2: Página de Simulation (8-12 horas)
├─ Integración de controles (sidebar)
├─ Gráfico I-V con Plotly
├─ Gráfico P-V con Plotly
├─ Tabla de parámetros
└─ Error handling

Hito 3: Página de Comparison (6-8 horas)
├─ Multi-panel selector
├─ Gráficos superpuestos
├─ Tabla comparativa
└─ Export a CSV

Hito 4: Página de Analysis (8-10 horas)
├─ Escenarios preconfigurados
├─ Simulación de día típico
├─ Gráficos de variación temporal
└─ Análisis de pérdidas térmicas

Hito 5: Polish (4-6 horas)
├─ Página About
├─ Theming (colores SolarTwin)
├─ Responsive design
├─ Deploy a Streamlit Cloud (opcional)

TOTAL: 2 sprints (40-50 horas de desarrollo)
```

### 5.2 Sprint 4 (Opcional: React Frontend)

```
Solo si validación Streamlit es exitosa
Arquitectura:
├─ Frontend React (Vite + TS)
├─ Backend API (FastAPI, sin cambios)
├─ Base de datos (PostgreSQL, opcional)
└─ Auth (JWT, para multi-tenant)

Timeline: 4-6 semanas
Requisitos: Senior React developer
```

---

## 6. Dependencias y Setup

### 6.1 Dependencias Streamlit

```toml
[project.optional-dependencies]
dashboard = [
    "streamlit>=1.35",
    "plotly>=5.17",
    "pandas>=2.2",
    "httpx>=0.27",
]
```

### 6.2 Script de Inicio

```bash
# Terminal 1: Backend API
cd /workspaces/SolarTwin_COV2
uvicorn apps.api.main:app --reload --port 8000

# Terminal 2: Streamlit Dashboard
cd /workspaces/SolarTwin_COV2/apps/dashboard
streamlit run main.py --server.port 8501
```

### 6.3 URLs de Acceso

```
Backend API:      http://localhost:8000
Dashboard:        http://localhost:8501
API Documentation: http://localhost:8000/docs (Swagger)
```

---

## 7. Ejemplo de Código Streamlit (Prototipo)

### 7.1 main.py

```python
import streamlit as st
import httpx
import pandas as pd
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="SolarTwin CO Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("SolarTwin CO")
    st.markdown("**Digital Twin Photovoltaic**")
    st.divider()
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "⚡ Simulation", "🔄 Comparison", "📊 Analysis", "ℹ️ About"]
    )

# ============================================================================
# MAIN CONTENT
# ============================================================================

if page == "🏠 Home":
    st.title("🏠 Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Paneles disponibles", 3, "Tier 1-2")
    
    with col2:
        response = httpx.get(f"{API_BASE_URL}/health")
        status = "✅ Online" if response.status_code == 200 else "❌ Offline"
        st.metric("API Status", status)
    
    with col3:
        st.metric("Modelo físico", "SDM", "CEC 5-parámetros")
    
    st.divider()
    
    # Panel grid
    st.subheader("Paneles Disponibles")
    
    try:
        panels_response = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels")
        panels = panels_response.json()
        
        df = pd.DataFrame([
            {
                "Panel ID": p["panel_id"],
                "Pmax (W)": p["pmax_stc_w"],
                "Voc (V)": p["voc_stc_v"],
                "Isc (A)": p["isc_stc_a"],
                "NOCT (°C)": p["noct_c"],
                "Tier": p["tier"],
                "Technology": p["technology"]
            }
            for p in panels
        ])
        
        st.dataframe(df, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading panels: {e}")

elif page == "⚡ Simulation":
    st.title("⚡ Panel Simulator")
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Simulation Parameters")
        
        # Get available panels
        try:
            panels_response = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels")
            panels_list = [p["panel_id"] for p in panels_response.json()]
        except:
            panels_list = ["jinko_tiger_neo_580"]
        
        panel_id = st.selectbox("Select Panel", panels_list)
        g_poa = st.slider("Irradiance (W/m²)", 10, 1400, 1000, 50)
        t_cell = st.slider("Cell Temp (°C)", -10, 85, 25, 5)
        n_points = st.slider("Curve Resolution", 10, 500, 100, 10)
    
    # Main content
    col1, col2 = st.columns(2)
    
    try:
        # Get IV curve
        iv_response = httpx.get(
            f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}/iv",
            params={"g_poa_w_m2": g_poa, "t_cell_c": t_cell, "n_points": n_points}
        )
        iv_data = iv_response.json()
        
        with col1:
            st.subheader("I-V Curve")
            
            fig_iv = go.Figure()
            fig_iv.add_trace(go.Scatter(
                x=[p["v_v"] for p in iv_data["points"]],
                y=[p["i_a"] for p in iv_data["points"]],
                mode="lines",
                name="I-V",
                line=dict(color="blue", width=2)
            ))
            
            fig_iv.update_layout(
                xaxis_title="Voltage (V)",
                yaxis_title="Current (A)",
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_iv, use_container_width=True)
        
        with col2:
            st.subheader("P-V Curve")
            
            fig_pv = go.Figure()
            fig_pv.add_trace(go.Scatter(
                x=[p["v_v"] for p in iv_data["points"]],
                y=[p["p_w"] for p in iv_data["points"]],
                mode="lines",
                name="P-V",
                line=dict(color="green", width=2),
                fill="tozeroy"
            ))
            
            fig_pv.update_layout(
                xaxis_title="Voltage (V)",
                yaxis_title="Power (W)",
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_pv, use_container_width=True)
        
        # Parameters table
        st.subheader("Operating Point Parameters")
        
        params_data = {
            "Parameter": ["Voc", "Isc", "Vmpp", "Impp", "Pmpp", "G_POA", "T_cell"],
            "Value": [
                f"{iv_data['v_oc_v']:.2f}",
                f"{iv_data['i_sc_a']:.2f}",
                f"{iv_data['v_mpp_v']:.2f}",
                f"{iv_data['i_mpp_a']:.2f}",
                f"{iv_data['p_mpp_w']:.2f}",
                f"{g_poa:.1f}",
                f"{t_cell:.1f}"
            ],
            "Unit": ["V", "A", "V", "A", "W", "W/m²", "°C"]
        }
        
        st.dataframe(pd.DataFrame(params_data), use_container_width=True)
    
    except Exception as e:
        st.error(f"Simulation error: {e}")

elif page == "📊 Analysis":
    st.title("📊 Performance Analysis")
    st.info("Escenarios de clima y análisis de rendimiento en desarrollo...")

elif page == "ℹ️ About":
    st.title("ℹ️ About SolarTwin CO")
    
    st.markdown("""
    ### SolarTwin CO V2
    Digital Twin Fotovoltaico para el Mercado Colombiano
    
    **Versión**: 0.1.0  
    **Modelo Físico**: Single Diode Model (CEC 5-parámetros)  
    **Temperatura**: Ross-NOCT adaptado para Colombia  
    **Localización**: Eje Cafetero (Manizales, Caldas)
    
    ### Paneles Disponibles
    - **Tier 1**: JinkoSolar Tiger Neo 580W (TOPCon)
    - **Tier 1**: LONGi Hi-MO X6 580W (HPBC)
    - **Tier 2**: Generic Poly 330W (poli-PERC)
    
    ### Tecnología
    - Backend: FastAPI + pvlib + NREL-PySAM
    - Frontend: Streamlit
    - Physics: Photovoltaic research-grade
    """)
```

---

## 8. Flujo de Integración

```
Etapa 1: MVP Validación (Sprint 3)
  Streamlit + FastAPI ← Prueba de concepto

           ↓ (feedback positivo)

Etapa 2: Optimización (Sprint 4)
  Streamlit refinado + Base de datos local

           ↓ (escalabilidad necesaria)

Etapa 3: React Production (Sprint 5+)
  React frontend + FastAPI backend + PostgreSQL

           ↓ (multi-tenant, auth)

Etapa 4: Enterprise (Sprint 6+)
  Microservicios, Kubernetes, SaaS
```

---

## 9. Decisiones de Arquitectura

### 9.1 Frontend-Backend Separation

```
✅ MANTENER:
- API REST independiente (packages/pv-twin)
- Sin acoplamiento frontend-backend
- Dashboard es consumidor, no capa mediadora

✅ AGREGAR:
- app/dashboard/ (Streamlit)
- app/web/ (React, futuro)
- Ambos consumen mismo API
```

### 9.2 Caching Strategy

```python
@st.cache_resource
def get_api_client():
    """Cache HTTP client para no recrear conexiones"""
    return httpx.Client(base_url=API_BASE_URL)

@st.cache_data(ttl=3600)
def fetch_panels():
    """Cache lista de paneles (válido 1 hora)"""
    client = get_api_client()
    return client.get("/api/v1/twin/panels").json()
```

### 9.3 Error Handling

```python
try:
    response = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}/iv",
                        params={"g_poa_w_m2": g_poa, "t_cell_c": t_cell})
    response.raise_for_status()
    return response.json()

except httpx.TimeoutException:
    st.error("⏱️ Request timeout. Check if backend is running.")
except httpx.RequestError as e:
    st.error(f"❌ Connection error: {e}")
except httpx.HTTPStatusError as e:
    st.error(f"⚠️ Server error {e.response.status_code}: {e.response.text}")
```

---

## 10. Roadmap Completo

```
Sprint 2 (Completo ✅)
├─ 2 paneles Tier 1
├─ Smoke test
└─ Documentación NOCT

Sprint 3 (Próximo)
├─ Streamlit MVP Dashboard ← RECOMENDADO INICIAR AQUÍ
├─ 4 páginas principales
├─ Integración API
└─ Deploy Streamlit Cloud

Sprint 4 (Opcional)
├─ Refinamiento Streamlit
├─ Agregar 4 paneles Tier 2
├─ Base de datos SQLite local
└─ Reports PDF/CSV export

Sprint 5 (Largo plazo)
├─ React frontend architecture
├─ TypeScript + Vite setup
├─ Auth/Multi-user
└─ Production-grade deployment

Sprint 6+ (Futuro)
├─ Comunidades energéticas
├─ Time-series data (históricos)
├─ Alerts y notificaciones
├─ Mobile app (React Native)
└─ Integración con inversores
```

---

## 11. Recomendación Final

### ✅ Para Sprint 3: Implementar Streamlit MVP

**Porque:**
1. **Rápido**: 2 sprints vs 6 para React
2. **Validación**: Proof-of-concept antes de inversión grande
3. **Mismo stack**: Python → Sin fricción
4. **Escalable**: Fácil migrar a React si es exitoso
5. **Demo listo**: Impresionar a stakeholders en semana 3

**Prototipo estimado**: 4-6 semanas (1-2 sprints dedicados)

---

**Documento**: SolarTwin CO Dashboard Integration Strategy  
**Versión**: 1.0  
**Status**: ✅ LISTO PARA IMPLEMENTACIÓN  
