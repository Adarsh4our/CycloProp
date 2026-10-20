# CFD-001: fresh OpenFOAM pilot

**Discipline:** CFD. **Status:** awaiting external execution. **Date:** 20 October 2026.

## Objective and completion condition

Execute three fresh NACA 0012 steady cases at Re 50,000 and angles -5, 0 and +5 degrees using the current shared runner. This is the first pending step toward replacing historical, mostly rejected CFD with traceable data. The pilot checks the executable pipeline and numerical behavior before committing to the full study.

Delivery is complete when all three attempts have manifests, mesh/solver logs as far as execution reached, quality results and a returned handoff. Successful pilot acceptance additionally requires all three cases to pass the unchanged numerical criteria and the complete three-angle CSV/JSON export. Rejected cases are a needs-revision outcome, not a successful pilot. An unavailable environment is awaiting external work.

## Current inputs and file packet

Supply a snapshot of the local files below, not just this brief or a remote repository URL. Include repository commit plus relevant uncommitted diff/files; current local work includes uncommitted runner, quality and template changes. The receiving specialist must confirm access before execution.

- This brief, [PROJECT_STATE.md](../PROJECT_STATE.md), [TASK_HANDOFF_TEMPLATE.md](../TASK_HANDOFF_TEMPLATE.md) and [OpenFOAM specialist prompt](../OpenFOAM_Agent_Prompt.md).
- `config/baseline.json`, `reports/BASELINE.md`, `reports/baseline.json`, `reports/cfd_quality.csv` and `docs/VALIDATION.md`.
- `requirements.txt`, `scripts/project_config.py` and `cfd_study/README.md`.
- All `cfd_study/scripts/*.py`, the complete `cfd_study/templates/steady/` tree and `cfd_study/airfoil_coords/naca0012_normalized.dat`.

Sources are the supplied repository files. The current calculation revision is `2026-10-20-corrected-preliminary`: four blades, radius 0.095 m, span 0.220 m, chord 0.038 m, 2640 RPM and 35 degree cyclic pitch amplitude. The saved analytical estimate is 8.400 N, 189.41 W and 331.108 g estimated mass. These are calculated/assumed, not measured. The calculated rotor Re envelope is 43,774–91,317; this pilot does not cover it.

At brief preparation, repository HEAD was `d2b8198769d7310ef4c8cdb40d2675c7164ecf1a` with relevant uncommitted work; that commit alone is not the input snapshot. The saved report's hashes were checked against local files:

- `config/baseline.json`: SHA-256 `2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f`.
- `scripts/cyclorotor_sizing.py`: SHA-256 `c726253f7722ecfde1e1ae1e7af5f199dd3b4abdfd824bae503375cf9a863298`.

Transfer the full packet with its current contents and record its hashes in the returned result; the runner records its own, coordinate and template hashes in the new run's manifests.

Historical CFD audit: 1 of 85 saved cases accepted, no complete polar. Do not reuse those tables as accepted pilot data.

## Permitted changes and constraints

- May create one fresh run directory under `cfd_study/runs/` and a returned-result document supplied back to the master. Preserve raw histories, existing runs and unrelated local edits.
- No baseline, source-code, template, coordinate, mesh-setting or acceptance-policy edits in this assignment. Propose necessary changes to the master with logs and a minimal suggested correction.
- Solver execution in the supplied Linux/OpenFOAM environment is the task. Installation requiring privileges or an unavailable license/environment returns as an external dependency. No commit, push, publication or external messaging is assigned.
- Python 3.11 with `requirements.txt` dependencies; OpenFOAM v2412 sourced, with `blockMesh`, `checkMesh` and `simpleFoam` on PATH. Record actual versions and source snapshot. Consult official version-specific documentation if troubleshooting requires API/solver details.
- Fluid assumptions: rho 1.225 kg/m3, mu 1.81e-5 Pa s. Speed is `Re * mu / (rho * chord)` = approximately 19.4415 m/s here.
- Use the runner's SST template, 1% inlet turbulence intensity and length scale 0.07 chord. They are assumptions requiring later sensitivity studies.
- The runner keeps inlet along +X and rotates the airfoil mesh. Its axes are lift +Z, drag +X and pitch +Y, with unit reference span, area 0.038 m2 and length 0.038 m. Do not rotate exported coefficients again.

