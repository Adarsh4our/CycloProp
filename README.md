# CycloProp

CycloProp is a preliminary cycloidal UAV propulsion design, with Python aerodynamic analysis, SolidWorks CAD, and OpenFOAM airfoil studies.

## Working across chats

Start with the [master-chat workflow](docs/MASTER_CHAT_WORKFLOW.md) and [compact project state](docs/PROJECT_STATE.md). Use the [task-handoff template](docs/TASK_HANDOFF_TEMPLATE.md) to transfer assignments and evidence manually. The first queued specialist task is the [three-case OpenFOAM pilot](docs/tasks/CFD-001_OPENFOAM_PILOT.md).

## Current calculation status

The current inputs live in [config/baseline.json](config/baseline.json). The former Stage 1 figures and performance claims are historical estimates. Use [reports/BASELINE.md](reports/BASELINE.md) and its JSON inputs/hashes for the current calculation.

The corrected preliminary calculation at 2640 RPM and 35 degree cyclic pitch predicts about **8.40 N vertical thrust, 189.41 W electrical power, and 331.11 g estimated module mass**. The model therefore falls below the 10 N thrust target. These values are analytical estimates; aerodynamic, CAD and hardware validation remain pending.

Corrections include vector induced flow, phase calibration for the requested thrust direction, periodic derivatives, continuous empirical stall transitions, explicit convergence failures, and uncapped efficiency checks. The analytical polar remains an empirical, Reynolds-independent approximation.

The specified solid steel shaft contributes 57.71 g before machining. Other BOM component masses remain provisional. A SolidWorks export with correct materials is required before treating the mass budget as verified.

## Setup

Use Python 3.11. The pinned versions in requirements.txt match the development environment.

