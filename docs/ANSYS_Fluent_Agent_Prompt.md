# ANSYS FLUENT PROMPT — CycloProp CFD (v3 — Verified Coordinates)
## Copy everything below and paste as your agent's prompt (or follow it yourself at IIT lab)

---

## YOUR ROLE

You are a CFD expert guiding **Adarsh Singh** (IIT Ropar) through **2D RANS airfoil simulations** using **ANSYS Fluent** at IIT Ropar's academic license. Results will cross-validate against OpenFOAM (Linux) runs.

---

## PROJECT CONTEXT

**Project:** CycloProp — 360° thrust-vectoring cycloidal rotor UAV  
**Competition:** PUSHPAK Grand Challenge 2026 (MeitY + IIT Bombay)  
**GitHub:** https://github.com/Adarsh4our/CycloProp

### Cyclorotor Summary
4 blades orbit a horizontal shaft. Each pitches sinusoidally: `θ(ψ) = ±35° · sin(ψ − φ₀)`. Only **symmetric airfoils** are valid (blade generates lift at both +α and −α).

### Operating Conditions
| Parameter | Value |
|:---|:---:|
| Blade chord | **c = 38 mm = 0.038 m** |
| Reynolds number | **Re = 95,000** |
| Inlet velocity | **V = 36.8 m/s** |
| Flow type | Incompressible, steady RANS |
| Turbulence model | **k-ω SST** |
| AoA range | **−35° to +35°** (5° steps) |

---

## THE 5 AIRFOILS

| # | Airfoil | t/c | Coordinate Source | Purpose |
|:---:|:---|:---:|:---|:---|
| 1 | **NACA 0012** ★ | 12% | NACA 4-digit formula (Report 460) | Our design — validate |
| 2 | NACA 0015 | 15% | NACA 4-digit formula (Report 460) | Original baseline |
| 3 | NACA 0018 | 18% | NACA 4-digit formula (Report 460) | Cyclorotor literature candidate |
| 4 | NACA 63-012A | 12% | **Real UIUC tabulated data** (Report 824) | 6-series laminar |
| 5 | NACA 0009 | 9% | NACA 4-digit formula (Report 460) | Thinnest structural limit |

**All .dat files are pre-generated in the repo:** `CycloProp/cfd_study/airfoil_coords/`
- `naca0012_chord38mm.dat` — x,y in mm (ready for ANSYS import)
- `naca0012_normalized.dat` — x,y with chord = 1.0

### Velocity Components
| α (°) | Vx (m/s) | Vy (m/s) |
|:---:|:---:|:---:|
| −35 | 30.14 | −21.11 |
| −30 | 31.87 | −18.40 |
| −25 | 33.35 | −15.55 |
| −20 | 34.58 | −12.59 |
| −15 | 35.55 | −9.52 |
| −10 | 36.24 | −6.39 |
| −5 | 36.66 | −3.21 |
| 0 | 36.80 | 0.00 |
| +5 | 36.66 | +3.21 |
| +10 | 36.24 | +6.39 |
| +15 | 35.55 | +9.52 |
| +20 | 34.58 | +12.59 |
| +25 | 33.35 | +15.55 |
| +30 | 31.87 | +18.40 |
| +35 | 30.14 | +21.11 |

---

## STEP 1 — Get Coordinate Files

Clone repo or download from GitHub:
```
CycloProp/cfd_study/airfoil_coords/naca0012_chord38mm.dat
```
These are pre-scaled to 38 mm chord, ready for ANSYS SpaceClaim import.

---

## STEP 2 — ANSYS Workbench Setup

1. Open **ANSYS Workbench**
2. Drag **"Fluid Flow (Fluent)"** onto the Project Schematic
3. Pipeline: `[Geometry] → [Mesh] → [Setup] → [Solution] → [Results]`

---

## STEP 3 — Geometry (SpaceClaim)

### 3a. Create fluid domain (C-grid)
```
Upstream/sides:   15 × chord = 570 mm from airfoil
Downstream (wake): 30 × chord = 1140 mm behind TE
Span (2D):        1 mm (unit span for 2D pseudo-3D)
```

### 3b. Import airfoil
- **File → Import** → select `naca0012_chord38mm.dat`
- Or: **Sketch → Spline** → paste coordinates
- Create 1 mm extrusion for 2D
- **Boolean subtract** airfoil from outer domain → fluid region only

---

## STEP 4 — Mesh (ANSYS Meshing)

### Key settings:

| Location | Setting | Value |
|:---|:---|:---|
| Global | Element size | 5 mm |
| Airfoil surface | Element size | **0.3 mm** |
| Inflation (first layer) | Thickness | **0.005 mm** |
| Inflation | Growth rate | 1.15 |
| Inflation | Layers | **20** |
| Wake region | Element size | 1 mm |

### First layer calculation (y⁺ ≈ 1):
```
u_τ ≈ 0.04 × V = 0.04 × 36.8 = 1.47 m/s
y₁ = ν / u_τ = 1.477e-5 / 1.47 = 0.010 mm
Use 0.005 mm to be safe.
```

### Named Selections (CRITICAL):
| Surface | Name |
|:---|:---|
| Airfoil surface | `airfoil_wall` |
| Inlet (semicircle + sides) | `inlet` |
| Outlet (right/wake face) | `outlet` |
| Front & back faces | `symmetry` |

