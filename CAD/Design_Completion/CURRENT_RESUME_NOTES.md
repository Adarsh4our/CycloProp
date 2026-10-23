# Current resume notes

## Latest checkpoint: starting-state preservation and numerical requirements

Read [NUMERICAL_REQUIREMENTS_REGISTER.md](NUMERICAL_REQUIREMENTS_REGISTER.md), [REMAINING_IMPLEMENTATION_STATUS.json](REMAINING_IMPLEMENTATION_STATUS.json), [STARTING_POINT_CHECKPOINT.json](STARTING_POINT_CHECKPOINT.json) and [STARTING_RECOVERY_COMPARISON.json](STARTING_RECOVERY_COMPARISON.json) first. These supersede earlier load-screen adequacy claims, not the retained native geometry or historical evidence files.

The current live pose differs from both the saved working assembly and the prior balloon-task recovery. Those two comparison copies agree on inspected poses/constraints. All original disk model and drawing sources are unchanged. Current dirty main assembly, Assem3 and cartridge subassembly were each saved as separate copies under Checkpoints/START_20261023T042432Z/Live. Inspected live poses were preserved through the read-only comparison; no geometry, configuration, travel constraint or setup hold was changed.

New physical finding: historical inertia screens omitted the moment from blade COM offset about the accelerating quarter-chord pivot. Keeping their12.5g/uniform-chord assumptions raises the rod-force estimate from15.96N to87.40N before aero/friction. Do not use the old rod/pin/bearing/post/servo screens as operating-load acceptance. The new script checks the correction against analytic and numerical identities. Proposed broad load caps and pitch/duty/thermal/endfloat limits remain provisional; no physical release.

Next task is actual blade construction and mass/COM/inertia, then realistic complete loads and actuator/drive selection. No replacement actuator or purchase list has been released. Manufacturing details and final native motion/clearance campaign remain outstanding. All steps and exact verification limits are recorded in REMAINING_IMPLEMENTATION_STATUS.json. The prior documentation tasks below remain valid in their stated scope.

## Latest completed task: ballooned assembly views

CP-RB-003_BALLOONED_ASSEMBLY has3sheets: BOM key, isometric47balloons and side21balloons.68unique labels/attached native component paths verified; all87BOM item numbers and405quantities preserved.19unlabelled items listed in CP-RB-003_BALLOON_COVERAGE.csv. PDF rendered/text-bounds checked and balloon sheets visually inspected.33drawing/PDF pairs now indexed. No source model files or originalBOM drawing changed.

SolidWorks marked the live assembly dirty during native balloon association. Unsaved live source was preserved separately; the working source file was not overwritten and the live assembly remains open. See ASSEMBLY_BALLOON_DRAWING_STATE.json for source hashes/recovery path. Do not discard this live state or claim a new motion/geometry check from this documentation task. See ASSEMBLY_BALLOON_TASK_CHECKPOINT.json for the new addendum.

## Latest completed task: native assembly BOM

CP-RB-002_ASSEMBLY_BOM.SLDDRW, PDF and CSV are under Drawings_Prototype. The native parts-only BOM has87entries and405leaf instances; every quantity matches the prior inventory. There are now32 active drawing/PDF pairs. PDF full-sheet/table detail visually checked; no clipped text. The drawing window is closed and the working assembly is open and clean. See ASSEMBLY_BOM_DRAWING_STATE.json and ASSEMBLY_BOM_TASK_CHECKPOINT.json.

The current clean assembly already had a different hash from the earlier implementation checkpoint at this task's start. It remained unchanged during this task;97other native model files match the earlier checkpoint. Do not infer a geometry change or restore older assembly bytes from that hash difference. Earlier motion/mate evidence remains tied to its recorded snapshot and was not repeated in this BOM-only task.

Remaining hidden-item detail callouts, material/procurement approval and manufacturing release remain separate work. Earlier sections below describe historical checkpoint states.

Saved 2026-10-23T01:45:15.102403+00:00. This supersedes the historical PAUSED_RESUME_NOTES.md/PAUSE_CHECKPOINT.json as the current entry point. The user resumed the task and then prioritized a fast saved pass. This is a saved checkpoint, not an overall completion or operating release.

Read MECHANICAL_COMPLETION_REPORT.md and CURRENT_IMPLEMENTATION_CHECKPOINT.json first. Working assembly: RevB_Isolated/RB_Assem20_Design_RevB.SLDASM. The saved native tree has98 model files and31 active drawing/PDF pairs. Recovery archive: Checkpoints\20261023T014513Z\SAVED_NATIVE_AND_DRAWINGS.zip. Restore files to their original task-relative locations; the archive is a recovery snapshot, not a separately validated cross-machine Pack and Go. Install the retained material database in a configured material folder on another machine and verify references/densities.

New interfaces are installed and saved: eight bearing cartridges; symmetric0.65mm hub shims and longer bolts; eight capped sockets; four arm crosspins; four longer arm-sideM2x12 screws. Follow ARM_SCREW_LENGTH_CORRECTION.json for the new screw names; REV_B_STATE.json contains historical old screw names. Native saved-pose checks passed202/98/8/36 comparisons respectively. Current travel constraints are restored and both angle holds suppressed; the active-mate scan found no errors.

Materials/density corrections and their backups are complete for the listed primary/secondary parts. Remaining14g servo override is explicitly manufacturer-nominal reference mass. The mixed native mass sum is1109.958g, not hardware mass. Servo selection fails the provisional X-axis torque screen.

Drawings are PROTOTYPE / NOT RELEASED FOR FABRICATION, with dimensional/interface notes, source hashes, DO NOT SCALE labels and release holds.31 active PDFs passed text/source checks and were rendered; contact-sheet layouts and representative full-size pages inspected. Two inactive candidates archived under Drawings_Prototype/Superseded_Candidates. Legacy manufacturing completeness, GD&T and assembly BOM/balloons remain open.

Next work: close named actuator/load/composite/supplier dependencies; finish remaining manufacturability and final moving-clearance/backlash checks. Do not claim fatigue, physical retention, actual supplied fit, measured mass or2640RPM capability. No baseline inputs/original sources were changed.

Do not rerun completed integration/material scripts. Debug draft inspect_material_database.py is disabled. Native operations must remain serial. Keep unused windows closed and preserve dirty task data before closing.
