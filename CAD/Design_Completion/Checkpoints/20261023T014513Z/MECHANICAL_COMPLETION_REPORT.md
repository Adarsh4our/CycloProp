# CycloProp Rev B: implementation checkpoint

The revised mechanism exists in native SolidWorks and is saved in an isolated reference tree. This pass added retained blade-bearing cartridges, removable socket caps, arm crosspins and longer arm-side screws; corrected material/mass assumptions; restored travel limits; and produced prototype inspection drawings. **The complete handoff is not finished and fabrication/operating readiness is not established.** The actuator selection needs revision, composite/metal-trunnion construction is undefined, manufacturing tolerances/details remain open, and physical qualification has not occurred.

## Working files and protection

Open [RB_Assem20_Design_RevB.SLDASM](RevB_Isolated/RB_Assem20_Design_RevB.SLDASM), together with its RevB_Isolated reference tree. Do not resume the historical top-level RevB assembly or repeat integration scripts.

[ORIGINAL_AND_BASELINE_PRESERVATION_CHECK.json](ORIGINAL_AND_BASELINE_PRESERVATION_CHECK.json) compares69 surviving isolation-source files: none changed. Two historical temporary source paths were absent; this is not a missing-reference finding in the isolated assembly. The current BOM scan found no unresolved loaded components. The calculation baseline SHA256 remains2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f. Original assemblies and baseline inputs were not edited. Recovery copies and per-integration state files preserve prior geometry.

Native access: SolidWorks2026, geometry/body Boolean operations, component transforms, materials/mass overrides and mate definitions were inspected through its API. This is native inspection, not an inference from filenames. No hardware was measured.

## Six work areas

| Area | Status | Evidence and limits |
| --- | --- | --- |
| Rotor/frame clearance | Implemented and checked for stated scope | Cage, pedestal, lower/upper bearing supports and hardware installed. FRAME_STATIC_CHECK.json passed163 affected-pair Boolean comparisons. Conservative blade/pillar gap7.511mm,6.511mm after proposed1mm adverse budget. Full loaded moving-clearance release remains open. |
| Physical ring timing | Implemented and checked for stated scope | Three-part Oldham with real shaft pin and ring pilots/bolts; accepted native shaft-angle driving demonstrates ring response. Earlier nominal revolution/critical-pitch checks below. Current XY and radial limits restored; rotor/ring construction-angle holds suppressed. Final free-drag/loaded campaign after these changes not performed. |
| Blade supports, endfloat and retention | Implemented but unverified | Eight F693ZZ-envelope cartridges installed; endplate holesD10.02; two0.65mm hub shims and longer hub bolts. Native nominal0.20mm gap each blade end,0.40 total;202 saved-pose Boolean comparisons passed. Bearing fits/contact lands, G10 edge ligament/clamp loads, oscillatory life and actual trunnions remain release holds. |
| Joints, arms and fasteners | Implemented but unverified | Eight threaded socket caps permit ball insertion/capture. FourD1x8 coiled-pin reference envelopes and matching arm/trunnion holes provide a proposed physical retention path. Four arm-side screws replaced byM2x12; nominal nut protrusion improves0.3 to2.3mm. Steel reference envelopes and rigid mates do not prove press retention, preload, bond strength, pullout, wear or fatigue. |
| Servo/horn interfaces | Needs revision; awaiting named supplier/load input | Provisional2640RPM inertia-only Xservo screen requires0.280Nm versus published0.216Nm at6V, before aero/friction loads. Present actuator selection is inadequate under those assumptions. Official STEP crownD5.0 still conflicts with nominal21T/D4.8 identity; old case envelope is not confirmed as the supplier revision. No delivered servo/horn exists to measure. |
| Materials, fits and drawings | Partially implemented; manufacturing release incomplete | Nine primary and additional secondary assignments/density proxies read back natively.87 active part/configuration rows,405 leaf instances, material/override register and CSV generated. 31 active native prototype inspection drawings/PDFs exported. These have interface/dimension notes and explicit holds; undimensioned legacy contours, thread runouts, GD&T, fits and manufacturing details are not released. |

## Checks: passed, failed and not performed

