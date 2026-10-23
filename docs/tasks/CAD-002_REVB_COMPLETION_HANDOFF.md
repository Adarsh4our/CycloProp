# CAD-002: CycloProp Rev B mechanical-design completion handoff

Prepared 21 October 2026. This is a continuation brief for a fresh mechanical-design/SolidWorks agent. Read it in full before changing CAD. It contains the current evidence, the user's authorization, proposed work, and the limits of each completion claim.

## 1. Your assignment and existing authorization

Continue the CycloProp mechanical-design and SolidWorks CAD work from the saved Rev B state. Do not restart the project, reconstruct an earlier assembly, or repeat completed mutation scripts.

The user originally requested an independent review, then explicitly authorized CAD corrections and implementation. The latest engineering authorization covers all six remaining areas:

1. Full rotor/frame clearance.
2. Physical ring-to-rotor timing.
3. Blade bushings, axial clearance and retention.
4. Socket retention, arm strength and fastener connections.
5. Actual servo/horn interfaces.
6. Materials, fits, tolerances and manufacturing drawings.

The user explicitly selected: **“Preserve the ±35° pitch target; redesign linkage dimensions.”** This decision remains controlling. The shorter linkage described below is the current provisional solution. Other geometric adjustments within the authorized mechanical scope can be developed when evidence requires them; explain and record the reasons.

Work directly within this scope. The user prefers concise, meaningful updates, a few well-designed checks and few confirmation requests. Do not request approval again for previously authorized CAD implementation. Ask for genuinely missing decisions or external information only when they prevent the dependent work; continue independent work meanwhile.

Do not commit, push, publish, change calculation-baseline inputs, or claim physical verification from CAD. Keep the original assembly and historical evidence recoverable. The current handoff request was **plan only**: the preparation of this brief did not authorize its author to continue native mutations. The receiving implementation agent should follow the engineering authorization above.

Your delivery must distinguish:

- Calculated feasibility.
- Implemented native geometry and assembly connections.
- Native rebuild, motion and clearance evidence.
- Material and strength assumptions/calculations.
- Supplier dimensional evidence and remaining fit conflicts.
- Required physical measurements and tests.

Do not claim the six areas are complete merely because CAD rebuilds. Where delivered hardware, approved operating loads or physical testing are missing, finish the work possible from available evidence and identify precisely what remains blocked.

## 2. Environment and authoritative starting point

Project root: `C:\Users\Adarsh Singh\CycloProp`.

- Windows; PowerShell.
- SOLIDWORKS 2026. Native API reported revision `34.3.2` during this continuation.
- Python 3.11 with `pythoncom`, `win32com.client`, and NumPy available.
- Native automation uses the existing interactive SolidWorks session.
- Last observed SolidWorks PID: `8284`. Discover the current process rather than assuming this PID persists. The older PID `21096` is stale.
- At the handoff check, **no Python process was running**. Only SolidWorks was listed among the checked CAD/Python processes.
- The tool environment was changed by the user to unrestricted filesystem/network access with approval policy `never`. Check the receiving agent's actual permissions. In that profile, do not send a `sandbox_permissions` argument. Earlier sandboxed COM access stalled; an outside-sandbox read-only inventory succeeded before the profile change.

Current working assembly:

`CAD/Design_Completion/Assem20_Design_RevB.SLDASM`

Preserved original assembly:

`CAD/Assem20.SLDASM`

Rev B is a separate assembly, **not necessarily an isolated copy of its referenced part/subassembly tree**. Many references are shared with the original. Copy and redirect affected references before editing a shared source when the original must retain its geometry. Saving a different assembly filename alone does not isolate referenced parts.

At the latest read-only native capture:

- Rev B was open and had `GetSaveFlag=False` at the start of capture.
- There were 276 root components.
- Active mate-error inspection returned an empty list in the native process output.
- `RESUME_NATIVE_STATE.json` records the inspected transforms, source paths, selected body bounds, cylindrical surfaces, mate names and selected mass-override flags. It does **not** itself contain the complete all-mate error scan; do not misattribute that result to a nonexistent JSON field.
- No new frame or timing-coupling CAD parts were created during this continuation.

Do not assume the user has left the assembly unchanged since this capture. Read the current active document/dirty state and relevant transforms before mutation. Preserve unsaved user work.

## 3. Interrupted command: exact status

The prior agent drafted:

`CAD/Design_Completion/revb_completion.py`

It contains separate `frame-parts` and `coupling-parts` generation phases. It was written to disk. The attempted `frame-parts` invocation was interrupted at the execution/approval boundary.

The subsequent handoff check found:

- No running Python process.
- No `COMPLETION_PROGRESS.json`.
- No generated `RevB_Cage_*`, `RevB_Lower_Bearing_*`, or `RevB_Oldham_*` native files in `CAD/Design_Completion`.
- Only the pre-existing Rev B assembly/tube/evidence, the new read-only inventory, and the drafted Python file were present there.

Therefore treat this file as **unexecuted draft automation, not implemented CAD**. Read and revise it before use. In particular:

- It generates candidate parts only. It does not integrate a new frame or coupling into Rev B.
- It does not implement the coupling's ring attachment, shaft fastening, retaining hardware, physical sliding mates, materials or manufacturing drawings.
- Its dimensional/clearance proposals are not a selected, validated mechanical solution.
- Its floating-disk cuts assume a face-sketch orientation; confirm `ModelToSketchTransform` rather than assuming which sketch axis corresponds to model X/Y.
- Its `make_part` existence check skips an existing file without proving that file is complete/correct. Add explicit per-part validation and recovery handling before relying on restart behavior.
- It depends on temporary helper scripts listed later. Preserve/copy those dependencies and their hashes if you make the automation durable.
- It calls the existing helpers, which create provisional custom properties. They do not establish a material assignment or release status.

Do not run the draft simply because it exists. Resolve its design dependencies and review its effects first.

## 4. Files to read and transfer

The receiving agent needs the **current local files**, including uncommitted changes and external/virtual references. A remote repository checkout or this brief alone is insufficient for native CAD implementation.

Read first:

