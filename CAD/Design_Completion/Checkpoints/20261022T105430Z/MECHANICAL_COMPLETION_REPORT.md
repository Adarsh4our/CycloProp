# CycloProp Rev B mechanical completion — working report

Implementation remains in progress. The revised cage and physical timing coupling exist in native CAD. Blade supports/retention, joint retention, supplier interfaces, the final material/BOM register and drawings are still open. No fabrication or operating release is claimed.

## Working assembly and recovery

Use [RB_Assem20_Design_RevB.SLDASM](RevB_Isolated/RB_Assem20_Design_RevB.SLDASM). This is the isolated reference tree, not the historical Rev B top-level file. Native Pack and Go copied71 files with an RB_ prefix. The copied6806 STEP link was detached into embedded virtual native components; the original bearing remains preserved. See ISOLATION_MANIFEST.json and BEARING_DETACH_RESULT.json.

Original assemblies and calculation-baseline inputs remain unchanged. Recoverable native copies are under Recovery/. The historical revb_completion.py draft was not executed. Revised automation is under automation/.

## Six work areas

| Area | Status | Inspected evidence and remaining scope |
| --- | --- | --- |
| Rotor/frame clearance | Implemented and checked for stated scope | New cage, pedestal, bearing seats/caps and reference fasteners installed. FRAME_INTEGRATION_STATE.json records clean active-mate rebuild. FRAME_STATIC_CHECK.json passed163 native Boolean comparisons with zero intersections at the saved pose. Conservative pillar/header bounds are recorded; final all-component moving clearances remain pending. |
| Physical ring timing | Implemented and checked for stated scope | Three-part Oldham coupling, four piloted standoffs, four M2 screws and shaft crosspin installed. Ring setup-angle hold suppressed. Native shaft-angle driving, joint closure and nominal pitch evidence below. Backlash, loaded gaps, wear and speed qualification remain open. |
| Blade supports, axial allowance and retention | Needs revision | Existing D3 journals in D6 plate holes and zero nominal blade/endplate allowance remain. Supplier designation/geometry conflicts and preliminary load screen are recorded in BLADE_SUPPORT_SELECTION_SCREEN.json. No blade-support holes have been changed. |
| Joints, pitch arms and fasteners | Implemented but unverified | Existing spherical socket prototypes remain. Physical insertion/pullout retention, arm attachment, fatigue, bond strength and released fastener specifications remain unresolved. |
| Servo/horn interfaces | Awaiting named external input/test | No delivered hardware available. Official Savox STEP crownD5.0 conflicts with nominal21T/D4.8 product identity. Toleranced supplier output/horn/case drawings or compatible physical samples, plus holding/thermal/dynamic-duty validation, are required. |
| Materials, fits, tolerances and drawings | Needs revision | New cage/coupling parts have explicit provisional library materials and no mass overrides. Historical target overrides and missing assignments remain in existing copied parts. Final revised BOM, fit register, native drawings and inspected PDFs remain pending. |

## Native timing checks

| Check | Result |
| --- | --- |
| Construction-offset full revolution, shaft alone prescribed by native angle mate | passed sampled native full revolution at construction XY offset |
| Centred closure and full revolution at eccentricity6.88mm | passed sampled native full revolution at maximum radial travel and centred closure |
| Dense-planar-analysis pitch extrema checked in native assembly | passed native nominal extrema; does not include tolerance/backlash/loaded variation |
| All new coupling solids against resolved leaf solids at saved pose | passed |

The checks inspect actual ring phase, both sliding-centre constraints, all four56.526653mm ball-centre distances, ball/socket centres, axial alignment and blade-pitch branch. They do not independently position the ring. The temporary shaft angle mate remains active as a construction drive; fixed XY setup dimensions remain until the final consolidated check. They must be removed/restored to usable travel before delivery.