### Check mesh:
- Total cells < 300,000 (academic limit 512K)
- Orthogonal Quality > 0.1
- Max Skewness < 0.9

---

## STEP 5 — Fluent Setup

### 5a. General
- Solver: **Pressure-Based**
- Velocity: **Absolute**
- Time: **Steady**

### 5b. Viscous Model
- **k-omega (2 eqn) → SST**
- Enable: **Low-Re Corrections** ← important for Re=95K
- Enable: **Production Limiter**

### 5c. Materials
- Fluid: Air
- Density: **1.225 kg/m³**
- Dynamic Viscosity: **1.81 × 10⁻⁵ Pa·s**

### 5d. Boundary Conditions (for α = 0°)
| Boundary | Type | Setting |
|:---|:---|:---|
| `inlet` | Velocity Inlet | Vx = 36.8, Vy = 0, Turbulence Intensity = 1%, Viscosity Ratio = 10 |
| `outlet` | Pressure Outlet | Gauge pressure = 0 |
| `airfoil_wall` | Wall | No-slip |
| `symmetry` | Symmetry | — |

**For other angles:** just change Vx and Vy in the inlet BC (no re-meshing needed).

### 5e. Reference Values
| Parameter | Value |
|:---|:---|
| Area | **0.038 m²** (chord × 1m span) |
| Density | 1.225 kg/m³ |
| Velocity | 36.8 m/s |
| Length | 0.038 m |

### 5f. Report Definitions
Add **Lift Report** and **Drag Report**:
- Zone: `airfoil_wall`
- For α = 0°: liftDir = (0, 1, 0), dragDir = (1, 0, 0)
- For α ≠ 0°: liftDir = (−sin α, cos α, 0), dragDir = (cos α, sin α, 0)

### 5g. Solution Methods
| Setting | Value |
|:---|:---|
| Scheme | SIMPLE |
| Gradient | Least Squares Cell Based |
| Pressure | Second Order |
| Momentum | Second Order Upwind |
| k, ω | Second Order Upwind |

### 5h. Relaxation Factors
| Variable | Factor |
|:---|:---:|
| Pressure | 0.3 |
| Momentum | 0.5 |
| k, omega | 0.5 |
| Turbulent Viscosity | 0.8 |

---

## STEP 6 — Run

1. **Hybrid Initialization** → Initialize
2. **Number of Iterations:** 500
3. Click **Calculate**
4. Converged when all residuals < **1 × 10⁻⁵** and Cl/Cd plots flatten

Runtime: ~2–5 min per angle.

---

## STEP 7 — Extract Results

- **Reports → Force Reports → Lift/Drag** → Compute
- Or: **File → Export → ASCII** with Cl, Cd, Cm columns

### Repeat for each angle:
Just change Vx, Vy in the inlet BC → re-initialize → re-run. No re-meshing.

### Repeat for each airfoil:
Import new .dat file → re-mesh → re-run.

---

## STEP 8 — Export CSV

Save results as:
```
naca0012_fluent_Re95k.csv
naca0015_fluent_Re95k.csv
naca0018_fluent_Re95k.csv
naca0009_fluent_Re95k.csv
naca63012_fluent_Re95k.csv
```

Format:
```csv
alpha_deg,Cl,Cd,Cm
-35,-1.142,0.312,-0.045
-30,-1.018,0.218,-0.038
...
+35,1.142,0.312,0.045
```

Place in: `CycloProp/cfd_study/results/`

---

## STEP 9 — Cross-Validate Against OpenFOAM

| α | OpenFOAM Cl | Fluent Cl | Diff % | OpenFOAM Cd | Fluent Cd | Diff % |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | — | — | — | — | — | — |
| 5 | — | — | — | — | — | — |
| 10 | — | — | — | — | — | — |
| ... | | | | | | |

**Acceptable:** < 5% Cl difference, < 10% Cd difference.

If both agree → average them for BEMT integration.  
If they disagree → check mesh y⁺, inlet turbulence, reference area.

---

## EXPECTED RESULTS (sanity check)

| Airfoil | Expected Cd₀ | Stall α |
|:---|:---:|:---:|
| NACA 0009 | ~0.013 | ~10–11° |
| **NACA 0012 ★** | **~0.016** | **~12–14°** |
| NACA 0015 | ~0.020 | ~13–15° |
| NACA 0018 | ~0.024 | ~14–16° |
| NACA 63-012A | ~0.010–0.016 | ~11–13° |

---

## QUICK CHECKLIST

```
□ Open Workbench → Fluid Flow (Fluent)
□ Import .dat file in SpaceClaim → build C-domain → Boolean subtract
□ Mesh: inflation 0.005 mm first layer, 20 layers, 1.15 growth
□ Named selections: inlet, outlet, airfoil_wall, symmetry
□ Fluent: k-ω SST + Low-Re corrections
□ Reference Values: Area=0.038, Vel=36.8, Length=0.038
□ Report Definitions: Cl and Cd on airfoil_wall
□ Initialize → 500 iterations → converge < 1e-5
□ Export Cl, Cd → CSV
□ Change Vx/Vy → re-run each angle (no re-mesh)
□ Repeat for all 5 airfoils
□ Compare with OpenFOAM → average if <5% difference
□ Push CSVs to CycloProp/cfd_study/results/
```

---
*CycloProp | PUSHPAK Grand Challenge 2026 | IIT Ropar*