```bash
python -m venv .venv
# Windows PowerShell:
.venv/Scripts/Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Current analysis

Run from the repository root:

```bash
python scripts/generate_baseline_report.py
python scripts/cyclorotor_bom_motorspec.py
python scripts/generate_kinematics_plot.py
python scripts/test_configs.py
python scripts/cyclorotor_sizing.py
```

The baseline report and BOM go to `reports/`; regenerated plots go to `figures/corrected/`. Geometry exploration retains the baseline component mass and does not predict a new mass for each variant. Invalid or unconverged calculations raise an error rather than produce a compliance claim. The main sizing script performs a wider model exploration and can expose limits outside the baseline.

`generate_engineering_drawings.py` is a legacy assembly schematic. It does not establish production dimensions, CAD mass, or dynamic clearance. Manufacture only from a reconciled CAD model and production drawings.

## CFD workflow

See [cfd_study/README.md](cfd_study/README.md). The shared runner generates each selected airfoil's geometry and records coordinate hashes, mesh settings, fluid properties, Reynolds number, inlet speed and numerical acceptance criteria.

```bash
# Plan only: 5 airfoils x 5 Reynolds numbers x 17 angles
python cfd_study/scripts/run_openfoam_sweep.py
# Generate a small case set without running OpenFOAM
python cfd_study/scripts/run_openfoam_sweep.py --prepare --airfoils naca0012 --reynolds 50000 --angles -5 0 5
# Linux with OpenFOAM v2412 sourced: generate and solve a fresh case set
python cfd_study/scripts/run_openfoam_sweep.py --run --airfoils naca0012 --reynolds 50000 --angles -5 0 5
```

Prepared studies and executed studies use separate fresh directories. `--run` prepares its own cases; it does not resume an earlier `--prepare` directory. Existing results are never overwritten by the shared runner. The five `run_bladeN_sweep.py` entry points delegate to the same implementation.

Audit historical histories with:

```bash
python cfd_study/scripts/cfd_quality.py
```

This returns a nonzero exit code when cases fail acceptance. The saved audit accepts 1 of 85 cases under the current criteria, so none of the five historical full polars is accepted. Historical files remain available in `cfd_study/results/` for diagnosis.

## Bench Prototype CAD, Motion Study & Structural FEA (`CAD-003A..C`, `SIM-001A..C`, `MFG-001`)

Full SolidWorks 2026 completion, all-pair boolean clearance verification, coupled 3D kinematic/dynamic simulation, critical-part structural FEA, native motion-study setup, and manufacturing CAD exports for the Bench Prototype (`CAD/Design_Completion/Bench_Prototype/`) are documented in:

- **Master Summary & SHA-256 Manifest:** [CAD/Design_Completion/Bench_Prototype/BENCH_PROTOTYPE_MASTER_SUMMARY.md](CAD/Design_Completion/Bench_Prototype/BENCH_PROTOTYPE_MASTER_SUMMARY.md)
- **Motion & Structural FEA Report (`SIM-001A/B`):** [CAD/Design_Completion/Bench_Prototype/Motion_Study/SIM001_MOTION_AND_STRUCTURAL_REPORT.md](CAD/Design_Completion/Bench_Prototype/Motion_Study/SIM001_MOTION_AND_STRUCTURAL_REPORT.md)
- **Deliverable D1 Manufacturing Exports (`MFG-001` Checkpoint):** `CAD/Design_Completion/Bench_Prototype/Deliverable_D1_Manufacturing/` (18 STEP AP214 models, 5 DXF flat patterns, 6 assembly views, 22 part renders, and geometry/BOM JSON dumps)

Key verified Bench Prototype metrics:
- **Top-Level Assembly (`BA_Bench_Actuation_Layout.SLDASM`):** `19.2329 kg` active mass (`3.0590 kg` rotor + 400W drive subassembly `BD_Bench_Development_Source.SLDASM`), `486` active solid leaf components in `"Default"` (`211` in `"Motion_Fast_Playback"`), `0` mate errors, and **`0.0000 mm^3` unfiltered all-pair boolean overlap** across `1,550,190` pair checks over 36 swept poses.
- **Coupled 3D Kinematics & Dynamics (`SIM-001A`):** 72-pose ($5^\circ$ step) SolidWorks 3D rebuild matches the analytical vector-loop solver to `1.33e-11 deg` on blade pitch and `2.02e-11 mm` on Oldham COM; Zaber `NA23C60-T4A` ($120\text{ N}$) actuation safety factors are $3.34\times$ peak / $6.03\times$ continuous RMS at `1900 RPM` and $2.74\times$ peak / $4.94\times$ continuous RMS at `2100 RPM` burst.
- **Critical-Part Structural FEA (`SIM-001B`):** All 4 critical bottleneck groups pass $SF \ge 1.5$ across `1900 RPM` nominal and `2100 RPM` burst regimes, with total elastic eccentricity deflection $\Delta e_X = 0.0055\text{ mm}, \Delta e_Y = 0.0165\text{ mm} \ll 0.100\text{ mm}$ budget.
- **Native SolidWorks `Motion Study 1` (`SIM-001C`):** Configured on `"Motion_Fast_Playback"` (`30.0 RPM` `RotaryMotor1`, $e_X = 6.88\text{ mm}$, `61` cached frames over `4.0 s` at `15 FPS`), with exported `.mp4` and `.avi` animations in `CAD/Design_Completion/Bench_Prototype/Motion_Study/`.

## Regression checks

```bash
python -m unittest discover -s tests -v
# or:
pytest -v
```

All **23 tests and 17 subtests pass** (`0` failed, `0` skipped) across `RotorTests`, `PolarTests`, `CFDWorkflowTests`, and `MassTests` in [tests/test_pipeline.py](tests/test_pipeline.py). Numerical regression checks do not establish physical accuracy.

## Repository map

| Path | Purpose |
| --- | --- |
| `config/baseline.json` | Current geometry, operating inputs, efficiencies, mass assumptions and CFD plan |
| `scripts/cyclorotor_sizing.py` | Preliminary rotor model and parameter exploration |
| `scripts/project_config.py` | Shared configuration and geometry-derived shaft mass |
| `cfd_study/scripts/` | Geometry preparation, numerical acceptance and bounded polar interpolation |
| `cfd_study/templates/steady/` | Reproducible OpenFOAM case template |
| `CAD/` | SolidWorks flight-module models and detailed CAD specification |
| `CAD/Design_Completion/Bench_Prototype/` | Verified Bench Prototype assemblies, CAD automation states, `Motion_Study/` reports/animations, and `Deliverable_D1_Manufacturing/` STEP/DXF/render exports |
| `CAD/Design_Completion/automation/` | SolidWorks 2026 COM automation & verification scripts (`CAD-003A..C`, `SIM-001A..C`) |
| `docs/` | Project state, implementation status, validation requirements, and task handoffs |
| `reports/` | Current preliminary calculation and CFD quality report |
| `CycloProp_PUSHPAK_Stage1_Submission/` | Historical Stage 1 submission snapshot |

Physical validation still requires accepted multi-Re CFD, mesh independence, transient treatment of persistent oscillation, flight-baseline BOM reconciliation, and hardware bench testing. See [docs/VALIDATION.md](docs/VALIDATION.md).
