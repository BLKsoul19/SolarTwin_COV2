# Contribuir a SolarTwin CO

Gracias por interesarte en este proyecto. Las contribuciones de ingeniería, documentación, pruebas y diseño son bienvenidas.

## Flujo recomendado

1. Crea una rama nueva a partir de la rama principal actual.
2. Describe el problema o la mejora en un issue antes de proponer cambios grandes.
3. Implementa cambios pequeños y verificables.
4. Añade o actualiza pruebas cuando sea posible.
5. Abre un pull request con una descripción clara del cambio.

## Requisitos locales

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Verificaciones recomendadas

```bash
pytest
ruff check .
mypy packages/pv-twin/src/pv_twin apps
```

## Estilo de contribución

- Mantén cambios enfocados y fáciles de revisar.
- Prioriza claridad en nombres, documentación y pruebas.
- Evita introducir dependencias innecesarias.
- Asegura que el código siga las convenciones del repositorio.