| Check | Outcome / evidence |
| --- | --- |
| Original source/baseline preservation | Passed: ORIGINAL_AND_BASELINE_PRESERVATION_CHECK.json. |
| Physical timing: nominal sampled360degree shaft drive | passed sampled native full revolution at construction XY offset. |
| Centred carriage and e6.88mm revolution | passed sampled native full revolution at maximum radial travel and centred closure. |
| Native nominal pitch extrema vs dense planar solution | passed native nominal extrema; does not include tolerance/backlash/loaded variation; approximately-34.98966/+34.99110deg. |
| Oldham affected solids at saved pose | passed;57 comparisons. |
| Blade support stack and affected solids | passed;202 comparisons; all4 blade gap pairs checked. |
| Modified socket bodies/caps at saved pose | passed;98 comparisons. |
| Added arm crosspin envelopes at saved pose | passed;8 comparisons. |
| Four longer arm-side screws at saved pose | passed. |
| Restored axis/radial limits and suppressed setup holds | Passed native rebuild/affected transforms and full active-mate scan; zero mate errors. |
| Material and target-override corrections | Passed for listed parts only; MATERIAL_CORRECTION_STATE.json and SECONDARY_MATERIAL_ASSIGNMENTS.json. |
| Servo torque selection | Failed provisional inertia-only screen; SERVO_LOAD_AND_INTERFACE_SCREEN.json. |
| PDF/source identity, text bounds and rendering | See Drawings_Prototype/PDF_QA.json and DRAWING_INDEX.json. Visual layout/representative full-size checks are distinct from manufacturing completeness. |
| Continuous all-pair moving clearance, loaded pitch/backlash, fatigue, physical hardware mass/fit and operating-speed tests | Not performed / not established. Earlier motion evidence predates the latest retention/fastener additions. Local saved-pose checks are not a replacement for final motion verification. |

The earlier direct-transform/DragAsUI probes did not propagate locked groups reliably and were rejected. Recovery copies preserve those failed states. Accepted timing evidence used a native shaft angle mate with an explicit direction reference; ring motion was not independently prescribed. Current construction holds are now suppressed after restoring the existing limit mates.

The radial constraint's maximum distance19.27005mm includes the fixed18mm axial separation: sqrt(18^2+6.88^2). Its distance must not be mistaken for a19.27mm radial allowance. Axis constraints use5.12..18.88mm datum distances, corresponding to-6.88..+6.88mm displacement.

## Implemented interfaces and remaining engineering limits

Cartridges use D10 pilot/M10x0.5 nut, OD14 flange, proposed7075 housing, F693ZZ3x8x4 flange9.5x0.9 envelope and M14x0.5 outer cap. Steel inner-ring-only spacerOD4/ID3.05/H0.3 and PTFEH0.15 keep nominal thrust off shields. Upper main-cap screw heads were reduced to a sourced1.3mm button-head envelope after a native interference was found. Housing, cap, flange and nut tool holes are implemented. Thread helices, root relief/runouts, qualified locking and torque are not.

Socket caps use M6x0.35 major envelopes with1.4mm nominal engagement, flangeOD7/H0.5, matchedD5.05 spherical seat andD4.4 mouth. Opening the cap permitsD5 ball insertion through theD6 body opening. All original joint centres and56.526653mm rod lengths were preserved. The tube remainsOD2/ID1/L46.526653 with2.5mm insertion into eachD2.1x2.7 bond bore.

Arm crossholes lie at arm-localZ1.75, corresponding to blade-localZ-7.75, directed along blade-localY. Proposed line-ream1.00..1.02mm lies within SPIROL's published1.00..1.04 recommended range for standard-dutyD1 coiled pins. The installed solidD1x8 envelope omits coils and does not establish actual spring-pin mass, grade or retention. The documented blade steel/titanium trunnion and composite spar/bond must be physically defined before fabrication; drilling a monolithic CAD journal does not define that construction.