| File | Purpose and limits |
| --- | --- |
| `CAD/Design_Completion/REV_B_STATE.json` | Assembly/tube paths, original backup, four component mappings, original XY/rotor/ring transforms, completed layout steps. Some transforms are historical construction inputs; use the newer inventory/live state for current transforms. |
| `CAD/Design_Completion/RESUME_NATIVE_STATE.json` | Latest read-only native capture from this continuation; selected geometry, current transforms, confirmed override flags. |
| `CAD/Design_Completion/REV_B_INTERFACE_INVENTORY.json` | Frame/shaft/base/endplate/hub/rail mate names, surfaces, frame feature list and earlier empty mate-error result. |
| `CAD/Design_Completion/SELECTED_LINKAGE.json` | Provisional short-link parameters and nominal planar calculation. |
| `CAD/Design_Completion/KINEMATIC_FEASIBILITY.json` | Why the earlier 95 mm linkage does not satisfy the complete requirement with constant 1:1 timing. |
| `CAD/Design_Completion/NATIVE_BOM_AND_MASS.json` and `.csv` | Original-assembly native mass inventory before the Rev B tube changes; not the current Rev B BOM or a trustworthy total mass. |
| `CAD/Rotor_Integration/Ball_Link_Prototype/ASSEMBLY_CLEANUP.json` | Completed removal of obsolete suppressed instances/mates from the original assembly. |
| `CAD/Rotor_Integration/Ball_Link_Prototype/FOUR_LINKS_NOTES.md` and related validation JSON | Earlier 95 mm linkage and limited checks; historical scope only. |
| `CAD/Connections_Completion/CONNECTIONS_NOTES.md` and `CONNECTIONS_VALIDATION.json` | Existing fastener, guide, bearing, hub, shaft and servo-interface implementations and limitations. |
| `CAD/Connections_Completion/Manufacturer_References/` | Official Savox STEP/archive, source/hash record and inspected faces. |
| `CAD/Servo_Mounting_Prototype/MOUNTING_NOTES.md` and its validation files | Earlier servo mount geometry and sampled travel checks; superseded source hashes may limit applicability. |
| `CAD/Travel_Stop_Prototype/REVIEW_NOTES.md`, `MOUNTING_NOTES.md` | Radial travel stop and mounting details. |
| `CAD/Drive_Tab_Mounting_Prototype/X_TAB_MOUNTING_NOTES.md` | Drive-tab interface history. |
| `CAD/CycloProp_Rev3_Master_CAD_Specification.md` | Intended design references; identify conflicts with native CAD. |
| `config/baseline.json`, `reports/baseline.json`, `reports/BASELINE.md` | Calculation inputs/results; read-only for this assignment. |
| `docs/PROJECT_STATE.md`, `docs/VALIDATION.md`, `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md` | Project history and unresolved validation; these can lag the latest native work. |

Also supply the complete native reference tree needed by Rev B. The earlier mass export includes virtual/imported 6806 bearing internals with paths under `%TEMP%\swx8284\IC~~`; investigate whether these are embedded/resolvable before moving work to another machine. Do not assume copying the top-level `.SLDASM` is sufficient.

Recovery locations:

- `%TEMP%\CycloProp_remaining_design_state.json`
- `C:\Users\ADARSH~1\AppData\Local\Temp\CycloProp_remaining_design_sac8k5sf`
- Earlier backups named in the connection/link/cleanup evidence.

At handoff preparation these SHA-256 values were read from disk:

| File | SHA-256 |
| --- | --- |
| `CAD/Design_Completion/Assem20_Design_RevB.SLDASM` | `e3b7bbb6d36c85acbd159518407d4cec37990fa721e33c5fe8f1c3d70d7222dd` |
| `CAD/Design_Completion/REV_B_STATE.json` | `8eccabd7e0230496799d57032a2a768ca98594373c145adf6d11a3d1ecf07074` |
| `CAD/Design_Completion/SELECTED_LINKAGE.json` | `ca7bf5f3b9c2f5f982efc05fa5e2f18d06fb36a48c4109fa52d42c85a6941d68` |
| `CAD/Design_Completion/revb_completion.py` | `2fb41f39b56d280b484b549f2b2c0a4d675544b52562ef69d6f604e76b85b871` |
| `config/baseline.json` | `2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f` |

These identify this handoff snapshot, not a requirement to overwrite later user edits with older files.

## 5. Implemented design facts and unresolved baseline conflicts

### Blades, rotor, endplates and shaft

- The intended current blades are four instances of `Part1.SLDPRT`, identified by the user as NACA 0012.
- `1-Blade_NACA0015.SLDPRT` is genuinely the older NACA 0015 blade; do not substitute it.
- Native Part1 bounds are approximately X `-0.000002..37.988863` mm, Y `-2.298672..2.298672` mm, Z `-12..232` mm.
- Part1 has native D3 cylindrical journals centred at local X9.5, Y0. The aerodynamic body spans 220 mm; journals protrude 12 mm each.
- Part1 is a single solid of approximately `4840.791484 mm3`, with no composite manufacturing definition established. Its shape/material/mass cannot establish a real CFRP skin/foam/spar construction.
- Rotor pitch radius is 95 mm, nominal chord is 38 mm, four blades, quarter-chord pivot 9.5 mm from the leading edge.
- G10 endplates and separate aluminum hubs have been implemented by the user. Material intent is not proof of native assignment or supplied material.
- Revised endplate native OD is 206 mm, thickness 1.5 mm, four blade holes D6 at R95, four hub bolt holes D2.8 on PCD22.
- The separate revised endplate corrected the inspected D15 central bore to D14. Original source part retained.
- Revised hub flange OD28 ×3, pilot D13.9 ×1.5, bore D6, collar OD14 ×11. Hub/endplate connection uses M2.5 through-bolts and nuts; shaft drive uses D2 crosspins.
- Current shaft is D6 ×275 mm, assigned `AISI 4340 Steel, normalized`.
- The calculation baseline instead uses D6 ×260 mm, while the specification calls for 4130. Preserve and report both conflicts. Do not silently change the calculation inputs or claim the CAD equals the specified material.
- Four shaft grooves were corrected to D5.7 roots, retaining 0.8 mm widths for nominal DSH6/DIN471 retention. Shaft crossholes and grooves require strength/fatigue checks.

### XY carriage and bearing

