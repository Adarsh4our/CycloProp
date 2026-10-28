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

Full Python regression test coverage (`pytest -v` against [tests/test_pipeline.py](../tests/test_pipeline.py)) was executed and verified on `2026-10-25` (`DOC-003`): **all 23 tests and 17 subtests passed in 13.18s** (`0` failed, `0` skipped) across `RotorTests` (9 tests), `PolarTests` (6 tests), `CFDWorkflowTests` (6 tests), and `MassTests` (2 tests), confirming regression integrity after the continuous-stall, plot, and default configuration updates. Full OpenFOAM v2412 CFD, transient studies, and physical hardware testing remain external validation work, detailed in [VALIDATION.md](VALIDATION.md).

## Delivered CAD, Simulation & Manufacturing Exports (`CAD-003A/B/C`, `SIM-001A/B/C` & `MFG-001`)

Automated SolidWorks 2026 COM/API completion, clearance verification, coupled 3D kinematic/dynamic analysis, critical-part structural FEA, native motion-study setup, and Deliverable D1 manufacturing exports for the Bench Prototype (`CAD/Design_Completion/Bench_Prototype/`, indexed in [BENCH_PROTOTYPE_MASTER_SUMMARY.md](../CAD/Design_Completion/Bench_Prototype/BENCH_PROTOTYPE_MASTER_SUMMARY.md)) are delivered and verified:

| Task ID | Automation Script | Verification State / Report Artifact | Summary of Delivered Scope |
| --- | --- | --- | --- |
| `CAD-003A` | [complete_bench_rotor_cad003a.py](../CAD/Design_Completion/automation/complete_bench_rotor_cad003a.py) | [CAD003A_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003A_COMPLETION_STATE.json) | `BD_RB_Part1.SLDPRT` multi-body mass/inertia override (`15.6908 g`, $J_{p,\text{blade}} = 1.6708 \times 10^{-6}\text{ kg}\cdot\text{m}^2$), `AISI 4340` material assignment to `MGNR05R`/`MGN5C`/`6806`, `R0.30 mm` step fillets on `BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT`, M5 motor flange fasteners, suppression of 70 legacy flight Savox/tab components & 186 mates, and 38-pose rotor clearance audit (`0.0 mm^3` overlap). |
| `CAD-003B` | [complete_bench_actuation_cad003b.py](../CAD/Design_Completion/automation/complete_bench_actuation_cad003b.py) | [CAD003B_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003B_COMPLETION_STATE.json) | Grounded flexible `BD_Bench_Development_Source.SLDASM` inside `BA_Bench_Actuation_Layout.SLDASM`, added 29 kinematic mates coupling Zaber `NA23C60-T4A` X/Y actuators (`Bench_X_Actuator_Stroke`, `Bench_Y_Actuator_Stroke`, `Bench_CrossSlot_Y_Coupling`), installed 65 reference fasteners/collars, added drop-link/crosshead/plate clearance features, and verified 38-pose coupled XY + $360^\circ$ motion. |
| `CAD-003C` | [complete_bench_cleanup_cad003c.py](../CAD/Design_Completion/automation/complete_bench_cleanup_cad003c.py) | [CAD003C_COMPLETION_STATE.json](../CAD/Design_Completion/Bench_Prototype/CAD003C_COMPLETION_STATE.json) | Added 10 precision fastener/thread/washer/rail/socket reliefs across 7 parts; verified **`0.0000 mm^3` unfiltered all-pair boolean overlap** across **`1,550,190` pair checks** (`486` active solid leaf components, `19.2329 kg` top-level mass, `3.0590 kg` rotor subassembly mass, `0` mate errors). |
| `SIM-001A` | [run_bench_motion_study_sim001a.py](../CAD/Design_Completion/automation/run_bench_motion_study_sim001a.py) | [SIM001A_MOTION_STATE.json](../CAD/Design_Completion/Bench_Prototype/SIM001A_MOTION_STATE.json), [CSV/Plot Outputs](../CAD/Design_Completion/Bench_Prototype/Motion_Study/) | 72-pose ($5^\circ$ increment) 3D SolidWorks rebuild vs analytical vector-loop verification (`1.33e-11 deg` pitch match, `2.02e-11 mm` Oldham COM match); extracted 4-bar whip amplification ($K_\alpha = 1.2846$ at $e = 6.88\text{ mm}$), pitch-link loads ($27.56\text{ N}$ at `1900 RPM` / $33.67\text{ N}$ at `2100 RPM`), Oldham $2\Omega$ dynamics, and Zaber `NA23C60-T4A` ($120\text{ N}$) actuation safety factors ($3.34\times$ peak / $6.03\times$ RMS at `1900 RPM`; $2.74\times$ peak / $4.94\times$ RMS at `2100 RPM` burst). |
| `SIM-001B` | [run_bench_structural_fea_sim001b.py](../CAD/Design_Completion/automation/run_bench_structural_fea_sim001b.py) | [SIM001B_STRUCTURAL_STATE.json](../CAD/Design_Completion/Bench_Prototype/SIM001B_STRUCTURAL_STATE.json), [SIM001_MOTION_AND_STRUCTURAL_REPORT.md](../CAD/Design_Completion/Bench_Prototype/Motion_Study/SIM001_MOTION_AND_STRUCTURAL_REPORT.md) | Critical-part structural stress, Goodman fatigue, Euler buckling, and eccentricity deflection FEA across 4 bottleneck component groups (`SF >= 1.5` and $\Delta e \ll 0.100\text{ mm}$ verified across all groups at `1900 RPM` and `2100 RPM` burst). |
| `SIM-001C` | [setup_native_motion_study_sim001c.py](../CAD/Design_Completion/automation/setup_native_motion_study_sim001c.py) | [SIM001C_MOTION_STUDY_STATE.json](../CAD/Design_Completion/Bench_Prototype/SIM001C_MOTION_STUDY_STATE.json), [MP4](../CAD/Design_Completion/Bench_Prototype/Motion_Study/sim001c_solidworks_native_motion.mp4), [AVI](../CAD/Design_Completion/Bench_Prototype/Motion_Study/sim001c_solidworks_native_motion.avi) | Created `"Motion_Fast_Playback"` configuration (`211` active components, `275` decorative fasteners suppressed) and native SolidWorks `"Motion Study 1"` (`RotaryMotor1` at `30.0 RPM`, `e_x = 6.88 mm`, `61` cached frames over `4.0 s` at `15 FPS`, `0.168 s` solve) in a single visible SolidWorks window. |
| `DOC-003` | — | [BENCH_PROTOTYPE_MASTER_SUMMARY.md](../CAD/Design_Completion/Bench_Prototype/BENCH_PROTOTYPE_MASTER_SUMMARY.md) | Master documentation synchronization, file/SHA-256 manifest, and `pytest -v` regression test verification. |
| `MFG-001` | `scratch_*.py` | [MFG001_PROGRESS_CHECKPOINT.json](../CAD/Design_Completion/Bench_Prototype/Deliverable_D1_Manufacturing/MFG001_PROGRESS_CHECKPOINT.json) | Exported 18 STEP AP214 neutral CAD files, 5 DXF 1:1 flat patterns, 6 assembly orthographic/isometric renders, 22 part renders, and full CAD geometry & BOM dumps (`Deliverable_D1_Manufacturing/`); all 123 `.SLDPRT` files verified untouched. |
