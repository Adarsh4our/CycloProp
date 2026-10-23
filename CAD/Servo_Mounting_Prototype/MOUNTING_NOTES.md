# Servo mounting prototype - 21 October 2026

Status: provisional native CAD attachment geometry. Actual servo selection, manufacturing tolerances, materials, bolt preload, anti-loosening and joint loads remain unverified. No fabrication release or module-mass update is implied.

## Implemented connections

Each servo mount now connects to its supporting plate with two M2.5x0.45x8 countersunk through-bolts, washers and plain nuts. The X mount attaches to the fixed base; the Y mount attaches to the intermediate X slider. Servo and linkage axes retain their existing positions.

Mount-local pad holes are centred at `(-25,18)` and `(-25,25)` mm. Each mount's 2 mm foot has diameter 2.9 through-holes and diameter 5.2, 90-degree countersinks on its underside. The mating 3 mm plates have plain diameter 2.9 through-holes. The Y mount is rotated 90 degrees, giving intermediate-plate hole centres `(-18,-25)` and `(-25,-25)` mm in that plate's native XY coordinates.

The existing M2.5 reference hardware in `../Travel_Stop_Prototype/` is reused. Its diameter 5 countersunk heads sit nominally 0.1 mm inside the foot underside. Washers are ID2.7, OD6, thickness0.5; plain nuts are AF5, height2. Nominal protrusion beyond each nut is 0.6 mm. The foot, plate, washer and nut total 7.5 mm; the screw's head is recessed 0.1 mm. Effective full-thread engagement depends on the actual screw end and nut lead-ins.

The Y mount is above the lower guide. Countersinking from the foot underside keeps its screw heads out of that narrow gap. The imported guide's nominal top is 0.397 mm beneath the foot; this small existing gap still needs a tolerance and deflection allowance. Fasteners and moving drive tabs are included in the sampled geometry checks.

## Servo-ear supports and clamps

The imported servo has mounting-ear underside and top planes at native Z17 and Z19.5 mm. Its imported hole-face bounds give nominal diameter 2.5 and centres `(123.5,-66.6)` and `(123.5,-38.4)` mm. Those axes map to mount-local XY `(-60,4.55)` and `(-60,32.75)` mm. This is evidence from the current older CAD envelope, not proof that a procured SH-0257MG+ has identical ears.

The ears were 2.2 mm above the mount shelves. Two integral OD5, height2.2 bosses per mount now bridge that gap without moving the servos. Diameter 2.4 holes pass through each boss and the 3 mm shelf. Bosses partly overhang the existing case cutout; their roots and the small clearance to the case require a stiffness and tolerance check. Each mount remains one merged solid body.

Each ear uses an M2x0.4x12 socket-head through-screw, a washer above the ear, a washer below the shelf, and a plain nut below that washer. The ear is 2.5 mm thick in the current CAD. Washer envelopes are ID2.2, OD5, thickness0.3. Nuts are AF4, height1.6. Socket-head envelopes are OD3.8, height2; screw length is measured below the head. Nominal protrusion beyond each nut is 2.1 mm. No rubber grommet, ferrule or vibration-isolation claim is made.

Threads and drive recesses are not modelled. A solid head and full hex nut exterior provide conservative exterior envelopes. These parts are references, not supplier-certified models. Plain nuts are not self-locking; an anti-loosening method and tightening instructions remain to be selected.

| Hardware added in this step | Quantity |
| --- | ---: |
| M2.5x8 countersunk screw | 4 |
| M2.5 washer 2.7x6x0.5 | 4 |
| M2.5 nut AF5 H2 | 4 |
| M2x12 socket-head screw | 4 |
| M2 washer 2.2x5x0.3 | 8 |
| M2 nut AF4 H1.6 | 4 |

## Evidence and limits

The completed native run passed all 25 sampled positions with no new actuator, mounting-hardware or stop intersections and zero errors across 197 active mates. It used 482 native Boolean checks after bounding-box screening and reuse of unchanged relative placements. All 16 copied-body overtravel probes and the excessive diagonal corner produced the expected stop overlap. Separate native interface checks passed for pad-hole alignment, boss-to-ear alignment, feature rebuild, head recess and nominal thread protrusion. The prior XY offset of approximately (4.05560145, 0) mm was restored.

