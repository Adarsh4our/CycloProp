# Recovery scope

`DISK_START.zip` contains the original saved model/drawing/material/evidence
files under project-relative paths. `STARTING_POINT.json` records member
hashes and the separate live-state copies. CRC and all member SHA-256 hashes
were verified by `automation/finalize_requirements_checkpoint.py`.

`Live/` contains separate SaveAs copies of the three task assemblies that were
dirty at capture. They retain references to the working isolated part tree.
They do not replace the saved disk versions in the archive. To reconstruct
the captured unsaved assembly state, restore the archived model tree to the
recorded original paths, then use the three Live copies at their recorded
source paths. Preserve any newer work before a restoration; no restoration
was performed during this task. The assemblies currently open in SolidWorks
retain their original paths and unsaved state.

`prior_balloon_live_recovery.SLDASM` and `saved_working_assembly.SLDASM` are
uniquely named, read-only comparison copies. They are evidence, not the new
working source. `RECOVERY_COMPARISON.json` records the inspected transforms,
constraints and blade feature/mass-geometry data; it does not prove complete
geometry equivalence or continuous motion.

`REQUIREMENTS_WORK.zip` and `REQUIREMENTS_MANIFEST.json` identify the new
requirements/load work and scripts. The broad input bounds remain provisional.
Native operating/moving-clearance checks and physical testing remain open.

This checkpoint is recoverable at its recorded workspace paths. It is not a
validated cross-machine Pack and Go. Twenty-one virtual bearing components
resolve in the captured native session; material database installation and
all references must be rechecked after transfer. No source native model,
drawing, PDF or calculation-baseline input was overwritten by this work.
