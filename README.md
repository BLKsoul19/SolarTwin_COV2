# SolarTwin CO

SolarTwin CO es una plataforma open-source para modelado, simulación y análisis de desempeño de sistemas fotovoltaicos, orientada al mercado colombiano y a la evolución hacia gemelos digitales, dashboards operativos y toma de decisiones basada en datos.

Este repositorio concentra el núcleo físico del proyecto: modelado de paneles solares, curvas I-V/P-V, temperatura de celda, catalogación de módulos y exposición de servicios a través de una API y un dashboard.

[![CI](https://github.com/BLKsoul19/SolarTwin_COV2/actions/workflows/ci.yml/badge.svg)](https://github.com/BLKsoul19/SolarTwin_COV2/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ¿Qué busca el proyecto?

SolarTwin CO combina ingeniería solar, simulación física y software para apoyar:

- selección técnica de paneles solares
- análisis de rendimiento bajo condiciones reales
- evaluación térmica y de irradiancia
- comparación entre módulos comerciales
- escalabilidad hacia dashboards y analítica energética

## Estado actual

El repositorio se encuentra en una fase de consolidación del núcleo físico del gemelo digital. La prioridad actual es estabilizar el modelo de simulación, validar resultados con datos físicos y preparar una base sólida para futuras capas de API, visualización y análisis.

## Capacidades actuales

- Catálogo versionado de paneles en formato JSON
- Implementación del modelo de un diodo simple (SDM)
- Cálculo de temperatura de celda con modelos térmicos
- Generación de curvas I-V y P-V
- API mínima para exponer resultados al dashboard
- Dashboard interactivo para exploración básica del sistema

## Estructura del repositorio

```text
.github/              Configuración de GitHub, CI y plantillas
apps/                 API y dashboard de referencia
packages/pv-twin/     Núcleo reutilizable del gemelo digital
tests/                Pruebas unitarias e integraciones
data/panels/          Catálogo de paneles solares
```

## Inicio rápido

### 1. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. Ejecutar pruebas

```bash
pytest
```

### 3. Levantar la API local

```bash
uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Levantar el dashboard

```bash
streamlit run apps/dashboard/main.py
```

## Ejemplos de uso

### Temperatura de celda

```bash
curl -X POST http://127.0.0.1:8000/api/v1/twin/cell-temperature \
  -H "Content-Type: application/json" \
  -d '{"g_poa_w_m2":1000.0,"t_amb_c":25.0,"noct_c":45.0}'
```

### Curva I-V de un panel

```bash
curl "http://127.0.0.1:8000/api/v1/twin/panels/generic_poly_330/iv?g_poa_w_m2=1000&t_cell_c=25&n_points=50"
```

## Ruta de desarrollo

La hoja de ruta del proyecto prioriza:

1. consolidación del núcleo físico
2. validación de modelos con criterios de ingeniería
3. mejora de UX y análisis del dashboard
4. escalabilidad hacia datos históricos, escenarios y decisiones operativas

## Contribuir

Las contribuciones son bienvenidas. Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para conocer el flujo recomendado de desarrollo, ramas y revisión de cambios.

## Seguridad

Si descubres una vulnerabilidad, consulta [SECURITY.md](SECURITY.md).

## Licencia

Este proyecto está bajo la licencia MIT. Consulta [LICENSE](LICENSE).
