# NOCT Model Physics for SolarTwin CO
## Application to Colombian Coffee Belt (Eje Cafetero)

---

## 1. Fundamentals: NOCT Definition

**NOCT** (Nominal Operating Cell Temperature) is the equilibrium cell temperature reached under:

```
Standard Test Conditions (NOCT):
├─ Plane-of-array irradiance:      G_NOCT = 800 W/m²
├─ Ambient temperature:             T_amb = 20°C
├─ Wind speed (over panel surface): v_wind = 1 m/s
└─ Air mass:                        AM = 1.5 (near sea level)
```

**Physical meaning**: NOCT is the realistic "steady-state" temperature at which a panel 
operates in moderate field conditions, NOT the peak temperature under STC.

---

## 2. Ross-NOCT Temperature Model

SolarTwin CO implements the **Ross-NOCT formula**:

$$T_{cell} = T_{amb} + \left(\frac{NOCT - 20}{800}\right) \times G_{POA}$$

Where:
- $T_{cell}$ = Cell temperature (°C) [t_cell_c]
- $T_{amb}$ = Ambient air temperature (°C) [t_amb_c]
- $NOCT$ = Panel's nominal operating cell temperature (°C) [noct_c]
- $G_{POA}$ = Plane-of-array irradiance (W/m²) [g_poa_w_m2]

### Example Calculation (JinkoSolar Tiger Neo 580W)

```
Panel spec:  NOCT = 43°C
Location:    Eje Cafetero, Colombia (altitude ≈ 1300 m, lat ≈ 5°N)

Scenario 1: Mid-morning (clear sky, high solar radiation)
  T_amb = 24°C
  G_POA = 900 W/m²  (90% of STC due to air mass & angles)
  
  T_cell = 24 + (43 - 20) / 800 × 900
         = 24 + 23/800 × 900
         = 24 + 25.875
         = 49.9°C  [realistic field operation]

Scenario 2: Peak STC conditions (lab, rarely seen in field)
  T_amb = 25°C
  G_POA = 1000 W/m²  (perpendicular, sea level, AM=1.5)
  
  T_cell = 25 + 23/800 × 1000
         = 25 + 28.75
         = 53.75°C  [lab peak]

Scenario 3: Morning with light cloud cover
  T_amb = 22°C
  G_POA = 400 W/m²  (partly cloudy)
  
  T_cell = 22 + 23/800 × 400
         = 22 + 11.5
         = 33.5°C  [cooler operation]
```

---

## 3. Physical Assumptions & Validity

### 3.1 Heat Balance (Why This Model Works)

The cell temperature equilibrium results from:

$$Q_{solar} = Q_{dissipated} + Q_{electrical}$$

Where:
- $Q_{solar}$ = Absorbed solar radiation = $G_{POA} \times \alpha_{abs}$ 
  - (α_abs ≈ 0.85-0.90 depending on spectral distribution)
- $Q_{dissipated}$ = Convective + radiative losses to atmosphere
- $Q_{electrical}$ = Useful electricity generated (small, ≈ 20% of input)

**Key insight**: As $G_{POA}$ increases, more solar energy must be dissipated as heat,
raising $T_{cell}$.

The **NOCT constant** $(NOCT - 20) / 800$ captures the panel's thermal resistance:
- **Lower NOCT** → Better cooling → More expensive (better materials, ventilation)
- **Higher NOCT** → Worse cooling → Cheaper

### 3.2 Limitations of Ross-NOCT

This model assumes **linear response**, which is valid for:
- $G_{POA}$ from 0 to 1200 W/m² ✓ (typical field range)
- $T_{amb}$ from -10 to +40°C ✓ (global weather range)
- Wind speed ≈ 1-2 m/s ✓ (stationary or slow-moving panels)

**NOT valid for**:
- Very high wind (> 5 m/s) → Panel cools more, model underestimates T_cell ✗
- Extreme temperatures (< -20°C or > 50°C) → Material effects dominate ✗
- Stagnant air (v_wind ≈ 0) → T_cell rises significantly ✗

---

## 4. Colombian Climate Context: Eje Cafetero

### 4.1 Typical Annual Profile

```
Location: Manizales, Caldas (5°07'N, 74°88'W, 2,154 m elevation)

Climate:  Tropical highland (eternal spring)
├─ T_amb range:      15-26°C (very stable, ±2°C seasonal variation)
├─ Annual rainfall:   2,000-2,500 mm (rainy all year, peaks Apr-May, Oct-Nov)
├─ Cloud cover:       60-80% annual average (mornings clear, afternoons cloudy)
└─ Wind speed:        2-4 m/s (trade winds, consistent)

Solar Resource (GHI):
├─ Peak GHI (clear):     ~1000 W/m² (but rare, maybe 10% days)
├─ Typical clear day:    800-900 W/m² peak
├─ Partly cloudy:        400-600 W/m² peak
└─ Annual insolation:    1,400-1,500 kWh/m²/year (vs. 1,600 global avg)
```

### 4.2 Why NOCT Matters for Colombia

1. **Constant T_amb (15-26°C)**
   - Year-round: $T_{cell}$ = 35-50°C (very stable)
   - No extreme heating (like Atacama) or cooling (like Germany)
   - Predictable, long panel lifetime (~30 years)

2. **High cloud cover (60-80%)**
   - Fewer STC-level irradiances
   - More operation in NOCT or below-NOCT regime
   - **Panel actually sees lower temperatures than STC**
   
3. **Moderate wind speed (2-4 m/s)**
   - Better cooling than tropical stagnant air
   - But not as extreme as high-altitude deserts
   - NOCT assumption (v_wind ≈ 1 m/s) is slightly conservative
   