ARM_ROD_RETENTION_STRENGTH_SCREEN.json is an explicitly idealized screen: uninterrupted twin rectangular webs predict21.3MPa offset bending under the previous inertia-only rod force; the tube needs about14.3GPa axial modulus for the proposed3x pinned-end Euler screen; average bond shear at that screening force is about3MPa. These are requirements/assumptions, not actual material allowables, minimum-section stress or fatigue approval. Approved aero/imbalance/jam loads and measured blade inertia remain absent.

FRAME_SUPPORT_LOAD_UPDATE.json uses a provisional50N transverse load, predicting0.152mm post deflection and0.27mm remaining radial gap after its proposed0.35mm adverse budget. It supersedes the older20N screen. Supplier bearing speed ratings do not approve44Hz pitch oscillation, nor establish bearing life or false-brinelling resistance.

## Mass, materials and design conflicts

The current native leaf-reference sum is **1109.958g**. It is a mixed reference/provisional-density result, not measured hardware mass or a certified module mass. Unassigned blade/guide/virtual-bearing properties, purchased solid envelopes and fixture scope prevent a trustworthy final hardware total. The only remaining inspected mass override is the servo's manufacturer-nominal14g reference; its modeled older case and delivered fit are still unverified.

Each revised G10 endplate now reports75.47g at assumed1850kg/m3, outer ring83.57g and inner carriage33.12g at proposed7075 density. Former target overrides were removed. Many steel hardware envelopes use the4340 library **only as a7850kg/m3 density proxy**, not as selected purchased grade or strength evidence. Explicit materials/bases are in [REVISED_NATIVE_MATERIAL_BOM.csv](REVISED_NATIVE_MATERIAL_BOM.csv).

The density-only G10/CFRP database is retained under Materials/ and was copied into the existing SolidWorks Material Databases folder. No system preferences or existing databases were changed. On another computer, install the retained database in a configured material folder or add the project Materials folder; inspect readback before mass calculations. No unsupported elastic/yield properties were inserted.

Conflicts remain explicit: calculation shaft6x260mm/57.708g versus the native machinedD6 shaft with solid localZ2..275; specified4130 versus assigned4340; old331.108g module estimate versus the much heavier revised bench assembly; nominal sinusoidal35degree calculation input versus actual non-sinusoidal linkage law. The approximate0.009degree nominal pitch margin is less than the0.205degree coupling play screen. Preserve the35degree target and baseline inputs; resolve the loaded tolerance requirement before accepting a design baseline change.

## Drawings and physical verification

[Drawings_Prototype/DRAWING_INDEX.json](Drawings_Prototype/DRAWING_INDEX.json) identifies active model/drawing/PDF hashes. Two uninstalled candidate sheets were moved into Superseded_Candidates. Sheets are marked DO NOT SCALE and PROTOTYPE / NOT RELEASED FOR FABRICATION. They are prototype inspection/interface drawings, not a complete production manufacturing package. Existing legacy custom parts and composite/trunnion construction still need full dimensions and released manufacturing definitions.

[FIT_TOLERANCE_AND_PHYSICAL_RELEASE_REGISTER.md](FIT_TOLERANCE_AND_PHYSICAL_RELEASE_REGISTER.md) lists interfaces, nominal stacks, exact missing inputs, proposed limits and test methods. No test there is reported as performed. Needed qualification includes incoming dimensions/material, blade endfloat/alignment, arm pin/trunnion retention, socket/bond pullout and fatigue, servo thermal/holding response, loaded pitch/backlash, balance/vibration and guarded staged-speed testing.

## Smallest next tasks

1. Establish approved mechanical load/life and blade mass/inertia inputs; select an adequately rated actuator/ratio, preserving35degree pitch and unchanged calculation baseline.
2. Define the real composite blade, metal trunnions and their bond/manufacture. Release cartridge fits/contact lands, G10 clamp/ligament limits and pin attachment.
3. Resolve joint locking/lubrication/bond process, remaining short guide-block threads, custom low-head fastener procurement and tolerance stacks; complete legacy manufacturing drawings and native assembly BOM/balloons.
4. Freeze final geometry, finish moving-clearance/backlash and usable-motion verification, then perform the named physical tests. No fabrication/operating release before these holds close.

Aerodynamic performance, CFD execution and structural certification are not claimed as satisfied by this work.
