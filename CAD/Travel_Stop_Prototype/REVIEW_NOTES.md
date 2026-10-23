# Combined XY travel-stop prototype — 21 October 2026

Status: **provisional CAD design; nominal mounting geometry is defined, but joint strength, tolerances and load capacity are not released for fabrication**.

This design is inserted into `../Assem20.SLDASM`. It adds physical contact geometry for the combined XY travel limit. It does not change the 6.88 mm calculation input, the shaft, the existing plates, or the servo/horn assumptions.

## How it works

A fixed circular stop surrounds a follower attached to the nonrotating bearing carriage. Its nominal radial allowance is:

`(19.76 mm bore − 6.00 mm follower) / 2 = 6.88 mm`.

This limits the combined offset, rather than allowing both axes to reach 6.88 mm simultaneously. The follower is separate from the drive shaft. Both stop axes are at `(50, 50) mm` relative to their respective plate centres at neutral, in the assembly's XY plane.

The fixed bracket is beneath the fixed base. The moving arm is beneath the bearing-carriage plate. Their attachment pads now have matching holes and two M2.5 through-bolts each, with washers and plain nuts. See [mounting notes](MOUNTING_NOTES.md) for screw lengths, hole coordinates, stack clearances, source references and remaining joint checks. Datum mates position the nominal geometry; bolt preload, slip and impact-load rating remain unverified.

## Parts and dimensions

| Part | Defined nominal geometry | Status |
| --- | --- | --- |
| `XY_Stop_Fixed_Bracket_PROTOTYPE.SLDPRT` | Bore Ø19.76; ring OD32; thickness 3; 8 mm wide diagonal bridge; base pad from XY `(18,18)` to `(30,30)` mm | CAD geometry and mounting holes defined; joint and material release pending |
| `XY_Stop_Moving_Arm_PROTOTYPE.SLDPRT` | Thickness 2; 8 mm bridge; Ø12 follower seat with Ø4.5 clearance hole; carriage pad from XY `(16,18)` to `(30,30)` mm | CAD geometry and mounting holes defined; joint and stiffness release pending |
| `XY_Stop_Follower_D6_M4_PROTOTYPE.SLDPRT` | Smooth Ø6 × 24 below the shoulder; upper M4×0.7 thread ×10; shoulder seats below the moving arm | Custom part proposal; steel grade, hardness, tolerances and edge details pending |
| `M4_Washer_4p3x9x0p8_REFERENCE.SLDPRT` | ID4.3, OD9, thickness 0.8 | Published hardware dimensions; reference geometry |
| `M4_Locknut_AF7_H5_REFERENCE.SLDPRT` | M4×0.7; 7 across flats; height 5 | Published hardware envelope; full hex exterior is conservative |

The follower shoulder and locknut capture the moving arm, with a washer beneath the nut. The smooth follower passes through the fixed ring. Its nominal axial engagement with the ring is 3 mm. The thread and nut bore are represented by nominal diameter envelopes, not actual helical thread flanks. Thread fit, tightening torque and locking performance were not tested.

The local Z=0 plane of the fixed bracket contacts the fixed-base underside. The moving arm's local Z=0 is 2 mm below the bearing-carriage underside. The follower's local Z=0 is its shoulder, against the moving-arm underside. These local frames differ; their assembly mates establish the intended stack.

## Manufacturer references

- Washer dimensions: [WDS 876-M4-303, 4.3 × 9 × 0.8 mm](https://www.wdscomponents.com/en-us/4-3-x-9-x-0-8-303-stainless-steel-form-a-washer-1pcs).
- Nut envelope: [Verpas DIN985 M4, product 0000400](https://www.verpas.com/fasteners/nuts/hexagon-lock-nut-steel-zinc-plated-din-985/).
- Coarse-thread and envelope reference: [FATOR DIN985 / ISO10511 table](https://fatorgroup.com/en/pages/hexagon-lock-nut-din-985-iso-10511).

These references support nominal hardware selection without having physical parts. They are not evidence of procurement, delivered-part inspection or load suitability.

## Verification

See `STOP_VALIDATION.json` for the final native SolidWorks results and source-file hashes. A pass must be supported by that file, not inferred from these notes.

The final run with mounting hardware passed all 25 sampled positions with zero active mate errors and zero new stop/hardware intersections. There were 63 native Boolean intersection checks after bounding-box screening and reuse of unchanged relative placements. All 16 overtravel probes and the simultaneous-axis corner produced the expected blocking overlap. All 113 active mates rebuilt without error after restoring the prior assembly position and travel limits. See `MOUNTING_VALIDATION.json` for the separately verified native hole alignment, changed-feature rebuild, nominal thread protrusion and screw-tip gaps.

Checks cover the centre, eight intermediate-radius positions, and sixteen positions on the nominal 6.88 mm boundary. They include native mate errors, commanded versus actual carriage displacement, and copied-body Boolean intersections involving the new stop parts and the available assembly geometry.

Overtravel is tested using copied follower geometry, without forcing the constrained assembly into an invalid pose: sixteen directions at radius 6.98 mm, plus the simultaneous `(6.88, 6.88) mm` corner. Positive overlap with the fixed stop is the expected result for those deliberately excessive positions. It demonstrates nominal rigid-body blocking geometry, not impact strength.

Existing-existing component pairs, including known guide end-region contacts and internal imported-servo overlaps, are outside these new-stop checks. Zero-volume face contact is allowed. Fastener threads use envelopes. Components are rigid; the control ring is held at its saved angular position. There is no claim of full continuous rotor motion, deformation, wear life or structural certification.

## Work required before fabrication release

1. Verify the newly defined pad attachments against actual joint loads: select approved fastener grades and an anti-loosening method, confirm effective thread engagement, head seating, edge distances, assembly order and actual tool access. Nominal attachment geometry is described in `MOUNTING_NOTES.md`.
2. Select materials and manufacturing tolerances. The 6.88 mm stop radius is nominal: actual travel depends on bore size, follower size, alignment, clearances and deflection. Release a tolerance stack and acceptable operating margin.
3. Check follower bending, thread/shoulder strength, arm and bracket stiffness, pad attachments and contact stresses under the actual stop loads. Decide whether a replaceable wear surface or compliant bumper is required.
4. Confirm the contact diameter, threaded transition, edge reliefs, surface finish and hardness of the custom follower. Release a production drawing and a real hardware specification.
5. Integrate the stop with the complete frame, rotor/endplate stack, bearings and cables. The available mechanism subassembly does not establish clearance in the complete module.
6. Assign approved CAD materials and reconcile added mass. No measured mass or updated module-mass baseline is claimed here.

The assembly's pre-existing position is recorded in the validation report and restored after the checks. No baseline inputs, project-state records, commits or publications are changed by this design step.


Subsequent servo mounting step: the assembly has since gained servo mounting hardware. The stop validation above records its earlier saved revision by hash. See [current assembly validation](../Servo_Mounting_Prototype/ASSEMBLY_VALIDATION.json) and [servo mounting notes](../Servo_Mounting_Prototype/MOUNTING_NOTES.md) for the later assembly, which also rechecks the stop geometry.
