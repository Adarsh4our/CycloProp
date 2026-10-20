# Calculation corrections

Policy: planning=deep; context_depth=dependency; verification_depth=impact;
delegation=none. Scope: current Python analysis, CFD automation, configuration,
regression tests and documentation. Existing CAD binaries and raw CFD results
are evidence, not generated outputs of this change.

Acceptance checks:

- Signed polar interpolation; reject malformed data and uncovered angle/Re values.
- Vector induced-flow closure; rotation consistency, vertical thrust targeting,
  explicit convergence and power validity.
- CFD acceptance requires residual and coefficient stability; accepted exports
  are separate from historical raw data.
- Every new CFD case records geometry, fluid, mesh and operating conditions.
- Shaft mass and BOM totals derive from one configuration.
- Current commands work from a fresh checkout with documented dependencies.

Numerical regression checks cannot establish aerodynamic accuracy. New CFD runs,
mesh/time-step independence, CAD material/mass exports and physical validation
must be recorded separately.

## Delivered software changes

Vector inflow, phase targeting, signed bounded multi-Re CFD interpolation, steady numerical acceptance, per-geometry case generation, shared baseline/BOM inputs and a continuous empirical stall join are implemented. Reports are in `reports/`.

23 checks passed before the last stall/plot/default edits; no further tests were run at the user's request. The baseline report, BOM and CFD plan were generated after the stall correction. Full CFD, transient studies and CAD verification remain external validation work, detailed in `docs/VALIDATION.md`.