- Two 40 mm miniature rails and guide blocks form the XY carriage.
- The annular bearing is a 6806, ID30 ×OD42 ×7 mm axial width.
- Assem3 is flexible so the outer ring can rotate relative to the carriage.
- Existing guide, servo, stop and retainer hardware has detailed connection notes. Some screw heads and lengths are custom references, not procured components.
- Fixed-base, intermediate-slider and inner-carriage central bores were all inspected as D20.5.
- Inner-carriage bearing seat OD30, local height10; its retainer threads are near R12.5. Enlargement of the central bore can reduce already limited thread/web material. Do not enlarge only for clearance without checking those interfaces.
- Outer-ring local bounds are ±43 mm in its transverse plane and local Y0..8.5. Ring connection holes for the rods are at R40.

### Existing planar linkage before and after Rev B

Earlier assembled linkage:

- Effective pitch arm 12 mm.
- Offset arm axial offset 22.075 mm.
- Ball-centre rod length 95 mm.
- OD2/ID1 carbon tube, cut length85 mm.
- Separate D5 ball inserts and D7 socket housings.
- M2 mounting hardware with compact spacer stacks.

Offset-arm source:

`CAD/Rotor_Integration/Ball_Link_Prototype/Blade_Pitch_Arm_Offset22p075_PROTOTYPE.SLDPRT`

It retains the original D3 journal/D-flat interface, uses twin webs and an offset platform, and has socket-clearance recess OD8/ID3.2/depth0.4 mm. Original construction used approximately 1.7 mm side webs. Do not infer bending, fatigue, clamp capacity or a physical retention method from its appearance.

Ball centres are approximately 34.5 mm above the fixed-base underside. Ball/socket axes are axial; rods lie in a common transverse plane.

Existing socket prototype:

- Sphere D5 ball, flats3 mm apart, D2.1 mounting bore.
- Socket OD7, thickness4.4 mm; spherical cavityD5.05; axial mouthsD4.4.
- Neck approximately4×4 mm extending7.5 mm from ball centre.
- Bond bore D2.1, depth2.7 mm, with nominal tube insertion2.5 mm.
- Nominal radial adhesive gap0.05 mm for OD2 tube.
- These dimensions do not establish ball insertion, pullout retention, adhesive capacity or manufacture.

Earlier checks only covered the saved position and X+0.5 mm carriage movement: 95 mm centre distances, coincident spherical centres, negligible axial offsets, pitch within ±35° at those poses, affected mate checks, and focused saved-pose intersections. They did not prove full rotation, full travel, sinusoidal pitch or physical ring timing.

One early assembly selected the alternate closure branch and produced about105° pitch despite valid mates. It was returned to the intended branch. Guard against this failure during every motion/constraint change.

## 6. Why the short linkage was selected, and what it proves

For R95, ring radius40, horn12, rod95 and eccentricity6.88 mm, a constant1:1 ring timing arrangement centred for zero pitch produced approximately `-44.86°..+33.32°` on one usable branch. Another branch had closure problems. Adding a timing constraint alone cannot fix that arrangement.

The user chose to preserve the ±35° target and permit linkage-dimension redesign.

Current selected provisional parameters:

| Parameter | Value |
| --- | ---: |
| Rotor radius | 95 mm |
| Ring connection radius | 40 mm |
| Horn radius | 12 mm |
| Maximum eccentricity | 6.88 mm |
| Ball-centre rod length | 56.52665325007647 mm |
| Tube cut length | 46.52665325007647 mm |
| Neutral ring-hole phase relative to corresponding blade radial direction | -15.825385589180533° |
| Planar calculation sample spacing | 0.1° over a revolution |
| Sampled pitch extrema | -34.98965311675082° / +34.991094277508445° |
| Maximum sampled closure residual | about2.13e-14 mm |
| Minimum mathematical branch separation | about89.2031763° |

These are rigid planar nominal calculations. **The pitch law is not exactly sinusoidal.** The calculation baseline still assumes sinusoidal35° pitch and has not been changed. Document the resulting analytical-model mismatch for later aerodynamic work.

The calculated extrema leave only about0.009° to a literal35° boundary. Manufacturing variation, joint clearance, backlash and deflection can exceed that nominal margin. Treat the requirement and tolerance budget explicitly; do not call the mechanism robustly within35° merely because a nominal sampled result is34.991°.

Native Rev B implementation completed before this handoff:

- All four shorter tubes installed.
- Old95 mm tube instances and tube/socket datum constraints removed from Rev B.
- New socket datum mate names begin `RevB_LinkN_...`.
- Existing spherical-joint mates retained.
- Saved fitted pitches were about +7.6177°, -32.6899°, -11.0764°, +32.3998°.
- A subsequent native interface inventory and the latest continuation scan found no active mate errors at the inspected state.

New tube file:

`CAD/Design_Completion/Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE.SLDPRT`

Component mapping overview; use the JSON as the complete source of names, including every spacer/screw/washer:

| Link | Blade | Offset arm suffix | Tube suffix | Arm ball / ring ball suffix | Arm socket / ring socket suffix |
| --- | --- | --- | --- | --- | --- |
| 1 | `Part1-2` | `-1` | `-1` | `-3` / `-4` | `-3` / `-4` |
| 2 | `Part1-1` | `-2` | `-2` | `-5` / `-6` | `-6` / `-7` |
| 3 | `Part1-4` | `-3` | `-3` | `-7` / `-8` | `-8` / `-9` |
| 4 | `Part1-3` | `-4` | `-4` | `-9` / `-10` | `-10` / `-11` |

Ball base name: `Ball_Insert_D5_Bore2p1_H3_REFERENCE`.
Socket base name: `Socket_Eye_D7_Sphere5p05_PROTOTYPE`.
Tube base name: `Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE`.

**Current constraints are temporary:** `RevB_SETUP_Rotor_Angle` and `RevB_SETUP_Ring_Angle` remain active. XY setup uses fixed distance values instead of restored advanced travel limits. Restore intended travel and remove/suppress the construction angle holds only after the physical timing mechanism exists and appropriate checks pass.

## 7. Live pose, coordinate conventions and axial stations

The user changed the original assembly pose between earlier reports. Use the latest native state and current live transforms, not older saved-position values.

Latest captured carriage offset relative to the fixed base:

