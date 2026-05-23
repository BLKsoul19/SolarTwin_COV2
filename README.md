# SolarTwin CO V2

Diseno e implementacion de una plataforma digital de monitoreo para sistemas
fotovoltaicos distribuidos en Colombia, con gemelo digital de paneles
comerciales, adaptada a edificios inteligentes y escalable a comunidades
energeticas.

## Estado actual

Este repositorio esta en fase de bootstrap. La prioridad no es construir todo el
monorepo de una vez, sino dejar una base pequena, verificable y facil de ampliar.

Foco recomendado del Sprint 1:

```text
packages/pv-twin/   Nucleo academico del gemelo digital
tests/unit/         Pruebas fisicas y de validacion
data/panels/        Catalogo versionado de paneles
apps/api/           API minima para exponer el nucleo
.github/            Instrucciones de Copilot y CI
```

## Estructura

```text
.github/
  copilot-instructions.md
  workflows/ci.yml
apps/
  api/
packages/
  pv-twin/
    src/pv_twin/
tests/
  unit/
data/
  panels/
  tarifas/
infra/
```

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
ruff check .
mypy packages/pv-twin/src/pv_twin apps
```

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
```

## API local

```bash
uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints iniciales:

```text
GET /health
GET /api/v1/twin/panels
GET /api/v1/twin/panels/{panel_id}
POST /api/v1/twin/cell-temperature
```

Ejemplo de calculo fisico:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/twin/cell-temperature \
  -H "Content-Type: application/json" \
  -d '{"g_poa_w_m2":1000.0,"t_amb_c":25.0,"noct_c":45.0}'
```

## GitHub Copilot CLI

Desde la raiz del repo:

```bash
copilot
```

Tarea puntual:

```bash
copilot -p "Revisa la estructura y propone el siguiente modulo para Sprint 1"
```

Tambien puedes usar GitHub CLI si lo tienes habilitado:

```bash
gh copilot
gh copilot -p "Resume el proyecto y crea un plan corto de commits"
```

Copilot debe tomar como contexto principal `.github/copilot-instructions.md`.
