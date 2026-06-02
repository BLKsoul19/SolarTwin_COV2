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

Fase activa: Sprint 3 - consolidacion del nucleo fisico.

Copilot debe priorizar:

- `packages/pv-twin/src/pv_twin/models/`
- `packages/pv-twin/src/pv_twin/simulator/`
- `packages/pv-twin/src/pv_twin/kpi/`
- `data/panels/`
- `tests/unit/`

No crear frontend, mobile, Kubernetes ni modulos grandes sin una tarea explicita.
El foco actual es completar el catalogo Tier 1, refinar temperatura con viento y
validar fisicamente el Single Diode Model con pvlib antes de avanzar a dashboard.

---

## Build, test & lint (comandos clave)

Requisitos: Python 3.11+, crea entorno virtual y instala dependencias de desarrollo:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Comandos comunes:

- Ejecutar toda la suite de tests: pytest
- Ejecutar un archivo de tests: pytest tests/unit/test_single_diode.py
- Ejecutar una prueba concreta (nodeid): pytest tests/unit/test_single_diode.py::test_solar_panel_twin_calculates_stc_iv_curve
- Ejecutar tests por palabra clave: pytest -k "get_cell_temperature"
- Ejecutar tests con cobertura (usar plugin pytest-cov): pytest --cov=packages/pv-twin --cov-fail-under=85
- Lint y formato: ruff check . && ruff format .
- Type checking: mypy packages/pv-twin/src/pv_twin apps
- Levantar la API local: uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000

NOTA: las pruebas marcadas como `integration` requieren infra externa (ver pytest markers).

---

## High-level architecture

- Monorepo minimal: apps/ (API), packages/ (paquetes reutilizables), data/ (catalogos), tests/.
- packages/pv-twin: nucleo del gemelo. Contiene:
  - pv_twin/models: Pydantic v2 data models (PanelParameters, catalog repo)
  - pv_twin/simulator: implementaciones fisicas (single diode model, temperatura)
  - pv_twin/kpi: funciones de KPI (PR, CUF, yield)
- apps/api: pequeño servicio FastAPI que expone endpoints para calculos y catalogos.
- data/panels: catalogo versionado de parametros STC (JSON). data/tarifas contiene tarifas.
- Dependencias fisicas importantes: pvlib (IV calculations) y NREL-PySAM para ajuste CEC (fit_cec_sam).
- Tests: tests/unit (unitarios, rapidos), tests/integration (requieren servicios/infra).
- Packaging: pyproject.toml declara packages/pv-twin bajo packages/pv-twin/src.
- CI: .github/workflows contains pipeline (ejecuta pytest, ruff, mypy, coverage).

---

## Repository-specific conventions

- Todas las variables fisicas incluyen su unidad en el nombre: `g_poa_w_m2`, `t_cell_c`, `p_dc_w`, etc.
- Series temporales siempre timezone-aware (tz: America/Bogota).
- Nunca pasar GHI directamente al SDM: transformar GHI->POA antes de cualquier calculo del gemelo.
- Aplicar mascara diurna (daylight mask) antes de invocar el Single Diode Model o calcular KPI.
- Pydantic v2 para modelos; las validaciones y field_validators deben usarse en modelos de catalogo.
- Evitar imports desde apps/api hacia packages/pv-twin (packages son independientes).
- Tests deben validar propiedades numericas y relaciones fisicas (ej. p_mpp cerca de Pmax STC), no solo non-None.
- Cuando un metodo usa fit_cec_sam, documentar la dependencia opcional NREL-PySAM (puede fallar en entornos sin ella).
- Mantener line-length ≤ 100 y seguir ruff/mypy settings en pyproject.toml.
- Coverage mínimo: 85% (configurado en pyproject.toml).

---

## How Copilot should prioritize context

- Prioridad para asistencias: primero abrir `packages/pv-twin/src/pv_twin/simulator/`, luego `models/`, luego `kpi/`, y finalmente `tests/unit/`.
- Para cambios que afectan la API, revisar `apps/api/` pero no introducir dependencias desde apps hacia packages.
- No proponer frontend, infra o módulos grandes sin una issue/consenso previo.

---

## Referencias extra (extractos importantes)

- pyproject.toml: ruff target py311, mypy strict=true, pytest testpaths=tests, coverage fail_under=85.
- README.md contiene ejemplos de uso de la API y comandos de desarrollo local.

---

## Cambios recomendados / notas para mantener

- Mantener este archivo sincronizado con README.md y pyproject.toml.
- Actualizar la lista de paneles canonicos cuando se agreguen nuevos JSON en data/panels.

---

## Antipatrones (recordatorio)

- Variables `G`, `T`, `P`, `E` sin unidades.
- `pd.date_range(...)` sin `tz`.
- Tarifas en constantes dentro del codigo.
- Imports desde `apps/api` dentro de `packages/pv-twin`.
- Tests que solo validen `result is not None`.