- X = `-0.22370391959580793 mm`.
- Y = `+6.684581416537716 mm`.
- Shaft rotation approximately75.92°.

`REV_B_STATE.json` stores the original captured rotor/ring transforms used during construction. The ring was re-indexed during the short-link fit; those original ring values must not be mistaken for its later/current orientation. `RESUME_NATIVE_STATE.json` stores the later native transform.

All following assembly stations are in mm relative to the fixed-base underside, **not arbitrary global assembly Z**:

| Feature | Station/range |
| --- | --- |
| Fixed-base plate | 0..3 |
| Intermediate-slider origin | 9 |
| Inner-carriage origin | 18 |
| Outer-ring origin/top reference | 30.5; its native local +Y points downward in this assembly |
| Shaft origin | 33.575 |
| Main ball-centre plane | 34.5 |
| Existing lower main-bearing cap origin | 37 |
| Existing lower outer-race spacer origin | 38 |
| Lower main bearing | about41.5..46.5 |
| Existing frame origin | 46 |
| Offset-arm boss origin | 56.575 |
| Mechanism-side endplate outer face | 64.575 |
| Mechanism-side endplate inner face | 66.075 |
| Drive-side endplate inner face | 286.075 |
| Drive-side endplate outer face | 287.575 |
| Existing upper main-bearing cap origin | 293.7 |
| Upper main bearing | about294.7..299.7 |
| Upper blade-pin end | about298.075 |
| Shaft tip | about308.575, from origin +275 |

The native frame's local levels must be offset by its46 mm assembly placement. The inner carriage maps local +Y approximately to assembly +Z; the ring maps local +Y to assembly -Z. Use `GetTotalTransform(True)` for nested components and transform points explicitly. Do not mix local part coordinates, subassembly coordinates and the fixed-base frame.

## 8. Existing cleanup and local clearance changes

At the user's request, the previous agent deleted31 obsolete suppressed component instances and144 suppressed mates from Assem20. Source part files were retained. The cleanup evidence reported:

- All276 active root components retained.
- No significant active-component pose changes.
- No active mate errors.
- No suppressed root components remaining at that cleanup state.

Earlier temporary setup-angle mates were among the obsolete material removed. Do not run old scripts assuming those names/components still exist. The newer `RevB_SETUP_*` constraints are different, current construction constraints.

Earlier local frame changes:

- `Frame_Mounting_RevA` underside relieved outside a protected R28 central region.
- Relieved underside at base Z39.5.
- Four standoffs OD6/ID3.4/L36.5 at X±24,Y±70, beginning at Z3.
- Fixed-base extensions and matching holes.

These addressed sampled static conflicts only. They do not resolve the rotating sweep. Their long mounting bolts, washers and nuts must be included in any replacement-frame interference and BOM work.

## 9. Mass: new confirmed findings and outstanding work

The original native inventory had68 distinct part/configuration rows and299 leaf instances, including bearing internals. It was captured before the Rev B link replacement.

Examples from that inventory:

- Endplate: reported18 g, volume about41099.9 mm3. At an assumed G10 density1850 kg/m3 that volume alone is about76.0 g per plate.
- Frame: reported25 g, volume about156233 mm3.
- Part1: volume about4840.8 mm3 with default1000 kg/m3 density; no composite construction established.
- Shaft: reported about60.548 g at density7850 kg/m3, machined volume about7713.08 mm3.
- Summed reported leaf mass about256.43 g was not a credible material-based or measured module mass.

**The continuation has now read native override flags**, using `CreateMassProperty2() -> GetOverrideOptions() -> OverrideMass`:

| Inspected part/instances | OverrideMass |
| --- | --- |
| Four `Blade_Pitch_Arm_Offset22p075_PROTOTYPE` instances | True |
| `Frame_Mounting_RevA` | True |
| Both `Endplate_Hub_Interface_RevA` instances | True |
| Outer control ring | True |
| Inner carriage plate | True |
| Four Part1 blade instances | False |
| Four L36.5 standoffs | False |
| Inspected upper cap, lower spacer and lower cap | False |
| Intermediate slider | False |
| Fixed base | False |
| Shaft | False |

These flags supersede the earlier “overrides suspected but not checked” statement **for the listed parts only**. Do not generalize to uninspected parts/configurations. No overrides or materials were changed in this continuation.

After material/geometry decisions, inspect every active part/configuration, record and resolve overrides explicitly, and compute a new Rev B mass report with source hashes. A reference annulus is not a real bearing's mass; virtual bearing internals and cosmetic fastener envelopes require suitable treatment. Use supplier mass when justified and labelled, and measured mass only when measured.

Keep the saved calculation estimate331.108 g and its260 mm shaft assumption unchanged. Report the reconciliation separately and flag any mass-budget impact of the new structure/timing hardware.

## 10. Candidate frame and support arrangement — not implemented or selected

The following is a proposed avenue to investigate, not a mandate to implement blindly:

- Outboard cage pillar centres X±105,Y±85; nominal OD8.
- An upper support underside around Z302 and top306, with a central bearing housing retaining the existing upper-bearing station.
- A lower bearing pedestal supported from beneath the carriage, passing through its central openings.
- A top cap for the lower main bearing, replacing the obstructing bottom-cap arrangement.

Why the envelope is promising: a conservative bound using the native blade's farthest transverse corner relative to its9.5 mm pivot is about `95 + sqrt(28.489^2 + 2.299^2) = 123.58 mm`. An OD8 pillar at(105,85) has an inner radial boundary about `sqrt(105^2+85^2)-4 = 131.09 mm`, about7.51 mm beyond that bound. This is only an envelope calculation, not a native swept-volume check of all rotor hardware. The3.5 mm rotor/frame clearance target must be evaluated for the complete moving assembly and tolerances.

Similarly, Z302 above the existing upper blade-pin end298.075 gives about3.925 mm nominal axial space. New bushings, collars, caps, tool-access features and fasteners can consume it; re-evaluate after integration.

Central-support problem now established:

`D20.5 bore radius10.25 - eccentricity6.88 - D6 post radius3 = 0.37 mm` nominal radial clearance at maximum displacement.

That small margin does not establish operating clearance. Account for positional errors, bore/post tolerances, structural deflection, guide play and thermal effects. Enlarging a carriage bore also affects the inner-retainer PCD25 threads, thin annular walls and other features. A thicker post improves stiffness while worsening clearance. Resolve this tradeoff before treating the arrangement as viable.

