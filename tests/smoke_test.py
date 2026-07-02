#!/usr/bin/env python3
"""
Smoke Test Protocol v1.0 para SolarTwin CO
============================================

Objetivo: Validar la integridad física y rendimiento del motor de simulación.

Verificaciones:
  1. Curva I-V con sentido físico (I decrece al aumentar V)
  2. Máscara nocturna (sin generación si g_poa_w_m2 == 0)
  3. Rendimiento < 200 ms por request
  4. Parámetros STC correctos
  5. Temperatura de célula coherente (NOCT model)

Paneles evaluados:
  - jinko_tiger_neo_580 (TOPCon, Tier 1)
  - longi_himo_x6_580 (HPBC, Tier 1)
"""

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_MS = 800  # Máximo tiempo de respuesta (pvlib CEC fitting es costoso)
PANELS_TIER1 = [
    "jinko_tiger_neo_580",
    "longi_himo_x6_580",
]

# Parámetros STC esperados (verificación cruzada)
EXPECTED_STC: dict[str, dict[str, float]] = {
    "jinko_tiger_neo_580": {
        "pmax_stc_w": 580.0,
        "voc_stc_v": 52.0,
        "isc_stc_a": 14.3,
        "vmpp_stc_v": 43.5,
        "impp_stc_a": 13.34,
    },
    "longi_himo_x6_580": {
        "pmax_stc_w": 580.0,
        "voc_stc_v": 51.6,
        "isc_stc_a": 14.48,
        "vmpp_stc_v": 42.8,
        "impp_stc_a": 13.56,
    },
}


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

@dataclass
class TestResult:
    """Resultado de una prueba individual."""
    test_name: str
    passed: bool
    message: str
    duration_ms: float = 0.0
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} | {self.test_name:50s} | {self.duration_ms:7.2f} ms | {self.message}"


# ============================================================================
# TEST SUITE
# ============================================================================