4. **High altitude (1,300-2,200 m)**
   - Lower atmospheric pressure → less convective cooling
   - **Effect**: T_cell slightly higher than sea-level (contraints Ross-NOCT)
   - **Adjustment**: Add +2-4°C buffer for altitude > 1,500 m

### 4.3 Corrected NOCT for Eje Cafetero

For panels installed > 1,500 m elevation, use:

$$T_{cell}^{altitude} = T_{cell}^{NOCT} + 2 \text{ °C}$$

**SolarTwin CO Implementation**:
```python
def get_cell_temperature(
    g_poa_w_m2: float,
    t_amb_c: float,
    noct_c: float,
    altitude_m: float = 1300.0  # Default Manizales
) -> float:
    t_cell = t_amb_c + (noct_c - 20) / 800 * g_poa_w_m2
    
    # Altitude correction for mountain regions
    if altitude_m > 1500:
        altitude_factor = (altitude_m - 1500) / 1000 * 0.02  # +2°C per 1000m
        t_cell += altitude_factor
    
    return t_cell
```

---

## 5. Validation Against Measured Data

### 5.1 Validation Metrics

For a panel in Eje Cafetero with known installed characteristics:

```
Test:  Compare NOCT model vs. actual field measurements
Data:  5 representative days (clear, cloudy, mixed)

Expected outcomes:
├─ RMSE (T_cell): < 3°C
├─ Bias:          -1 to +2°C (model slightly conservative)
└─ Correlation:   > 0.95 with GHI
```

### 5.2 Cross-Check: Energy Balance

```
Panel efficiency at NOCT:
  η = P_max_STC / (G_NOCT × A_panel)
  η = 580 W / (800 W/m² × 2.0 m²)
  η ≈ 36.25%  [but includes mismatch losses, wiring, etc.]
  
Corrected module efficiency:
  η_module ≈ 20-22%  (typical Tier 1 panels)
  
Heat generated:
  Q_heat = G_NOCT × A × (1 - η_module)
  Q_heat = 800 × 2.0 × 0.78 = 1,248 W
  
Temperature rise:
  ΔT = Q_heat / (h_conv × A) where h_conv ≈ 5-10 W/m²K
  ΔT ≈ 1,248 / (7.5 × 2) ≈ 83 K (too high!)
  
Resolution: Part of heat is radiated away (σT⁴ term).
The NOCT constant empirically captures this complete energy balance.
```

---

## 6. SolarTwin CO Implementation

### 6.1 Tier 1 Panels with NOCT

| Panel | Technology | NOCT | Altitude Adjustment |
|-------|-----------|------|---------------------|
| JinkoSolar Tiger Neo 580W | TOPCon | 43°C | +2°C @ 1,300m |
| LONGi Hi-MO X6 580W | HPBC | 42°C | +2°C @ 1,300m |
| Generic Poly 330W | poli-PERC | 45°C | +2°C @ 1,300m |

### 6.2 Temperature Coefficients Impact

For each panel, power output decreases with temperature:

$$P_{out} = P_{max,STC} \times \left[1 + \gamma \times (T_{cell} - 25°C)\right]$$

Where $\gamma$ is the temperature coefficient of Pmax (typically -0.3% to -0.5% per °C).

**Example: JinkoSolar (γ = -0.29% per °C)**

```
At STC (25°C):           P = 580.0 W
At NOCT field (50°C):    P = 580 × [1 - 0.0029 × 25]
                         P = 580 × 0.9275
                         P ≈ 538 W  (-7.25% from STC nameplate)
                         
Colombia daily avg (35°C): P = 580 × [1 - 0.0029 × 10]
                         P ≈ 559 W   (-3.6% from STC nameplate)
```

This means **Colombian panels generate 3-7% less than STC rating**, which is why 
performance ratio (PR) is crucial for validating system health.

---

## 7. Practical Guidelines

### 7.1 Installation Best Practices for Eje Cafetero

```
✓ DO:
  - Leave 10-15 cm air gap under panels (natural convection)
  - Orient South (5°S latitude ≈ minimal seasonal tilt variation)
  - Use Tilt = Latitude ± 5° for year-round balance
  - Monitor T_cell via thermal imaging quarterly
  - Log G_POA with calibrated pyranometer

✗ DON'T:
  - Mount on metal roofs without ventilation (T_cell → 60-70°C)
  - Expect STC nameplate power (always 5-10% lower in field)
  - Ignore altitude correction for sites > 1,500 m
  - Use NOCT for transient conditions (clouds, wind gusts)
```

### 7.2 SolarTwin CO Output Interpretation

When calling `GET /api/v1/twin/panels/{panel_id}/iv`:

```json
{
  "panel_id": "jinko_tiger_neo_580",
  "g_poa_w_m2": 900,
  "t_cell_c": 49.9,
  "v_oc_v": 51.3,
  "i_sc_a": 14.18,
  "v_mpp_v": 42.8,
  "i_mpp_a": 12.62,
  "p_mpp_w": 540.0,
  ...
}
```

**Interpretation for Colombia**:
- T_cell = 49.9°C is realistic (NOCT + altitude)
- P_mpp = 540W is -6.9% from 580W nameplate (expected)
- V_oc drops from 52V (STC) → 51.3V due to heating (expected)
- I_sc stays ≈ 14.18A (photocurrent, less temperature-sensitive)

---

## References

- IEC 61724-1: "Photovoltaic system performance monitoring"
- NREL Technical Note on Cell Temperature: Evans et al. (1982)
- pvlib Python documentation: https://pvlib-python.readthedocs.io
- Colombian Climate Data: IDEAM (Instituto de Hidrología, Meteorología y Estudios Ambientales)

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-24  
**Applicable to**: SolarTwin CO v0.1.0+  
