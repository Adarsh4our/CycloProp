# Remaining engineering validation

The software changes correct data handling and internal numerical consistency. They do not certify the aerodynamic model or physical hardware without external testing.

## CFD

1. Execute the generated multi-Re study in OpenFOAM v2412. Retain case manifests, checkMesh logs, solver logs and numerical quality reports.
2. Compare at least three mesh resolutions while holding geometry, fluid, discretization and boundary conditions fixed. Record coefficient changes, wall resolution and force stability; select acceptance tolerances before comparing results.
3. Investigate persistent oscillation using a transient solver. Record physical timestep, Courant limit, startup exclusion, sampling interval and averaging duration. Repeat with a smaller timestep and longer averaging window. Quantify mean and variation; do not treat steady SIMPLE iterations as physical time samples.
4. Validate static polars against independent reference data at matching Reynolds number, surface condition and turbulence assumptions. Then assess cyclic pitching at the rotor's amplitude and frequency. A static airfoil comparison alone does not validate rotor hover.
5. Import only complete numerically accepted tables within the rotor operating envelope. The current integration path accepts steady numerical exports; transient data requires a separately reviewed time-averaging and acceptance record before import.

## CAD and mass

### Completed Bench Prototype SolidWorks 2026 Verification (`CAD-003A..C` & `SIM-001A..C`)

For the **Bench Prototype** (`CAD/Design_Completion/Bench_Prototype/`, indexed in [BENCH_PROTOTYPE_MASTER_SUMMARY.md](../CAD/Design_Completion/Bench_Prototype/BENCH_PROTOTYPE_MASTER_SUMMARY.md)), full SolidWorks 2026 component mass/inertia extraction, material assignment, all-pair boolean clearance verification, coupled 3D motion analysis, and critical-part structural FEA are **complete and verified**:

1. **SolidWorks 2026 Mass & Inertia Exports ([CAD003A_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003A_COMPLETION_STATE.json), [CAD003B_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003B_COMPLETION_STATE.json), [CAD003C_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003C_COMPLETION_STATE.json), [SIM001A_MOTION_STATE.json](../CAD/Design_Completion/Bench_Prototype/SIM001A_MOTION_STATE.json)):**
   - Top-level bench actuation assembly (`BA_Bench_Actuation_Layout.SLDASM`): **`19.2329 kg` (`19,232.87 g`)** across `486` active solid leaf components (`0` parts with default `1000 kg/m^3` water density).
   - Bench rotor + 400W drive subassembly (`BD_Bench_Development_Source.SLDASM`): **`3.0590 kg` (`3,059.00 g`)**.
   - Multi-body NACA 0012 blade (`BD_RB_Part1.SLDPRT`): **`15.6908 g`** bare blade (`19.1928 g` with offset pitch arm `BD_RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE.SLDPRT` at `2.5027 g` and clamped root hardware), $\text{COM} = (15.243, 0.0, 110.0)\text{ mm}$ ($5.743\text{ mm}$ aft of quarter-chord pivot), $J_{p,\text{blade}} = 1.6708 \times 10^{-6}\text{ kg}\cdot\text{m}^2$, and total oscillating pitch inertia $J_{p,\text{total}} = 1.9800 \times 10^{-6}\text{ kg}\cdot\text{m}^2$ ($1.316\times$ the uniform-slab estimate in `scripts/cyclorotor_sizing.py`).
   - Comparison with untouched preliminary flight baseline ([config/baseline.json](../config/baseline.json), `SHA-256: 2445c715...`): CAD actual blade mass is `15.6908 g` vs `12.5 g` preliminary allocation; the machined 260 mm steel shaft (`Before_Main_Drive_Shaft.SLDPRT`) is `53.21 g` and the extended 311 mm bench drive shaft (`BD_RB_3-Drive_Shaft.SLDPRT`) is `68.88 g`, compared with `57.708 g` for the gross unmachined 6 mm $\times$ 260 mm rod in `config/baseline.json`.
