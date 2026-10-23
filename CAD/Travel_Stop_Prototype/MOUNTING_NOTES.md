# Travel-stop mounting prototype - 21 October 2026

Status: nominal CAD attachments defined; not released for fabrication. See `STOP_VALIDATION.json` for the current sampled-motion results. These notes do not establish joint strength.

## Arrangement

Two M2.5 through-bolts attach each stop pad to its mating plate. No tapped thread is assumed in either plate. Both plates are 3 mm thick in the inspected native CAD. The fixed bracket is 3 mm thick; the moving arm is 2 mm thick.

The hole centres are `(24,21)` and `(27,27)` mm from each corresponding plate centre, expressed in the main assembly XY directions. The pad and mating plate have matching diameter 2.9 mm holes. The carriage part uses a different native coordinate system: its hole axes pass through local `(X,Z)=(-24,21)` and `(-27,27)` mm, along local Y.

| Attachment | Quantity | Screw | Head position | Washer and nut position |
| --- | ---: | --- | --- | --- |
| Fixed bracket to fixed base | 2 | M2.5 x 0.45 x 10 countersunk | Beneath fixed bracket, recessed nominally 0.1 mm | Above fixed base |
| Moving arm to carriage | 2 | M2.5 x 0.45 x 8 countersunk | Above carriage, recessed nominally 0.1 mm | Beneath moving arm |

Four plain washers use ID2.7, OD6 and thickness0.5 mm. Four plain hex nuts use M2.5x0.45, 5 mm across flats and 2 mm height. Threads and drive recesses are not modelled. Nut exteriors are full hexagonal envelopes without chamfers. Plain nuts are not self-locking; an anti-loosening method has not been selected or verified.

The countersinks are diameter 5.2 mm at the outer face, 90 degrees included angle, and 1.15 mm deep down to the diameter 2.9 through-hole. They are in the fixed bracket underside and the carriage top face only. The moving arm has plain through-holes, so it retains its full 2 mm thickness away from those holes.

The selected reference screw has a diameter 5 mm head. Its 90-degree head cone meets the nominal thread-diameter envelope 1.25 mm below its outer face; the published overall head-height envelope is 1.55 mm. The lower neck is within the modelled shank envelope. Screw length includes the countersunk head. Do not substitute a different head diameter without revising the countersink and repeating checks.

## Nominal stack and clearances

Coordinates below are Z heights from the stationary-base underside in the main assembly, not coordinates in each individual part.

| Feature | Fixed attachment | Moving attachment |
| --- | --- | --- |
| Screw outer head face | -2.9 mm | 20.9 mm |
| Screw tip | 7.1 mm | 12.9 mm |
| Washer | 3.0 to 3.5 mm | 15.5 to 16.0 mm |
| Nut | 3.5 to 5.5 mm | 13.5 to 15.5 mm |
| Nominal thread protrusion past nut | 1.6 mm | 0.6 mm |
| Nominal clearance from screw tip to intermediate plate | 1.9 mm | 0.9 mm |

The intermediate plate occupies Z9 to Z12. Its relative XY motion does not change those axial gaps. The moving screw heads are below the carriage top at Z21, leaving nominal clearance beneath the control ring at Z22. These are rigid, nominal dimensions, not a worst-case tolerance or deflection result. Effective full thread engagement still depends on real screw end chamfers and nut lead-ins.

The original proposed first hole at (21,21) would have overlapped an existing carriage-hole countersink envelope. The final (24,21) location leaves the existing diameter 2 mm hole at (20,24) separate. The second hole at (27,27) leaves a nominal 0.4 mm land between its countersink edge and the plate edge. OD6 washers reach the pad boundary at that second hole. Edge distances, bearing area, countersink weakening and pad stiffness require a joint-load and tolerance check.

## Assembly sequence and access

Install the moving-arm screws from the carriage top before fitting the control ring. Fit washers and plain nuts beneath the arm. The fixed-bracket screws enter from beneath its pad; their washers and nuts fit above the base. Verify tightening access with the actual driver and spanner and confirm the mechanism can be disassembled. No tool envelope or physical assembly trial has been performed.

The original 15 stop datum mates are retained. Twelve fastener components use 36 additional datum-plane mates to locate their nominal envelopes. This is a CAD positioning scheme, not a simulation of bolt preload, thread contact, friction or loosening.

An extra loose `XY_Stop_Fixed_Bracket_PROTOTYPE-2` was already present when this mounting step began. It was left untouched; it is not part of the intended stop attachment. Its presence must be resolved before a production BOM or mass release. The intended fixed bracket is instance `-1`.

## Evidence and sources

The native-cut checks compare removed volumes against two diameter 2.9 through-holes and, where applicable, two 90-degree countersinks. Both plate thicknesses and all changed cut features were checked in native SolidWorks. The source hashes in `STOP_VALIDATION.json` identify the saved CAD used for the motion/intersection checks. The completed mounting run passed all 25 sampled positions, 16 overtravel probes and the excessive diagonal-corner check, with zero new stop/hardware intersections and zero errors across 113 active mates. `MOUNTING_VALIDATION.json` separately records passing native hole alignment, changed-feature rebuild, nominal thread protrusion and screw-tip clearances. The original assembly offset was restored.

- [Schaefer + Peters M2.5 x 8 countersunk screw](https://shop.schaefer-peters.com/sp/en/iso-10642-a2-m-2-5x8-p194367/): selected reference head diameter 5 mm, overall head height 1.55 mm. The 10 mm version uses the same provisional head envelope; confirm the exact supplier drawing before procurement.
- [Schaefer + Peters DIN125A 2.7 washer](https://shop.schaefer-peters.com/sp/en/din-125-a2-2-7-p62164/), [manufacturer catalogue](https://shop.schaefer-peters.com/userdata/filegallery/original/db5d02f7-3c1e-4e16-987b-c7be809d106f.pdf): 2.7 x 6 x 0.5 mm envelope.
- [JC Fasteners DIN934 dimension table](https://www.jcfasteners.com/wp-content/uploads/Din-934-Hex-Nut-A2C31-MS-ZN.pdf): M2.5x0.45, across flats max5, height max2 mm. The catalogue does not establish an approved material or strength grade for this assembly.

## Remaining release work

Select plate/bracket and screw materials and grades; calculate the actual stop and joint loads; verify bolt preload, slip, bearing, pull-through, fatigue and edge distances; select an anti-loosening method; define manufacturing tolerances and tool access; integrate with the complete frame and rotor. No baseline inputs or module-mass estimates were changed.

The shared source `CAD/4-Inner_Carriage_Plate.SLDPRT` now includes these two holes and countersinks. Other assemblies referencing that file will see the change when rebuilt. The fixed base, both stop pad parts and `Assem20.SLDASM` were also saved. Pre-change copies are recorded in the temporary mounting-state JSON; no commit or publication was made.


Subsequent servo mounting step: the assembly has since gained servo mounting hardware. The stop validation above records its earlier saved revision by hash. See [current assembly validation](../Servo_Mounting_Prototype/ASSEMBLY_VALIDATION.json) and [servo mounting notes](../Servo_Mounting_Prototype/MOUNTING_NOTES.md) for the later assembly, which also rechecks the stop geometry.

Subsequent connections1-4 revision: the assembly and shared mounting parts have changed further. See [latest connection notes](../Connections_Completion/CONNECTIONS_NOTES.md) and [saved validation evidence](../Connections_Completion/CONNECTIONS_VALIDATION.json). Earlier motion checks remain evidence for their recorded source hashes only.