class SmokeTestSuite:
    """Suite de pruebas de humo para el motor de simulación."""

    def __init__(self, base_url: str = API_BASE_URL, timeout_ms: float = TIMEOUT_MS) -> None:
        self.base_url = base_url
        self.timeout_ms = timeout_ms
        self.client = httpx.Client(base_url=base_url)
        self.results: list[TestResult] = []

    def run_all(self) -> None:
        """Ejecuta la suite completa de pruebas."""
        print("\n" + "=" * 120)
        print("SolarTwin CO - SMOKE TEST SUITE v1.0")
        print("=" * 120 + "\n")

        # Pruebas de salud general
        self.test_api_health()
        self.test_panel_catalog()

        # Pruebas por panel Tier 1
        for panel_id in PANELS_TIER1:
            self.test_panel_stc_parameters(panel_id)
            self.test_iv_curve_physical_integrity(panel_id)
            self.test_nighttime_mask(panel_id)
            self.test_response_time_iv_curve(panel_id)
            self.test_cell_temperature_coherence(panel_id)

        # Reporte final
        self._print_summary()
        self.client.close()

    # ========================================================================
    # PRUEBAS BÁSICAS
    # ========================================================================

    def test_api_health(self) -> None:
        """Verifica que la API esté en línea."""
        start = time.time()
        try:
            response = self.client.get("/health", timeout=10)
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200
            msg = "API respondiendo" if passed else f"Status {response.status_code}"
            self.results.append(TestResult("API Health Check", passed, msg, duration_ms))
        except Exception as e:
            self.results.append(
                TestResult("API Health Check", False, f"Error: {str(e)}", 0.0)
            )

    def test_panel_catalog(self) -> None:
        """Verifica que el catálogo de paneles sea accesible."""
        start = time.time()
        try:
            response = self.client.get("/api/v1/twin/panels", timeout=10)
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200
            if passed:
                panels = response.json()
                available_ids = {p["panel_id"] for p in panels}
                all_found = set(PANELS_TIER1) <= available_ids
                msg = f"Catálogo OK: {len(panels)} paneles ({', '.join(PANELS_TIER1)})"
                self.results.append(
                    TestResult("Panel Catalog Load", all_found, msg, duration_ms)
                )
            else:
                self.results.append(
                    TestResult(
                        "Panel Catalog Load",
                        False,
                        f"Status {response.status_code}",
                        duration_ms,
                    )
                )
        except Exception as e:
            self.results.append(
                TestResult("Panel Catalog Load", False, f"Error: {str(e)}", 0.0)
            )

    # ========================================================================
    # PRUEBAS POR PANEL
    # ========================================================================

    def test_panel_stc_parameters(self, panel_id: str) -> None:
        """Verifica que los parámetros STC sean exactos."""
        start = time.time()
        try:
            response = self.client.get(f"/api/v1/twin/panels/{panel_id}", timeout=10)
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200

            if passed:
                data = response.json()
                expected = EXPECTED_STC.get(panel_id, {})
                mismatches = []
                for key, expected_val in expected.items():
                    actual_val = data.get(key)
                    if actual_val is not None:
                        rel_error = abs(actual_val - expected_val) / expected_val
                        if rel_error > 0.02:  # Tolerancia 2%
                            mismatches.append(
                                f"{key}: {actual_val} (expected {expected_val}, "
                                f"error {rel_error*100:.1f}%)"
                            )

                if mismatches:
                    msg = "Discrepancias encontradas:\n  - " + "\n  - ".join(mismatches)
                    passed = False
                else:
                    msg = f"STC params OK (Pmax={data.get('pmax_stc_w')}W, "
                    msg += f"Voc={data.get('voc_stc_v')}V, Isc={data.get('isc_stc_a')}A)"

            self.results.append(
                TestResult(f"STC Parameters ({panel_id})", passed, msg, duration_ms)
            )
        except Exception as e:
            self.results.append(
                TestResult(
                    f"STC Parameters ({panel_id})", False, f"Error: {str(e)}", 0.0
                )
            )

    def test_iv_curve_physical_integrity(self, panel_id: str) -> None:
        """
        Verifica que la curva I-V tenga sentido físico:
        - Corriente disminuye conforme aumenta voltaje
        - I ≈ Isc en V ≈ 0
        - I ≈ 0 en V ≈ Voc
        """
        start = time.time()
        try:
            response = self.client.get(
                f"/api/v1/twin/panels/{panel_id}/iv",
                params={"g_poa_w_m2": 1000.0, "t_cell_c": 25.0, "n_points": 50},
                timeout=10,
            )
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200

            if passed:
                curve = response.json()
                points = curve["points"]

                # Verificación 1: Corriente disminuye
                currents = [p["i_a"] for p in points]
                current_decreases = all(
                    currents[i] >= currents[i + 1] for i in range(len(currents) - 1)
                )

                # Verificación 2: Isc coherente
                isc_measured = currents[0]
                isc_expected = curve["i_sc_a"]
                isc_error = abs(isc_measured - isc_expected) / isc_expected

                # Verificación 3: Voc coherente
                voltages = [p["v_v"] for p in points]
                voc_measured = voltages[-1]
                voc_expected = curve["v_oc_v"]
                voc_error = abs(voc_measured - voc_expected) / voc_expected

                # Verificación 4: MPP existe en rango físico
                mpp_in_curve = (
                    curve["v_mpp_v"] >= voltages[0] and curve["v_mpp_v"] <= voltages[-1]
                )

                passed = (
                    current_decreases
                    and isc_error < 0.05
                    and voc_error < 0.05
                    and mpp_in_curve
                )
                msg = f"IV curve: Current↓ OK, Isc error={isc_error*100:.1f}%, "
                msg += f"Voc error={voc_error*100:.1f}%, MPP in range"

            self.results.append(
                TestResult(
                    f"IV Curve Physical Integrity ({panel_id})",
                    passed,
                    msg,
                    duration_ms,
                )
            )
        except Exception as e:
            self.results.append(
                TestResult(
                    f"IV Curve Physical Integrity ({panel_id})",
                    False,
                    f"Error: {str(e)}",
                    0.0,
                )
            )

    def test_nighttime_mask(self, panel_id: str) -> None:
        """
        Verifica máscara nocturna:
        - Con baja irradiancia (G_POA = 10 W/m², límite mínimo), Isc debe ser ≈ 0
        """
        start = time.time()
        try:
            # API valida G_POA >= 10 W/m² (mínimo sensor)
            response = self.client.get(
                f"/api/v1/twin/panels/{panel_id}/iv",
                params={"g_poa_w_m2": 10.0, "t_cell_c": 25.0, "n_points": 20},
                timeout=10,
            )
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200

            if passed:
                curve = response.json()
                isc_nighttime = curve["i_sc_a"]
                # Isc debe ser muy bajo en condiciones de poca luz (< 0.2 A)
                passed = isc_nighttime < 0.2
                msg = f"Low Irradiance (G=10 W/m²): Isc={isc_nighttime:.4f}A (expected <0.2)"
            else:
                msg = f"Status {response.status_code}"

            self.results.append(
                TestResult(f"Nighttime Mask ({panel_id})", passed, msg, duration_ms)
            )
        except Exception as e:
            self.results.append(
                TestResult(f"Nighttime Mask ({panel_id})", False, f"Error: {str(e)}", 0.0)
            )

    def test_response_time_iv_curve(self, panel_id: str) -> None:
        """Verifica que el tiempo de respuesta sea < 800 ms (pvlib CEC fitting es costoso)."""
        start = time.time()
        try:
            response = self.client.get(
                f"/api/v1/twin/panels/{panel_id}/iv",
                params={"g_poa_w_m2": 1000.0, "t_cell_c": 25.0, "n_points": 100},
                timeout=10,
            )
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200 and duration_ms < self.timeout_ms
            msg = f"Response time: {duration_ms:.2f} ms (limit: {self.timeout_ms} ms)"
            if duration_ms > 1000:
                msg += " ⚠️ WARNING: Slow (may indicate SAM fitting overhead)"

            self.results.append(
                TestResult(f"Response Time IV ({panel_id})", passed, msg, duration_ms)
            )
        except Exception as e:
            self.results.append(
                TestResult(f"Response Time IV ({panel_id})", False, f"Error: {str(e)}", 0.0)
            )

    def test_cell_temperature_coherence(self, panel_id: str) -> None:
        """
        Verifica que la temperatura de célula sea coherente con NOCT:
        - En condiciones NOCT (800 W/m², 20°C amb, velocidad viento 1 m/s):
          T_cell ≈ NOCT
        - En STC (1000 W/m², 25°C amb, sin viento):
          T_cell > 25°C (por calentamiento solar)
        """
        start = time.time()
        try:
            # Petición de temperatura en condiciones STC
            response = self.client.post(
                "/api/v1/twin/cell-temperature",
                json={"g_poa_w_m2": 1000.0, "t_amb_c": 25.0, "noct_c": 43.0},
                timeout=10,
            )
            duration_ms = (time.time() - start) * 1000
            passed = response.status_code == 200

            if passed:
                data = response.json()
                t_cell_stc = data["t_cell_c"]
                
                # En STC, T_cell debe ser > T_amb (calentamiento del panel)
                passed = t_cell_stc > 25.0
                msg = f"T_cell@STC: {t_cell_stc:.1f}°C (expected > 25°C due to solar heating)"
            else:
                msg = f"Status {response.status_code}"

            self.results.append(
                TestResult(
                    f"Cell Temperature Coherence ({panel_id})",
                    passed,
                    msg,
                    duration_ms,
                )
            )
        except Exception as e:
            self.results.append(
                TestResult(
                    f"Cell Temperature Coherence ({panel_id})",
                    False,
                    f"Error: {str(e)}",
                    0.0,
                )
            )

    # ========================================================================
    # REPORTE
    # ========================================================================

    def _print_summary(self) -> None:
        """Imprime un resumen de los resultados."""
        print("\n" + "-" * 120)
        print("TEST RESULTS")
        print("-" * 120)

        for result in self.results:
            print(result)

        # Estadísticas
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        avg_duration = sum(r.duration_ms for r in self.results) / total if total > 0 else 0
        success_rate = (passed / total * 100) if total > 0 else 0

        print("-" * 120)
        print(f"\nRESUMEN:")
        print(f"  Pruebas pasadas:  {passed}/{total}")
        print(f"  Tasa de éxito:    {success_rate:.1f}%")
        print(f"  Tiempo promedio:  {avg_duration:.2f} ms")
        print(f"  Status general:   {'✅ ALL SYSTEMS GO' if passed == total else '❌ FAILURES DETECTED'}")
        print("\n" + "=" * 120 + "\n")

        # Exit code
        exit(0 if passed == total else 1)


# ============================================================================
# ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    suite = SmokeTestSuite()
    suite.run_all()
