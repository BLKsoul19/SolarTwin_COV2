# SolarTwin CO - Copilot Instructions

Este archivo es el contexto principal para GitHub Copilot dentro del repositorio.
Mantenerlo actualizado al inicio de cada sprint.

## Identidad del proyecto

SolarTwin CO es una plataforma open-source de monitoreo fotovoltaico con gemelo
digital para el mercado colombiano. El desarrollo inicia con el nucleo academico
de simulacion de paneles y luego crece hacia API, dashboard, EMS y comunidades
energeticas.

Repositorio: `SolarTwin_COV2`
Lenguaje principal: Python 3.11+
Lenguaje secundario futuro: TypeScript
Zona horaria del dominio: `America/Bogota`

## Prioridad actual

Fase activa: Sprint 1 - Twin core.

Copilot debe priorizar:

- `packages/pv-twin/src/pv_twin/models/`
- `packages/pv-twin/src/pv_twin/simulator/`
- `packages/pv-twin/src/pv_twin/kpi/`
- `data/panels/`
- `tests/unit/`

No crear frontend, mobile, Kubernetes ni modulos grandes sin una tarea explicita.

## Reglas de codigo

- Usar type hints completos en Python.
- Usar docstrings estilo Google en funciones publicas.
- Usar Pydantic v2 para modelos de datos.
- Toda variable fisica debe incluir unidad en el nombre:
  - `g_poa_w_m2`
  - `t_cell_c`
  - `v_mpp_v`
  - `i_mpp_a`
  - `p_dc_w`
  - `e_ac_kwh`
- Series temporales siempre timezone-aware con `America/Bogota`.
- Nunca alimentar GHI directo al gemelo; transformar GHI a POA antes del SDM.
- Aplicar mascara diurna antes de invocar el Single Diode Model.
- No hardcodear tarifas; cargarlas desde `data/tarifas/`.

## Capas

```text
packages/pv-twin/   Nucleo independiente. No importa desde apps/.
packages/ems/       Puede importar desde pv-twin cuando exista.
apps/api/           Puede importar desde packages/.
```

## Comandos esperados

```bash
pytest
ruff check .
ruff format .
mypy packages/pv-twin/src/pv_twin apps
uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000
```

## Catalogo inicial de paneles

IDs canonicos:

- `jinko_tiger_neo_580`
- `longi_himo_x6_580`
- `canadian_hiku7_600`
- `trina_vertex_splus_420`
- `ja_solar_jam72d40_570`
- `risen_rsm144_550`
- `generic_poly_330`

## Definiciones KPI

- PR = `(E_AC / P_STC) / (H_POA / G_ref)`
- CUF = `E_AC / (P_STC * horas)`
- Yield especifico = `E_AC / P_STC`

## Antipatrones

- Variables `G`, `T`, `P`, `E` sin unidades.
- `pd.date_range(...)` sin `tz`.
- Tarifas en constantes dentro del codigo.
- Imports desde `apps/api` dentro de `packages/pv-twin`.
- Tests que solo validen `result is not None`.