The unexecuted `revb_completion.py` draft proposes the following additional details:

- Lower frame Z-8..-4, outer rectangle X±110/Y±90 with opening X±100/Y±80; centre spine X±5; base mounting pads at X±24,Y±70.
- Upper support Z302..306 with similar outer rails/spine; central OD20/D13 bearing seat Z294.7..299.7 and outer shoulder above it.
- Four OD8/ID6/L306 tubes from Z-4 to302.
- Four M3 threaded tie rods cut325 mm, intended Z-13.5..311.5, with end washers/nuts still to be fully specified and assembled.
- Four OD6/ID3.4/L4 spacers between lower-frame topZ-4 and base undersideZ0.
- Lower pedestal flange OD22, Z-4..0; D6 stem Z0..31; OD20 head beginningZ31; closed floor toZ33; D11.4 shaft/clip cavity Z33..41.5; D13 bearing seat Z41.5..46.5.
- Lower-bearing top cap OD22/ID11.4/H1 atZ46.5, three D2.2 holes onPCD16.6.
- Three nominal M2 attachment/tapped envelopes onPCD16.6 at the pedestal flange and cap interfaces.

None of those new parts exists yet. Tube material, tie-rod mass, tube end compression, preload, buckling, structure stiffness, joint locking, head/wrench access and bottom-frame clearance to the servo mechanisms are unresolved. Long steel tie rods have a substantial mass penalty; calculate it before selecting this frame. Do not produce an apparently complete cage with unexplained bonded/clamped joints or unsupported strength claims.

## 11. Candidate physical timing coupling — not implemented or selected

The previous proposal was a custom annular Oldham-type coupling: input attached to the rotor/shaft, output attached to the eccentric ring, floating member with orthogonal sliding interfaces. Investigate whether it provides a practical1:1 timing drive through the complete6.88 mm eccentricity and full rotation.

Candidate axial envelope:

- Output plate baseZ39.5, thickness4, top43.5.
- Floating disk Z43.7..47.7.
- Input plate Z47.9..51.9, with a raised bridge/hub potentially reachingZ60.
- Central openings must clear the stationary pedestal, caps and hardware throughout floating-disk and ring movement.

The draft Python file proposes:

- Output annulus OD92/ID40/H4, two Y-directed tongues W4/L10/H2 spanning R28..38.
- Floating annulus OD92/ID40/H4; underside Y slots and upper-side X slots, width4.1/depth2, open at inner/outer radii.
- Input annulus OD92/ID24/H4, downward X-directed tongues of similar size, raised central bridge and D6-bore/OD14 hub.
- Nominal0.1 mm tongue/slot width difference. This permits backlash; do not call it zero-backlash.
- Approximately0.2 mm face gaps and1.8 mm nominal engagement from the proposed2 mm tongue/slot heights. Verify these with actual geometry, axial tolerance stack and loss-of-engagement cases.

Required design work before implementation/acceptance:

1. Choose a torque path with actual shaft-to-input and ring-to-output fastening, phase indexing and positive retention. A lock mate or keyed-looking sketch alone is insufficient.
2. Avoid placing output attachment screw heads in the floating-disk sweep or replacing ring-ball fasteners with overlapping hardware.
3. Verify central-hole clearance for every relative offset. A floating disk can move relative to both input and output; one centred section is insufficient.
4. Confirm sliding length/engagement at maximum eccentricity and all rotor angles; include manufacturing fits and backlash-induced pitch error.
5. Define axial retention without clamping the floating disk or allowing it to escape/disengage.
6. Define sliding materials, lubrication/contamination strategy, wear, friction and heat. Do not infer a load/speed rating from a generic Oldham coupling.
7. Evaluate inertia and friction loads at2640 RPM and6.88 mm eccentricity, using the actual selected geometry and mass. Shaft phase, ring phase and blade loads interact.
8. Install physical parts and sliding constraints that represent the actual interfaces. Artificial independent ring-angle driving is acceptable for a documented geometry probe, but not proof that the real timing mechanism works.
9. Remove the ring setup-angle hold only after the physical connection closes correctly. Then demonstrate that moving the rotor drives the ring without independently prescribing its angle.
10. Keep the non-sinusoidal pitch-law distinction and check closure branch continuity.

Manufacturer information consulted only to understand limitations, not to rate this custom design:

- Ruland's coupling-selection guide discusses Oldham sliding interfaces and limited angular/axial accommodation: <https://www.ruland.com/media/wysiwyg/PDF/Coupling-Selection-MV-OI.pdf>.
- A specific Ruland41.3 mm commercial coupling lists maximum parallel offset4.13 mm: <https://www.ruland.com/oct26-12-a-od26-41-pek-mosc41-11-a.html>. Its specifications do not approve a custom6.88 mm-offset annular design or establish simultaneous capacity at every listed maximum.

An Oldham solution may be rejected if packaging, backlash, mass, sliding loads or retention prove unacceptable. Develop a justified alternative within the user's pitch-preserving authorization; do not present this candidate as already chosen.

## 12. Blade bushings, axial allowance and retention: required design

Current aerodynamic blade span and endplate inner-face separation are both220 mm. There is no established axial running allowance. Native blade journals are D3; endplate blade holes are D6.

The specification's `JFM-0306-04` dimensions remain unverified. An older official igus catalogue did not contain that exact part. Its `JFM-0304-05` row instead specified ID3, OD4.5, flangeOD7.5, length5, flange thickness0.75 mm. This cannot be substituted directly into the currentD6 holes.

Source: <https://www.igus.com/us/pdf/j.pdf>. Recheck the actual selected manufacturer's current drawing before using a part number. If a reference cannot be retrieved, retain the limitation rather than inventing dimensions.

Required work:

