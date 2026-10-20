# Servo actuation prototype — 20 October 2026

Status: **provisional mechanical layout; not released for fabrication**.

The prototype is assembled in `../Assem20.SLDASM`. It adds two servo drives to the existing orthogonal MGN5 stages. The original servo part, shaft, plates, calculation baseline and project-state documents were not edited for this actuation layout.

## Arrangement and dimensions

- The lower-stage servo case mounts to the fixed base and drives the intermediate plate.
- The upper-stage servo case mounts to the intermediate plate and drives the bearing carriage. This preserves independent control of the two axes.
- Each conceptual servo arm has a 12 mm effective radius. Each link has 40 mm between pivot centres and is 2 mm thick, with nominal 2.1 mm pivot holes.
- The horn is a **clearance envelope**, not a working manufactured horn: its 5.2 mm centre opening does not transmit torque through a spline. A measured, compatible commercial horn or a properly designed adapter must replace this interface.
- Two new mounts support the existing Savox CAD envelope; two new drive tabs reach below the plates. Their mounting holes are deferred, as requested, until the attachment hardware is established.
- The actuator and link planes were placed an additional 3 mm behind the base to clear the lower pivot at maximum X travel. The reference pins have 7.5 mm shanks and reserve approximately 2.5 mm beyond the mating plate for retention. Actual nut/clip geometry remains unverified.
- The drive-tab feet are 2 mm thick. The nominal clearance above the imported rail profile is approximately 0.397 mm where a foot passes over a rail. This small gap needs a tolerance and deflection check.
- The combined eccentricity remains nominally limited to 6.88 mm. The CAD limit uses the distance between fixed-base and carriage origins at the existing 18 mm axial separation. Its upper bound must be recalculated if that separation changes. The lower distance bound is zero; the stack mates set the axial separation. A 1 nm allowance on the spatial-distance upper bound avoids numerical flags at the nominal boundary; this is not a manufacturing clearance.

## CAD source and hardware identity

`Savox_SH0257MG_INTERFACE_REFERENCE.SLDPRT` is a copy of the existing `Savox_SH-0257MG.SLDPRT`, with an output-axis reference added. The source file remains unchanged. The native output-body vertices establish its local axis at X = 123.5 mm, Y = -47.15 mm, with the output reaching approximately Z = 28.280025 mm.

Savox documents a 21-tooth output interface for this micro-servo family. The supplied horn's usable hole radius, hole diameter, thickness, spline seating depth and retaining screw still need inspection. Do not assume that the newer SH-0257MG+ drawing or hardware is identical to every detail of this older CAD model. Manufacturer references: [SH-0257MG+ specification](https://www.teamsavox.com/product/sh-0257mgp/), [SH11M 21-tooth micro horn set](https://www.savoxusa.com/products/savsh11m-sh11m-micro-servo-horn-set).

The catalogue servo mass is not evidence of measured hardware mass. Existing project claims of 8.5 g per servo require reconciliation with the selected physical servo; the current manufacturer's SH-0257MG+ listing states 14 g. No module-mass baseline was changed here.

## Validation evidence

See `PROTOTYPE_VALIDATION.json` for the current native-CAD checks, sampled offsets, mate errors and any intersections. Do not infer a pass merely because this notes file exists.

The final run passed all 17 sampled positions with no active mate errors, no component-position discrepancies and no new actuation-part intersections. It used 197 native Boolean intersection checks after bounding-box screening and reuse of unchanged relative placements. The saved centred assembly has 62 active mates; the four individual axis limit mates are restored. Small positive native drag movements of approximately 1 mm were also observed on each axis. The assembly was centred again using mate dimensions after those checks.

The ideal crank angles needed for the two displacement extremes are approximately -34.653 degrees and +35.340 degrees relative to neutral. These are servo-arm angles for this proposed 12/40 mm linkage, not verified blade pitch angles or calibrated electrical servo commands.

The checks use rigid nominal bodies and the control ring's saved angular position. They cover the centre and 16 positions on the 6.88 mm travel boundary. Body intersections are checked between new actuation parts and the selected existing plates, guides, retainers, control ring and shaft, and between separate new components. Repeated unchanged relative placements may reuse the same native Boolean result.

Previously identified rail/block end-region intersections and internal imported-servo body overlaps are outside these new-part checks. No ignored-interference flags are added. Sampled positions are not proof of clearance throughout continuous motion or through a complete rotor revolution.

## Outstanding design work

1. Replace the conceptual horn envelope with the measured commercial horn or a verified adapter, including its real retaining screw.
2. Select actual pivot hardware, its thread/shoulder dimensions and retention; the modelled pins are reference envelopes. Confirm the complete head, washer, nut/clip and tool-access envelope.
3. Finalize mount holes, attachment screws, thread engagement, countersinks and assembly access. Datum-plane mates represent rigid attachments in the layout; they do not establish a bolted connection. Earlier attachment lock mates are suppressed.
4. Select materials and tolerances; check bracket/link stiffness, strength, fatigue, backlash, actuator force and servo capability under the actual loads. No such approval is implied by the CAD.
5. Design a physical combined-travel stop. The radial SolidWorks mate does not stop real hardware, and separate axis stops alone allow excessive diagonal travel.
6. Integrate the mechanism into the chassis and rotor assembly, verify the full motion and cable routing, then reconcile native CAD mass with the calculation baseline.

No aerodynamic, CFD or structural-certification result is established by this prototype.
