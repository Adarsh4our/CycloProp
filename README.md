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

## Regression checks

```bash
python -m unittest discover -s tests -v
```

23 checks passed before the final stall-transition and documentation edits. Further test execution was skipped at the user's request. Numerical regression checks do not establish physical accuracy.

## Repository map

| Path | Purpose |
| --- | --- |
| `config/baseline.json` | Current geometry, operating inputs, efficiencies, mass assumptions and CFD plan |
| `scripts/cyclorotor_sizing.py` | Preliminary rotor model and parameter exploration |
| `scripts/project_config.py` | Shared configuration and geometry-derived shaft mass |
| `cfd_study/scripts/` | Geometry preparation, numerical acceptance and bounded polar interpolation |
| `cfd_study/templates/steady/` | Reproducible OpenFOAM case template |
| `CAD/` | Existing SolidWorks models and detailed CAD specification |
| `reports/` | Current preliminary calculation and CFD quality report |
| `CycloProp_PUSHPAK_Stage1_Submission/` | Historical submission snapshot |

Physical validation still requires accepted multi-Re CFD, mesh independence, transient treatment of persistent oscillation, CAD material/mass reconciliation, and structural/thermal/hardware checks. See [docs/VALIDATION.md](docs/VALIDATION.md).
