#!/bin/bash

# ============================================================================
# SolarTwin CO - Quick Start para Paneles Tier 1
# ============================================================================
# Este script automatiza el setup y validación del sistema
# ============================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  SolarTwin CO - Panel Tier 1 Quick Start                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# PASO 1: Verificar dependencias
# ============================================================================

echo "📦 Paso 1: Verificando dependencias..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION encontrado"

# ============================================================================
# PASO 2: Crear entorno virtual (si no existe)
# ============================================================================

echo ""
echo "📦 Paso 2: Verificando entorno virtual..."

if [ ! -d ".venv" ]; then
    echo "⚙️  Creando entorno virtual..."
    python3 -m venv .venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

source .venv/bin/activate
echo "✅ Entorno virtual activado"

# ============================================================================
# PASO 3: Instalar dependencias
# ============================================================================

echo ""
echo "📦 Paso 3: Instalando dependencias..."

pip install --upgrade pip > /dev/null 2>&1
pip install -e ".[dev]" > /dev/null 2>&1

echo "✅ Dependencias instaladas"

# ============================================================================
# PASO 4: Validar paneles Tier 1
# ============================================================================

echo ""
echo "🧪 Paso 4: Validando paneles Tier 1..."

python3 << 'PYEOF'
from pv_twin.models import PanelCatalogRepository

catalog = PanelCatalogRepository()
all_panels = catalog.list_all()
tier1_panels = [p for p in all_panels if p.tier == 1]

print(f"\nPaneles encontrados: {len(all_panels)}")
print(f"Paneles Tier 1: {len(tier1_panels)}")
print()

for panel in tier1_panels:
    print(f"  ✓ {panel.panel_id:25s} {panel.technology:8s} Pmax={panel.pmax_stc_w:6.0f}W NOCT={panel.noct_c}°C")

if len(tier1_panels) < 2:
    print("\n⚠️  Advertencia: Menos de 2 paneles Tier 1")
else:
    print(f"\n✅ {len(tier1_panels)} paneles Tier 1 disponibles")
PYEOF

# ============================================================================
# PASO 5: Ejecutar pruebas unitarias
# ============================================================================

echo ""
echo "🧪 Paso 5: Ejecutando pruebas unitarias..."

UNIT_TESTS=$(python3 -m pytest tests/unit -q --tb=no 2>&1 | tail -1)
echo "✅ $UNIT_TESTS"

# ============================================================================
# PASO 6: Lanzar API y smoke test
# ============================================================================

echo ""
echo "🚀 Paso 6: Lanzando API y smoke test..."
echo ""
echo "⚠️  IMPORTANTE:"
echo "  1. La API se lanzará en el puerto 8000"
echo "  2. El smoke test validará todas las pruebas"
echo "  3. Presiona CTRL+C cuando quieras detener"
echo ""

# Lanzar API en background
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 &> /tmp/api.log &
API_PID=$!

# Esperar a que API esté lista
echo "⏳ Esperando que API esté lista..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ API lista en http://127.0.0.1:8000"
        break
    fi
    sleep 1
done

# Ejecutar smoke test
echo ""
echo "🧪 Ejecutando smoke test..."
echo ""

python3 tests/smoke_test.py

# Limpiar
echo ""
echo "🧹 Limpiando procesos..."
kill $API_PID 2>/dev/null || true

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETADO                                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Próximos pasos:"
echo "  1. Revisar docs/NOCT_MODEL_PHYSICS.md para entender la física"
echo "  2. Revisar docs/PANEL_TIER1_SETUP.md para especificaciones"
echo "  3. Ejecutar: uvicorn apps.api.main:app --reload"
echo "  4. Consumir API en http://127.0.0.1:8000"
echo ""