- Establish an actual purchasable bushing or a fully defined custom bushing/adapter, including installed bore, flange orientation, housing fit and rotation surface.
- Build an axial stack with flange thicknesses, shoulder locations, endplate thicknesses, journal lengths, thrust faces, running allowance and tolerances.
- Provide positive blade axial retention that permits pitching; do not use a clamping stack that immobilizes the bearing or rely on an unexplained floating journal.
- Determine whether to change endplate spacing, add hub/endplate spacers, change journal shoulders or use another interface. Preserve220 mm aerodynamic span unless a reasoned, explicitly recorded mechanical decision requires otherwise; changing the aerodynamic baseline is outside this task.
- Any endplate spacing change affects hub pilot engagement, bolt lengths, blade-centre mates, arm elevation, rod plane, frame clearance and upper retention envelope. Check all dependencies together.
- Do not introduce shims that eliminate pilot engagement or leave bolt threads short of their nuts.
- Check D-flat/pitch-arm engagement length and trunnion torque transmission after axial changes.
- Inspect all four blades and both ends; a correctly positioned bushing at one journal is not an assembly-wide pass.

## 13. Socket retention, arms and fasteners: required design and analysis

Do not equate the existing spherical mate with a retained physical joint. The current ball/socket geometry leaves insertion, pullout, wear and manufacture unresolved.

Required work:

- Select a retainable joint construction: a verified purchased joint, a designed split/capped socket, or another justified manufacture/assembly method.
- Preserve or deliberately revise ball centres and effective rod length if the new joint changes the geometry; repeat dependent pitch/clearance checks.
- Define ball insertion and assembly sequence, mechanical pullout retention, tube insertion depth, adhesive or mechanical tube retention, and inspection criteria.
- Check whether a planar pin joint is appropriate before retaining unnecessary spherical articulation; any topology change must be justified against actual alignment/motion and existing constraints.
- Evaluate the offset arm's twin webs, platform, fillets, eye, D-flat/boss and clamp connection for bending, torsion, fatigue and stress concentrations using declared loads and material properties.
- Build a load-case record: aerodynamic hinge loading, pitch inertia, centrifugal loading, timing-drive friction/inertia, stop/jam and assembly preload where relevant. Label values as measured, source-derived, calculated or assumed. The saved analytical model is not an approved operating-load envelope.
- If necessary load or fatigue requirements are unavailable, provide a provisional calculation with explicit assumptions and a list of decisions/tests needed. Do not issue a strength sign-off from arbitrary loads.
- Review every active fastener interface: diameter/pitch/length, head and tool access, washer stack, thread engagement, nut protrusion, blind-hole bottoming, edge distance, remaining web, material, grade, preload and anti-loosening.

Specific existing concerns to carry forward:

- Compact arm-side M2x10 stack had only about0.3 mm nominal protrusion beyond the nut. Tolerances and screw-end lead-ins can consume it.
- Ring-side M2 blind engagement was about3.7 mm in the earlier stack; verify against current geometry and material.
- Some guide-block screws have about1 mm nominal engagement in supplier M2×1.5-deep holes.
- Some plate webs are under1 mm after counterbores.
- Several low-head screws and unusual lengths are custom envelopes without a final drive form, grade or supply specification.
- Existing thread-envelope overlaps can be intentional, but classify each with an actual interface definition rather than ignoring all screw collisions.
- Existing provisional Loctite222 selection in the connection notes is not applied/cured hardware evidence; confirm suitability, preparation and torque with selected materials/supplier data.

## 14. Servo/horn interfaces: what can and cannot be completed

The user has no actual servo/motor/horn hardware to measure. Do not repeatedly ask for measurements from nonexistent hardware or invent delivered dimensions.

Existing custom horn spline was extracted from the official Savox SH-0257MG+ STEP. There is an unresolved dimensional conflict:

- Official STEP crown diameter about5.0 mm.
- Product-page nominal output identity21T D4.8.
- The stationary servo body remains the older project's case envelope, not a complete replacement with the newer supplier case.

Reference files:

- `CAD/Connections_Completion/Manufacturer_References/sh-0257mgp.STEP`
- `SH-0257MGP_3D.zip`
- `SOURCE.json`
- `OFFICIAL_MODEL_FACES.json`

Supplier sources:

- <https://www.teamsavox.com/product/sh-0257mgp/>
- <https://web.teamsavox.com/wp-content/uploads/2025/05/SH-0257MGP_3D.zip>
- <https://www.savoxusa.com/products/savsh11m-sh11m-micro-servo-horn-set>

Required work:

- Resolve the exact servo model/revision and compatible horn part or obtain authoritative clarification of the spline conflict.
- Compare supplier mounting ears, case, output-axis location, horn retention screw and spline engagement against the actual current mounts. A compatible output extraction does not verify the stationary-case mounting envelope.
- Prefer a verified compatible commercial horn where it satisfies the required radius/interface; otherwise specify custom-horn manufacture and fit verification explicitly.
- Verify servo stroke, guide travel, linkage mechanical advantage, torque and speed against declared load cases and supply voltage. A nominal torque on a product page is not proof of transient duty or thermal suitability.
- Preserve an interface drawing and incoming-inspection checklist if supplier/delivered fit remains unresolved.
- Do not label actual hardware fit “complete” without suitable evidence. This does not prevent completing other mechanical work.

## 15. Materials, fits, tolerances and drawings

Build a part/configuration-level material and fit register. It must distinguish intended, assigned, supplier-specified and measured material/mass.

Required work:

- Resolve actual material choices for structural plates, frame/cage, bearing pedestal, shaft, arms, bushings, sockets, balls, rods, horns and fasteners.
- Record the shaft4340-versus4130 conflict explicitly; do not silently change it while fixing another part.
- Define composite construction where relevant. Assigning a bulk density to a solid blade is not a skin/core/spar definition or strength model.
- Read and document mass-override flags for all active configurations. Preserve the pre-change values and rationale before correcting overrides in isolated revised parts.
- Define bearing seats and locating/floating strategy, journal/bushing fits, pin holes, sliding fits, tongue/slot clearance, thread specifications, datum references, perpendicularity/runout, edge breaks and finish.
- Use supplier fit instructions for polymer bushings and miniature bearings; a generic metallic fit choice can be wrong for these parts.
- Complete tolerance stacks for blade axial allowance, bearing retention, hub pilots, shaft clips, Oldham engagement/backlash, carriage-post clearance and critical screw stacks.
- Create native manufacturing drawings for custom parts and an assembly drawing/BOM, with dimensions, tolerances, materials, finish, hole/thread callouts, quantities, revision and notes.
- Include assembly order, locking/retention methods and inspection points. Modelled major-diameter thread envelopes must not be dimensioned as tap-drill diameters.
- Export reviewable drawing PDFs and inspect their rendered content for legibility, completeness and consistency with the referenced CAD revision.

