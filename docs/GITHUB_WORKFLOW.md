# Flujo de trabajo GitHub para SolarTwin CO

Este documento describe el flujo de trabajo recomendado para trabajar en el repositorio y mantener la calidad científica y de ingeniería.

## Modelo de ramas

- `main`: rama estable de producción.
- `develop`: rama de integración para cambios validados antes de `main`.
- `JH_DEV`: rama de trabajo actual para mejoras de infraestructura y documentación; debe fusionarse a `develop` o `main` cuando esté lista.
- `feature/<descripción>`: nuevas funcionalidades.
- `fix/<descripción>`: correcciones de errores.
- `docs/<descripción>`: cambios en documentación.
- `hotfix/<descripción>`: correcciones urgentes que deben ir directamente a `main`.

### Reglas clave

- No trabajar directamente en `main`.
- Crear una rama específica para cada cambio significativo.
- Mantener PRs enfocados y con un solo propósito.
- Siempre incluir pruebas o validaciones cuando el cambio impacta código.
- Actualizar documentación si cambia el comportamiento o el uso.

## Proceso de pull request

1. Abrir un issue si el cambio es relevante o requiere discusión.
2. Crear la rama basada en `develop` o `main` según el alcance.
3. Trabajar en la rama y hacer commits pequeños y coherentes.
4. Push de la rama remota.
5. Abrir un pull request hacia `develop` o `main`.
6. Completar la plantilla de PR y el checklist de revisión.
7. Esperar revisiones y corregir comentarios.
8. Merge después de aprobación y CI exitoso.

## Integraciones de CI

El proyecto tiene estas acciones configuradas:

- `ci.yml`: ejecuta tests, lint, formateo y tipeo en cada push y pull request.
- `release.yml`: publica un release automático cuando se crea un tag `v*`.
- `dependabot.yml`: revisa dependencias semanalmente.

### Qué valida el CI

- `pytest tests/unit tests/integration -v --cov=packages --cov=apps`
- `ruff check .`
- `ruff format . --check`
- `mypy packages/pv-twin/src/pv_twin apps`

## Versionado y releases

Usar [SemVer](https://semver.org/): `vMAJOR.MINOR.PATCH`.

- `MAJOR`: cambios incompatibles en la API o en la arquitectura del gemelo.
- `MINOR`: nuevas funcionalidades compatibles.
- `PATCH`: correcciones y mejoras menores.

### Proceso de release

1. Asegurar que `develop` o `main` estén actualizadas.
2. Fusionar los cambios aprobados.
3. Crear un tag con `git tag vX.Y.Z`.
4. Subir el tag con `git push origin vX.Y.Z`.
5. GitHub ejecuta `release.yml` y publica el release.

## Recomendaciones para un proyecto científico

- Documentar modelos físicos y supuestos en `docs/`.
- Usar `tests/` para validar resultados numéricos, no solo el flujo.
- Mantener un registro de versiones de catálogo en `data/panels/`.
- Añadir casos de prueba para paneles representativos y límites físicos.
- Priorizar reproducibilidad: un desarrollador debe poder levantar API y dashboard con los mismos pasos.