Direct-transform and drag probes did not produce trustworthy propagation through locked rotor groups. Those failed probe states are preserved under Recovery/Direct_Transform_Probe and Recovery/Native_Drag_Probe. The assembly was restored from saved native copies. The accepted motion method changes the shaft angle mate and verifies actual shaft direction; a Front Plane direction reference prevents its opposite-direction ambiguity. Failed probes are not counted as passed motion evidence.

## Implemented packaging

The cage has four aluminum OD8/ID6 compression sleeves at X±105,Y±85, with M3 tie rods, lower frame, upper header and separate lower bearing pedestal. The revised upper header underside is Z304mm. The D5.5 steel pedestal retains the existing D20.5 carriage bores. Its head begins Z32.8 to clear inner-retainer screw heads reaching Z32.3. The isolated shaft nose was shortened by2mm; its assembly origin, hub/bearing stations and220mm blade span remain unchanged. Nominal nose/floor clearance is0.575mm. See FRAME_INTERFACE_CHANGES.json.

The native shaft solid now occupies local Z2..275mm, rather than a simple6×260mm calculation cylinder. Assigned4340 and documented4130 remain a material conflict. The calculation baseline has not been silently changed.

The timing output/input plates are proposed7075-T6, with a relieved POM floating member weighing6.946g in native CAD. Four OD3 pilots in D3.02 pockets transmit torque; M2 screws provide axial clamping. The shaft input uses a D2 crosspin at local Z22.925mm and clock164.174614°. Native threads are major-diameter envelopes; production tap-drill diameters must follow drawings, not the CAD major envelopes.

COUPLING_GEOMETRIC_BOUNDS.json records nominal1.8mm tongue engagement,0.2mm face gaps, at least9.12mm longitudinal contact and2.12mm central clearance under the stated planar assumptions. The0.7mm output/head gap requires a tolerance/deflection budget. Nominal coupling play screens at approximately0.205°, before pilot/pin/bearing/guide contributions; this is much greater than the approximately0.009° nominal margin to35°. A literal loaded35° limit is unverified. The selected pitch law is not exactly sinusoidal, unlike the unchanged calculation model.

## Loads and mass limits

INERTIA_LOAD_SCREEN.json uses the baseline12.5g/blade and an assumed uniform distribution: peak rod force15.96N and ring reaction29.75N at2640RPM. The relieved floating-member centre-motion inertia is7.30N. These are analytical assumptions, not approved or measured operating loads; aerodynamic/imbalance/jam loads and actual inertia remain dependencies.

FRAME_SUPPORT_LOAD_UPDATE.json explicitly supersedes the earlier20N post study with a provisional50N screen. It predicts0.152mm deflection, a library-based static factor2.64 with assumed Kt2, and0.27mm remaining radial gap after the stated0.35mm adverse budget. The deflection allowance increased explicitly from0.15 to0.20mm. No fatigue, modal, rotor-critical-speed or structural certification is claimed.

The new bench cage and coupling substantially exceed the historical frame allocation. The complete module will exceed the old331.108g estimate. Historical endplates alone have approximately41099.9mm³ each despite18g target overrides. No mass override will be used to conceal this. CAD mass cannot establish measured hardware mass.

## Remaining physical/supplier holds

- Approved mechanical load cases, required service life and actual blade mass/inertia/COM.
- Blade manufacturing definition: CFRP skin/core/spar, steel trunnion attachment, laminate, bond process and qualification.
- Bearing fits/contact lands, oscillatory life, support alignment and running-clearance inspection.
- Joint insertion/pullout or positive-capture proof, adhesive tests, fastener preload/locking and arm fatigue.
- Servo/horn toleranced interface, continuous force/holding torque, thermal and dynamic response.
- Balance, vibration, guide play/runout and guarded low-speed-to-operating-speed physical validation.

CFD, aerodynamic performance and structural certification remain outside this implementation's verified scope. Their inputs may affect the mechanical load envelope; none is treated as satisfied.