If loads, supplier fit or manufacturing inputs remain unresolved, issue drawings clearly marked **PROTOTYPE / NOT RELEASED FOR FABRICATION** and enumerate release holds. Do not leave ambiguous “TBD” information while claiming production readiness. A picture, STEP file or unannotated view is not a manufacturing drawing.

## 16. Recommended implementation sequence and dependencies

### Phase A — Resume, isolate and freeze the reference snapshot

1. Confirm live SolidWorks document, dirty state, references and processes. Avoid redoing the lengthy inventory if the files/pose still match and only a focused confirmation is needed.
2. Read the current maps and selected linkage. Record the actual live pose in a new task state file.
3. Save a recoverable copy of affected task documents and hashes before mutation. Preserve unsaved edits appropriately; do not save unrelated open user documents.
4. Inventory shared references that will be edited. Create distinct revised part/subassembly filenames and redirect only the working assembly as needed.
5. Reconcile which statements in older notes are historical. Keep a six-area status table from the outset.

Acceptance: a known, recoverable input set; original shared parts protected; no unexplained live-state differences.

### Phase B — Close mechanical packaging before detailed manufacture

1. Use the selected56.526653 mm linkage and actual native geometry to map moving envelopes and required clearances.
2. Resolve frame support positions together with bearing support, central-post passage, blade axial allowances and timing-coupling envelope.
3. Evaluate candidate mass/stiffness consequences before choosing the cage. Revisit topology if it cannot fit or support the required loads reasonably.
4. Establish coordinate frames, axial stack and physical load paths. Record the selected solution versus rejected alternatives briefly.

Acceptance: a justified layout with no known geometric impossibility and explicit unresolved load/fit assumptions. Do not equate nominal envelope separation with operating clearance.

### Phase C — Implement frame, bearing supports and their real attachments

1. Create native parts using isolated sources.
2. Integrate the frame/supports into Rev B with actual attachment hardware and correct bearing stations.
3. Resolve old frame/posts/cap/hardware replacements deliberately. Preserve recoverable history; do not leave duplicate active structures or dangling mates.
4. Check bearing/clip/shaft shoulders, cap contact lands, base attachments and assembly/tool access.

Acceptance: implemented native structure, physically defined attachment paths, clean affected rebuild/mates, verified critical interface dimensions and a first focused collision check.

### Phase D — Implement the physical timing drive

1. Finalize the selected timing mechanism's geometry, attachments, indexing, retention and motion interfaces.
2. Integrate it with rotor and ring while temporarily holding the known construction pose.
3. Replace the independent ring construction constraint with the actual mechanism constraints.
4. Drive rotor motion and observe ring response without prescribing ring motion separately. Check phase error/backlash and branch continuity.
5. Remove or suppress remaining temporary angle holds when safe, restoring intended degrees of freedom and travel limits.

Acceptance: ring timing is produced by implemented physical geometry/constraints and demonstrated natively; no hidden construction hold is masquerading as the timing mechanism.

### Phase E — Close blade, joint, arm and fastener interfaces

1. Implement the selected bushings/adapters, axial allowance and positive retention at every blade end.
2. Implement retainable joints and rod retention, preserving/rechecking effective centre length.
3. Resolve pitch-arm coupling, socket envelope, connection fasteners and relevant strength calculations.
4. Recheck all affected axial stations and frame/timing interfaces after these changes.

Acceptance: every moving connection has a specified physical retention/assembly method, native geometry and defined fits; unverified loads/tests are explicitly listed.

### Phase F — Supplier interfaces, material assignment and release documentation

1. Complete authoritative servo/horn reconciliation as far as evidence permits.
2. Finalize/propose materials and fits with evidence, inspect/correct overrides in isolated revised parts, and produce the new mass/BOM report.
3. Produce native drawings and reviewed PDFs with appropriate release status.

Acceptance: documentation matches actual revised geometry and exposes remaining supplier/load/test holds.

### Phase G — Consolidated final native check and return

Run the coherent checks below on the final geometry, restore the intended user pose/usable constraints, save only task documents, record final hashes and return the evidence. Avoid rerunning full campaigns after purely editorial changes.

## 17. Verification strategy: meaningful checks with honest scope

Choose tolerances and sampling/refinement rules before inspecting the results. Do not loosen them to hide failures. Keep calculations in SI internally or explicitly labelled mm/deg; avoid unit mixing.

### Kinematics

- Verify all four actual ball-centre distances, spherical/pin interfaces, axial offsets and linkage branch.
- Check centred carriage and maximum allowed radial eccentricity through rotor rotation. Cover eccentricity directions relative to the non-axisymmetric frame and actuator geometry.
- The allowed XY region is the radius6.88 mm disk. X=±6.88 and Y=±6.88 simultaneously is outside it and belongs only to explicitly labelled overtravel/stop probes.
- Verify pitch extrema and phase against the selected calculation and the ±35° requirement, including tolerances/backlash where modelled.
- Record non-sinusoidal pitch over the cycle for downstream analysis.
- Check the actual physical timing mechanism, not independently driven ring and rotor angles.
- Check slider limits, stops, branch changes, solver flips, singularities and loss of joint/tongue engagement.

### Clearance

- Include blade bodies/journals/retention, endplates/hubs/pins, offset arms, sockets/balls/rods/fasteners, ring/timing parts, bearing supports/caps, frame/posts/base, guide and servo hardware.
- Use conservative continuous envelopes where valid, and native copied-body Boolean/distance checks for critical interfaces and predicted worst cases.
- A sparse set of poses cannot prove continuous clearance. Refine near minimum gaps and changes of contact; document what bounds the intervals between samples or leave that portion unverified.
- Check both positive overlap and minimum running gaps. “No intersection” does not prove3.5 mm rotor/frame clearance or sufficient tolerance/deflection allowance.
- Use correctly transformed copies of native bodies. Temporary body handles may become invalid after rebuild; copy them before reuse and refresh them when geometry changes.
- Classify intentional contacts individually: bearing fits, threaded envelopes, bonded interfaces. List exclusions and do not silently exclude a collision-prone pair because it was present before.
- Include an axial- and radial-tolerance/deflection budget for critical interfaces. CAD operates on nominal rigid bodies.