2. **Unfiltered Full-Motion Boolean Clearance Certification ([CAD003C_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003C_COMPLETION_STATE.json)):**
   - Executed **`1,550,190` unfiltered all-pair solid boolean intersection checks** (`IBody2::Operations2(SWBODYINTERSECT)`) across `486` active leaf components over 36 swept poses covering $(0,0)$, cardinal $(\pm 6.88, 0)\text{ mm}$ and $(0, \pm 6.88)\text{ mm}$, and diagonal $(\pm 4.8649, \pm 4.8649)\text{ mm}$ eccentricities with $360^\circ$ shaft rotation: **`0.0000 mm^3` maximum boolean overlap** and **`0` active mate errors**.
3. **72-Pose Coupled 3D Kinematic & Dynamic Verification ([SIM001A_MOTION_STATE.json](../CAD/Design_Completion/Bench_Prototype/SIM001A_MOTION_STATE.json)):**
   - 72-pose ($5^\circ$ increment) SolidWorks 2026 rebuild sweep matches the exact 3D analytical vector-loop solver to within **`1.33e-11 deg`** on blade pitch $\theta_p(\psi)$ and **`2.02e-11 mm`** on Oldham floating-disk COM position.
   - At $e = 6.88\text{ mm}$ ($\theta_{\max} = \pm 34.991^\circ$), finite 4-bar geometry produces a $+28.46\%$ non-harmonic pitch angular acceleration whip amplification ($K_\alpha = 1.2846$), peak pitch-link axial load of $27.56\text{ N}$ (`1900 RPM`) / $33.67\text{ N}$ (`2100 RPM` burst), and Zaber `NA23C60-T4A` ($120\text{ N}$ rated thrust) peak rapid-slew safety factors of **$3.34\times$ (`1900 RPM` dry, $35.95\text{ N}$) / $2.74\times$ (`2100 RPM` burst, $43.79\text{ N}$)** and continuous RMS safety factors of **$6.03\times$ ($19.91\text{ N}$) / $4.94\times$ ($24.30\text{ N}$)**.
