# CycloProp project state

Updated 20 October 2026. This is the compact working record for the master chat. Update it after each task disposition; preserve detailed history in the linked sources.

## Current baseline

Calculation revision: `2026-10-20-corrected-preliminary`. Inputs: [config/baseline.json](../config/baseline.json). Saved output and provenance: [reports/baseline.json](../reports/baseline.json), summarized in [BASELINE.md](../reports/BASELINE.md).

| Item | Current value | Evidence status |
| --- | --- | --- |
| Geometry | Radius 95 mm, span 220 mm, chord 38 mm, four NACA 0012 blades, quarter-chord pivot | Assumed design inputs; CAD reconciliation pending |
| Operating point | 2640 RPM, 35 degree sinusoidal pitch amplitude | Assumed calculation inputs |
| Vertical thrust / electrical power | 8.400 N / 189.41 W | Calculated, empirical analytical polars; physical validation pending |
| Figure of merit | 0.5134 | Calculated; supersedes earlier performance claims |
| Module mass | 331.108 g | Estimated BOM, not measured or CAD verified |
| Solid shaft mass | 57.708 g; diameter 6 mm, length 260 mm, density 7850 kg/m3 | Calculated gross geometry; machining unverified |
| Rotor Reynolds envelope | 43,774 to 91,317 | Calculated at this operating point |
| Target | At least 10 N thrust | Design target in current project records; baseline falls short |

No measured aerodynamic, CAD mass or hardware validation is established by these reports. Analytical coefficients remain empirical and Reynolds independent. Uniform inflow, blockage factor 0.96, component masses and efficiency assumptions remain provisional; see the baseline JSON and [VALIDATION.md](VALIDATION.md).

## Accepted working decisions

These are the current calculation/workflow decisions, not a fabrication or flight release.

| ID | Decision | Source / implication |
| --- | --- | --- |
| D-01 | Use the corrected preliminary inputs and report for calculations. | [README](../README.md), baseline files; older Stage 1 and knowledge-base performance claims are superseded. |
| D-02 | Retain historical CFD as diagnostic evidence; use accepted exports for integration. | [CFD workflow](../cfd_study/README.md), [saved audit](../reports/cfd_quality.csv): 1 of 85 cases accepted, no complete historical polar. |
| D-03 | Use multi-Re signed polars with bounded interpolation. | [CFD workflow](../cfd_study/README.md); a single Re 95,000 table does not cover the nominal rotor envelope. |
| D-04 | Keep numerical acceptance, independent physical validation and deferred testing distinct. | [VALIDATION.md](VALIDATION.md); oscillating steady histories require transient investigation. |
| D-05 | One master, one specialist per task, separate review for significant engineering changes; manual handoffs and one active implementation. | User's master-chat workflow plan; [workflow guide](MASTER_CHAT_WORKFLOW.md). |

## Unresolved issues and external work

| ID | Issue / next action | Evidence and claim blocked |
| --- | --- | --- |
| I-01 | Execute fresh multi-Re CFD; begin with CFD-001. Requires Linux with OpenFOAM v2412. | [VALIDATION.md](VALIDATION.md): prior local Windows environment had no usable OpenFOAM; accepted current polars pending. |
| I-02 | Complete mesh, timestep, averaging and turbulence/transition sensitivity studies, then independent reference and cyclic-pitch validation. Select comparison tolerances before studies. | [VALIDATION.md](VALIDATION.md); static numerical acceptance cannot verify rotor hover. |
| I-03 | Reconcile shaft/endplate dimensions, blade profile, materials, interfaces and full-motion clearances against CAD; export component masses. | [CAD specification](../CAD/CycloProp_Rev3_Master_CAD_Specification.md), [VALIDATION.md](VALIDATION.md). Binary CAD not verified. |
| I-04 | Resolve thrust shortfall through an explicit design decision with motor/ESC thermal and structural assessment. | 8.40 N calculated versus 10 N target; no RPM/geometry change authorized by workflow setup. |
| I-05 | Regression coverage after final model edits remains unverified. | [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md): 23 checks passed before final edits; later tests were skipped at the user's request. Do not describe current model as regression verified. |
| I-06 | Treat conflicting historical specifications as issues before baseline changes. | [knowledge base](../CYCLOPROP_MASTER_KNOWLEDGE_BASE.md) retains historical compliance/frozen-design language; its correction notice takes precedence for calculation claims. |

## Task register

| Task | Disposition | Evidence / next step |
| --- | --- | --- |
| WF-001: master-chat workflow documentation | Complete for documentation scope | Guide, state, template and revised CFD prompts delivered; [CFD-001 readiness record](tasks/CFD-001_OPENFOAM_PILOT.md#handoff-readiness-record) documents the written handoff check. No engineering validation claimed. |
| CFD-001: three-case OpenFOAM pilot | Awaiting external work; first queued specialist assignment | [Filled brief](tasks/CFD-001_OPENFOAM_PILOT.md). No specialist execution or independent review yet. |

No implementation task is currently executing. CFD-001 becomes active when assigned to a specialist with the required file packet and environment.

## Evidence discipline

Use [TASK_HANDOFF_TEMPLATE.md](TASK_HANDOFF_TEMPLATE.md) for assignments and returns. Record revisions/hashes and relevant dirty-worktree files when transferring work. Baseline report hashes identify saved inputs/solver; mismatches must be investigated. Missing evidence is unverified, and deferred checks stay open with an owner and a blocked claim. Only record a baseline decision as newly accepted when the user has accepted it.