`ASSEMBLY_VALIDATION.json` records the native sampled positions, mate errors, intersections and saved source hashes. It includes the previous servo actuator parts and stop hardware as well as the newly inserted servo mounting hardware. `INTERFACE_VALIDATION.json`, when present, records the separate native hole, boss, ear alignment and screw-stack checks. Do not infer a pass from this notes file alone.

Checks use rigid nominal bodies, the saved control-ring angle and sampled XY offsets. Existing-existing guide contacts are excluded; imported-servo internal body overlaps are excluded within a component. Copied-body overtravel probes test nominal stop blocking. These checks do not establish continuous-motion clearance, load capacity, actual delivered-part fit or complete rotor/frame clearance.

Install and tighten the mount-pad connections before the upper stages obstruct access. Seat the servo ears on the support bosses, add the top washers and screws, then add lower washers and nuts. Confirm actual driver and spanner access and assembly order with the selected hardware. No tool-envelope sweep or physical assembly trial has been performed.

Changed shared source files are `Servo_Actuation_Prototype/Servo_X_Mount_PROTOTYPE.SLDPRT`, `Servo_Y_Mount_PROTOTYPE.SLDPRT`, `CAD/XY_Fixed_Base.SLDPRT`, `CAD/Intermediate_X_Slider.SLDPRT`, and `CAD/Assem20.SLDASM`. The original servo source and the reference servo bodies were not modified. Existing files have pre-change copies identified in the temporary servo mounting state and validation data. The user's pre-existing XY position is restored after the checks. No calculation baseline, project-state record, commit or publication is changed.

Earlier servo and stop validation reports identify earlier assembly revisions by their hashes. Use this step's assembly validation for the current saved assembly. The previously present loose stop-bracket instance `-2` remains untouched and must be resolved before a production BOM or mass release.

## Manufacturer references

- [Schaefer + Peters ISO4762 M2x12](https://shop.schaefer-peters.com/sp/ro/iso-4762-a2-m-2x12-p512735/): diameter 3.8, height2 head envelope.
- [Schaefer + Peters DIN125 M2 washer](https://shop.schaefer-peters.com/sp/en/din-125-a2-2-2-p62162/): 2.2x5x0.3 mm.
- [Schaefer + Peters DIN934 M2 nut](https://shop.schaefer-peters.com/sp/ro/din-934-a4-m-2-p500712/): AF4 and height1.6 envelope. Catalogue material is not an approved assembly material specification.
- [M2.5 reference hardware sources and limits](../Travel_Stop_Prototype/MOUNTING_NOTES.md).
- [Current Savox SH-0257MG+ manufacturer specification](https://www.teamsavox.com/product/sh-0257mgp/): current product-family identity only; equivalence to the older project's CAD ear dimensions is unverified.

Next incomplete interfaces are the two moving drive-tab attachments, pivot retention and the real compatible horn/spline connection. The conceptual R12 horn does not transmit torque through its clearance bore. Materials, tolerances, loads, fastener locking, frame/rotor integration and final CAD mass remain outstanding.


Subsequent X drive-tab step: its two fastener sets have been inserted. See [X tab mounting notes](../Drive_Tab_Mounting_Prototype/X_TAB_MOUNTING_NOTES.md). That later revision has a single-position check only; the earlier 25-position report remains evidence for its earlier source hashes. The Y drive-tab attachment is still unfinished.

Subsequent connections1-4 revision: Y-tab mounting, pivot retention, the custom horn interface and guide/bearing/hub/frame connections have since been implemented provisionally. The earlier unfinished-interface statements describe the earlier revision. See [current connection notes](../Connections_Completion/CONNECTIONS_NOTES.md) and [current saved evidence](../Connections_Completion/CONNECTIONS_VALIDATION.json); the spline production fit remains unverified because supplier sources conflict.