4. **Critical-Part Structural Stress, Fatigue, Buckling & Deflection Verification ([SIM001B_STRUCTURAL_STATE.json](../CAD/Design_Completion/Bench_Prototype/SIM001B_STRUCTURAL_STATE.json), [SIM001_MOTION_AND_STRUCTURAL_REPORT.md](../CAD/Design_Completion/Bench_Prototype/Motion_Study/SIM001_MOTION_AND_STRUCTURAL_REPORT.md)):**
   - All 4 critical component groups pass $SF \ge 1.5$ across both `1900 RPM` nominal and `2100 RPM` burst regimes:
     - **Stepped Lower Bearing Pedestal (`BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT`):** `R0.30 mm` step fillets reduce peak notch stress at $Z = 8.5\text{ mm}$ ($D12 \to d5.5\text{ mm}$) by **$-46.3\%$** ($K_t = 2.429$ vs $4.539$ sharp); with AISI 4340 Normalized Steel ($\sigma_y = 710\text{ MPa}$), $SF_y = 5.14\times$ (steady hold) / $3.71\times$ (rapid slew) at `1900 RPM`, $SF_y = 4.22\times$ (hold) / $3.05\times$ (slew) at `2100 RPM` burst, and Goodman infinite-life fatigue $SF_{\text{Goodman}} = 5.09\times$ (`1900 RPM` slew) / $4.19\times$ (`2100 RPM` burst slew). *(Shop drawing note: AISI 4140/4340 Q&T or 17-4PH H900 is mandatory; do not substitute annealed 303/304 SS).*
     - **Blade Root $D3.0\text{ mm}$ Trunnion, ISO 8750 $D1\times 8\text{ mm}$ Coiled Pin & $OD6/ID4$ Carbon Spar (`BD_RB_Part1.SLDPRT`):** 7075-T6 trunnion net section $SF_y = 3.49\times$ (`1900 RPM`) / $2.54\times$ (`2100 RPM`) with M2 split-clamp parallel load sharing ($1.90\times$ / $1.56\times$ unassisted $K_f$); ISO 8750 $D1\times 8\text{ mm}$ heavy-duty coiled spring pin ($750\text{ N}$ double-shear rating) $SF_{\text{ult}} = 3.16\times$ / $2.59\times$; $OD6.0 \times ID4.0\text{ mm}$ carbon spar $SF = 5.65\times$ / $4.63\times$ ($\delta_{\text{mid}} = 2.55 / 3.11\text{ mm}$).
     - **Offset Pitch Arm, Carbon Pitch-Link Buckling & Oldham Delrin Tongues:** 7075-T6 pitch arm $SF_y = 18.71\times$ / $15.32\times$; $OD2.0 \times ID1.0\text{ mm}$ carbon pitch link Euler buckling $SF_{\text{buckling}} = 5.78\times$ (`1900 RPM`) / $4.73\times$ (`2100 RPM` burst); POM Delrin Oldham floating disk tongues $SF_y = 36.27\times$ / $29.70\times$ ($p_c = 1.48 / 1.80\text{ MPa}$).
     - **Actuator Drop Links & Eccentricity Deflection Budget:** `BA_X_Actuator_Drop_Link` $SF_y = 48.15\times$ / $39.53\times$; `BA_Y_Cross_Slot_Drop_Link` $SF_y = 129.90\times$ / $106.61\times$; total combined elastic eccentricity loss $\Delta e_X = 0.00453 / 0.00552\text{ mm}$ and $\Delta e_Y = 0.01358 / 0.01653\text{ mm}$ ($\Delta\theta_p = 0.069^\circ / 0.084^\circ$), more than **$6.0\times$ below the $0.100\text{ mm}$ ($0.50^\circ$) control budget**.

### Remaining External Hardware & Flight-Baseline Reconciliation

Physical hardware weighing, bench thrust-stand testing, and any authorized update to the preliminary flight-module BOM in [config/baseline.json](../config/baseline.json) remain separate from the completed Bench Prototype CAD/FEA verification above.

## Design decision

The corrected preliminary baseline predicts about 8.40 N vertical thrust at 2640 RPM, 189.41 W electrical demand and 331.11 g estimated mass. It falls below the 10 N thrust target. Higher RPM, geometry changes and mass reduction require motor/ESC thermal assessment, strength/stiffness checks and updated CFD. The analytical estimate is not a flight or fabrication sign-off.

## Evidence status

- **Python regression test suite (`pytest -v`) verified (`DOC-003`, `2026-10-25`):** **23 passed, 17 subtests passed in 13.18s** (`0` failed, `0` skipped) in [tests/test_pipeline.py](../tests/test_pipeline.py), covering `RotorTests`, `PolarTests`, `CFDWorkflowTests`, and `MassTests` after all stall/plot/default updates.
- **Bench Prototype SolidWorks 2026 CAD, Clearance, Motion & Structural FEA verified (`CAD-003A..C`, `SIM-001A..C`, `2026-10-25`):** `1,550,190` all-pair boolean checks (`0.0000 mm^3` overlap), 72-pose 3D kinematic match (`1.33e-11 deg`), Zaber `NA23C60-T4A` actuation margins ($SF \ge 2.74\times$), critical-part structural margins ($SF \ge 1.5$ across all 4 groups), and native SolidWorks `"Motion Study 1"` fast-playback configuration completed.
- The baseline report, BOM and CFD plan in `reports/` reflect `config/baseline.json` (`2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f`).
- Existing CFD histories were audited: 1 accepted case, 84 rejected cases.
- **Pending external validation:** New OpenFOAM v2412 solves (`CFD-001`), transient/mesh sensitivity studies, and physical bench hardware measurements remain pending. OpenFOAM was unavailable in the local Windows environment; WSL listed only Docker Desktop.