### Build and state

- Check feature/body validity and affected mates during each integration step; perform one complete active-mate/rebuild inspection at the final consolidated state.
- Confirm no obsolete setup constraints lock intended motion, no duplicate components were inserted, and no missing references remain.
- Restore the intended carriage/rotor pose after probes; document any deliberately changed design pose.
- Validate the final saved source hashes and report precisely which assembly they certify.

### Strength and physical tests

- State assumed load cases, sources, materials, margins and limitations for every calculation.
- Keep fatigue, buckling, bearing life, fastener preload/slip, socket pullout, adhesive qualification, servo thermal/dynamic response and vibration/balance tests distinct from geometry checks.
- Provide a specific physical verification plan with test item, method, required inputs, acceptance criterion to be approved, and the release claim it blocks.
- Do not invent measured results or label an assumed load as approved by the user.

## 18. Automation guidance and known traps

Reuse existing helpers; do not rewrite the entire CAD automation layer. Primary helpers:

- `%TEMP%\cycloprop_frame_hub_connections.py`
- `%TEMP%\cycloprop_connections.py`

Load definitions without executing their main blocks:

```python
exec(Path(path).read_text().rsplit('\nif __name__', 1)[0])
```

Use `rsplit`, not a generic split on `if __name__`, because helper files contain nested loaders. Inspect top-level statements as well: removing a main block does not make every historical script safe to import.

The helper chain also uses `cycloprop_stop_mounts.py`, `cycloprop_travel_stop.py`, and `cycloprop_servo_layout.py`. Their `OUT`, `ST`, state functions and document paths can point at original/historical work. Override them deliberately or write narrow new wrappers; do not accidentally update the original connection state or `Assem20.SLDASM`.

Recent completed historical scripts:

- `cycloprop_kinematic_feasibility.py`
- `cycloprop_link_symmetric_solve.py`
- `cycloprop_select_short_link.py`
- `cycloprop_remaining_inventory.py`
- `cycloprop_remaining_bom.py`
- `cycloprop_revb_links.py`
- `cycloprop_revb_interfaces.py`

Latest completed read-only script:

- `%TEMP%\cycloprop_resume_native.py` -> `RESUME_NATIVE_STATE.json`.

**Do not rerun `cycloprop_revb_links.py`: it can insert duplicate short-link components.** Other scripts may also lack restart safety. Read their guards and persisted progress before invocation.

Optimized COM method wrapper:

```python
def c(o, name, *args):
    if name not in o._olerepr_.mapFuncs:
        o._FlagAsMethod(name)
    return getattr(o, name)(*args)
```

Other API details:

- `GetMaterialPropertyName2` needs a BYREF BSTR database argument, not an integer reference.
- `IBody2` uses `GetMaterialPropertyName`, not `GetMaterialPropertyName2`.
- Confirmed override-reading path: `CreateMassProperty2`, `GetOverrideOptions`, `OverrideMass`.
- `ReplaceComponents2(FileName, ConfigName, ReplaceAllInstance, UseConfigChoice, ReAttachMates)` operates on selected top-level components; replacing subassembly children requires appropriate subassembly context. It can close component documents and does not automatically save their modifications. Preserve work before replacement and verify mate reattachment afterward. Check the installed/current API documentation before relying on a signature.
- Reference-plane matches do not guarantee face-mate reattachment to a newly generated part. Inspect affected mates and actual poses.
- Row-vector transform convention used by existing code: `world = local @ rotation + translation`, with the first9 transform entries reshaped3×3 and entries9:12 as translation.
- `GetTotalTransform(True)` matters for flexible nested subassemblies.
- Save only task documents, not all open documents.
- Use `try/finally` to restore `CommandInProgress`, graphics updates and feature-tree settings if disabled.
- COM calls can be slow; batch reads, cache repeated part data and avoid full scans during every small edit. The latest full inventory took several minutes. A quiet console is not automatically a deadlock.
- Run native CAD operations serially. Never launch concurrent mutation scripts. If interrupted, inspect running processes and persisted state before restarting; do not kill SolidWorks or discard unsaved work as a routine recovery step.

## 19. Required deliverables and return format

Keep new deliverables under `CAD/Design_Completion/` or a clearly named revision subdirectory. Names below are suggested output contracts; do not overwrite historical evidence with a different scope.

1. Revised working native assembly and all required revised/new referenced parts/subassemblies.
2. Updated task state with original/final poses, component mappings, backups, source hashes, completed steps and unresolved items.
3. `MECHANICAL_COMPLETION_REPORT.md`: decisions, implemented changes and six-area status table.
4. Kinematic/timing evidence with actual native poses, pitch/phase/branch checks, physical drive definition and limitations.
5. Clearance evidence with minimum gaps, worst poses, native overlap results, continuous bounds/refinement, tolerances and explicit exclusions.
6. Material/override register and revised BOM/mass report with assumptions and supplier/geometry/mass evidence separated.
7. Strength/load-case notes with unresolved loads and physical test requirements.
8. Native custom-part/assembly drawings and inspected PDF exports, clearly marked with release status.
9. A concise master-chat return: what changed, where, what passed, what failed, what was not performed, and what specifically requires user/supplier/hardware input.

For each of the six areas use: **implemented and checked for stated scope**, **implemented but unverified**, **needs revision**, or **awaiting named external input/test**. Link evidence. Do not use an overall “complete” or “fabrication-ready” label while required interfaces, loads, drawings or physical checks remain unresolved.

Before ending, verify that no task Python mutation process remains active unintentionally, the CAD is saved in a recoverable usable state, temporary constraints are accurately reported, and the calculation-baseline input hash remains unchanged.

## 20. First action for the receiving agent

Read `REV_B_STATE.json`, `RESUME_NATIVE_STATE.json`, `SELECTED_LINKAGE.json` and the draft `revb_completion.py`; confirm the live assembly/reference state. Then resolve the frame/central-support/timing packaging together, with the D20.5 bore and retainer-wall constraints included, before executing part generation. Continue from the four installed short links. Do not repeat their installation or promote the unimplemented cage/Oldham proposal to a verified design.