## Procedure and evidence

From the supplied repository root, after the environment is ready:

```bash
python cfd_study/scripts/run_openfoam_sweep.py --run --airfoils naca0012 --reynolds 50000 --angles -5 0 5
```

This prepares and solves a new timestamped directory; record the printed path and exit status. It does not resume a `--prepare` directory. Do not rerun into an existing directory. Do not use the default command as a solve: without `--run` it only writes a plan.

Retain `plan.json`, every `case.json`, `log.blockMesh`, `log.checkMesh`, `log.simpleFoam`, force coefficient histories, `history.csv` and `quality.json` where generated. If a step fails before an artifact exists, identify the absent artifact and retain the failure output. Case paths are `naca0012/Re50000/alpha_-5`, `alpha_+0` and `alpha_+5` inside the run directory.

Acceptance uses `cfd.acceptance` unchanged: final 20 samples, finite/increasing history, nonnegative drag, residual maxima at most 1e-4 for p/Ux/Uz/k/omega, and Cl/Cd/Cm peak-to-peak ranges at most `0.002 + 0.02 * abs(window_mean)`. `checkMesh` must report `Mesh OK.`; run length is 2000 SIMPLE iterations. `cfd_quality.py:assess_history` defines the exact policy. Steady iteration windows are not physical time averages.

If all three pass, retain `polars/naca0012_openfoam_Re50000.csv` and its `.json` sidecar, including CSV hash, input manifests and acceptance results. A complete requested three-angle group is still only a pilot table. Do not import it into a full rotor calculation or call it a complete operational polar.

Return the completed result section of the handoff template, exact commands/status, environment versions, input/run provenance, coefficient means/ranges, residual maxima, rejection reasons and artifact paths. Supply the artifacts themselves or access the reviewer can verify; a path in another machine is insufficient.

## Deferred checks and return conditions

Full five-airfoil/five-Re/17-angle execution (425 cases), three-mesh comparison, transient timestep/averaging studies, independent reference comparison, cyclic pitching, CAD and hardware checks are deferred to later tasks owned by the master for assignment to the relevant CFD/CAD/hardware specialists. They block aerodynamic, rotor-performance and fabrication validation; pilot numerical success cannot close them.

Return to the master for unavailable inputs/environment, source/hash conflicts, geometry or sign inconsistencies, proposed numerical-setting changes, persistent oscillation or failure requiring code/template changes. Routine environment sourcing and log inspection are within scope. Never relax criteria, smooth/symmetrize histories or fabricate missing data to pass. Persistent oscillation requires a separately scoped transient investigation.

A separate CFD reviewer must inspect the run evidence before the master accepts a successful pilot and scopes expansion. Missing review access leaves acceptance unverified.

## Handoff readiness record

20 October 2026, local documentation check: the file packet and commands were checked against `run_openfoam_sweep.py`, `cfd_quality.py`, baseline files and the steady template. The runner supports the specified CLI, creates fresh directories, produces the named artifacts and exports only a fully accepted requested group. Configuration establishes the three cases and acceptance numbers above. Relative document links and required packet paths were checked locally.

A read-only Python standard-library check passed for eight documentation files: 42 local Markdown links resolved, code fences balanced, baseline input/solver hashes matched the saved report, the configured full study contained 425 cases, the saved audit contained 1 accepted and 84 rejected cases, and required packet paths existed. `git diff --check` passed for the edited tracked documentation. No generated engineering reports were overwritten.

This is a written handoff check by the implementation agent, not an independent engineering review or a fresh-chat execution. No OpenFOAM pilot, physical validation or model regression tests were run for this documentation task. The first specialist must still confirm actual input access and environment before beginning.
