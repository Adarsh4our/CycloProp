# CycloProp CFD workflow

The current runner is `scripts/run_openfoam_sweep.py`. It regenerates the selected geometry for every case, uses the configured chord and fluid properties to compute inlet velocity from Reynolds number, and writes provenance in `case.json`. Inputs and acceptance criteria come from `../config/baseline.json`.

## Prepare or execute

Run these commands from the repository root. Planning and preparation work on Windows or Linux. Execution requires an environment with OpenFOAM v2412 sourced (`blockMesh`, `checkMesh`, `simpleFoam` on PATH).

```bash
# Write reports/cfd_plan.json; no meshing or solving
python cfd_study/scripts/run_openfoam_sweep.py
# Prepare fresh cases; no solver
python cfd_study/scripts/run_openfoam_sweep.py --prepare --airfoils naca0012 --reynolds 50000 --angles -5 0 5
# Prepare and execute fresh cases on Linux
python cfd_study/scripts/run_openfoam_sweep.py --run --airfoils naca0012 --reynolds 30000 50000 75000 100000 125000
```

Each invocation uses a fresh timestamped directory under `cfd_study/runs/`. `--run-dir` selects another fresh output path. Existing directories are refused. Prepared runs are reviewable artifacts; to execute, invoke `--run` with a new directory. The historical five blade runners are compatibility entry points for this same workflow.

The template has fixed 1% turbulence intensity and length scale 0.07 chord. Those assumptions, the turbulence model, wall treatment and boundary placement need sensitivity studies. Inlet flow remains along +X; the mesh rotates the airfoil. Unit span gives reference area equal to chord in square metres. Do not apply an additional wind-axis rotation to the exported coefficients.

## Numerical acceptance

`checkMesh` must report success. A steady case must also pass all criteria in `cfd.acceptance`: sufficient samples, finite values, positive drag, bounded final residuals, and stable lift, drag and moment coefficients. Final residuals alone are insufficient.

Accepted coefficients are the mean of the stable final window of the steady iteration history. They are numerical estimates of a steady solution. This procedure does not establish a physical time average of an oscillating flow.

Only a complete accepted angle group is exported to the run's `polars/` directory. Each CSV has a JSON sidecar binding its content hash, Reynolds number, angle grid, inputs and acceptance results. Rejected cases keep their logs and quality reasons. They are excluded from the accepted export.

```bash
python cfd_study/scripts/cfd_quality.py
python cfd_study/scripts/integrate_cfd_polars.py --results cfd_study/runs/RUN_ID/polars
```

The integration tool checks signed angle order, unique points, finite coefficients and numerical acceptance metadata. It interpolates linearly in angle and Reynolds number. Queries outside either range fail explicitly. Unsupported airfoils also fail explicitly. Select one source per airfoil and Reynolds number; duplicate sources require explicit cross-comparison and investigation before averaging.

A complete multi-Re dataset is needed for a rotor solve. The nominal preliminary baseline spans approximately Re 44,000 to 91,000. A single Re 95,000 table cannot cover it. Static CFD polars also require validation before supporting cyclic-pitch performance claims.

## Historical results

`results/` and `openfoam/blade*/` retain the original simulations. Under the current steady acceptance policy, 1 of 85 saved cases passes; no complete historical airfoil polar qualifies. `reports/cfd_quality.csv` records each rejection reason. No Fluent cross-validation or new CFD solve was executed as part of these software corrections.

## Persistent oscillation

An oscillating steady iteration history is rejected. The follow-up is a transient investigation with documented physical timestep, Courant number, initialization, discarded startup interval, averaging duration and time/mesh independence. Follow [the validation protocol](../docs/VALIDATION.md); smoothing or symmetrizing iteration traces does not authorize acceptance.
