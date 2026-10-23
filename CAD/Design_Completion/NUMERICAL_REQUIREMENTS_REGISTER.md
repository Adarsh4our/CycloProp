# Powered bench prototype: numerical requirements, revision 0

23 October 2026. **Design study only. No fabrication, purchase or powered-test release.** Values marked proposed are engineering assumptions for review, not approved limits or demonstrated capacity. The user authorized continued design work and access; that does not establish material properties or test results.

The fixed design remains four NACA 0012 blades, radius 95 mm, span 220 mm, chord 38 mm, quarter-chord pivot and nominal ±35° cyclic pitch. The existing linkage is nonsinusoidal. The 2640 RPM point remains a qualification target. `config/baseline.json` is unchanged, SHA-256 `2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f`.

## Starting state and evidence

`STARTING_POINT_CHECKPOINT.json` identifies the disk archive, all source hashes, configuration, live transforms, references, suppression and separate copies of three dirty assemblies. `STARTING_RECOVERY_COMPARISON.json` compares the current live assembly with uniquely named read-only copies of the latest balloon-task recovery and the saved working assembly. Those two comparison copies have matching inspected poses and constraints. The current live pose differs from both; it is retained unchanged, with no attribution to a geometry edit. Disk sources are unchanged since the balloon task. No unknown live work was discarded.

The native inventory found Default configuration, 342 root components, 416 instances including 21 virtual bearing components, zero suppressed components, no unresolved active references and no reported active mate errors. Only the two construction angle holds are suppressed. XY advanced limits and the existing radial limit are active. These are inspection results, not a rebuild, solver-DOF check or motion proof. Current live axis offsets inferred from the limit mates are X +0.757161 mm, Y −2.295245 mm; eccentricity is about 2.417 mm.

Of 33 indexed drawing source identities, 32 match current disk model bytes; CP-RB-001 retains a historical assembly source identity. This does not certify manufacturing completeness. Historical static/motion checks retain their original source scope. The final motion and collision campaign remains outstanding.

## Correction to the historical load model

The previous `INERTIA_LOAD_SCREEN.json` included only `Jp × pitch acceleration`. For a blade whose centre of mass is aft of its quarter-chord pivot, the pivot itself accelerates around the rotor. Moment balance about that accelerating pivot also requires:

`M_required = Jp × beta_ddot + (m × r_COM) cross a_pivot`.

Here beta is the absolute blade angle. At constant rotor speed, its second time derivative equals the relative pitch second derivative. Native chord +X opposes the pitch-arm direction, as documented in `automation/check_coupling_drive.py`. With a chordwise aft COM offset d and the current tangent-based pitch convention, the added signed term is `m × d × R × omega² × cos(pitch)`. This is an inertial term, not an aerodynamic coefficient. It persists at centred XY with constant relative pitch.

The new calculation differentiates linkage closure analytically, resolves all four rod reactions and sums ring forces and ring torque. It uses five radial samples (0, 1.72, 3.44, 5.16, 6.88 mm), 24 XY directions away from centre, and 1440 rotor azimuths per position. Fine azimuth checks use 36000 and 72000 points at the historical +X critical setting. This is sampled rigid kinematics/load analysis, not continuous clearance or a complete dynamic model.

Under the **same historical assumptions** of 12.5 g, 9.5 mm aft COM offset and Jp 2.632292e−6 kg m², the correction produces:

| Quantity | New calculated result | Interpretation |
| --- | ---: | --- |
| Angular speed / frequency | 276.460 rad/s / 44 Hz | Target speed only |
| Centred orbital COM torque per blade | 0.862228 N m | Old J-only result at centre was zero |
| Peak combined inertia hinge torque | 0.887164 N m | Excludes aero, friction and distributed linkage inertia |
| Peak rod force | 87.4033 N | Historical J-only screen was 15.9595 N |
| Maximum absolute ring-axis force across sampled disk | 48.8845 N on either axis | Identical blades and correlated loads; not an independent-blade tolerance bound |
| Peak internal ring torque | 3.17019 N m | Must pass through timing hardware |
| Minimum rod moment arm | 9.60555 mm | Sampled nominal geometry |
| Ring-phase to blade-pitch gain | 1.37906 maximum absolute ratio | Apply before allocating timing clearance |

Ring torque is an **internal circulating torque**. Multiplying it by rotor speed does not give net motor demand: rotor/blade reactions can return power. Main-drive selection needs total kinetic-energy variation, aerodynamic shaft torque, losses and acceleration separately. The preliminary aerodynamic baseline cannot supply instantaneous hinge moments or certify drive sizing.

## Requirements and provisional bounding inputs

| ID | Value / definition | Evidence class and release condition |
| --- | --- | --- |
| GEO-01 | 4 blades; NACA 0012; R95, span220, chord38, pivot9.5 mm | Fixed user requirement. No calculation-baseline change. Native airfoil profile identity still needs manufacturing reconciliation. |
| SPD-01 | 2640 RPM / 44 Hz qualification target | Fixed target; not approved operating speed. |
| BLD-01 | Study cap m ≤20 g each, aft COM offset 0..10 mm, Jp ≤5e−6 kg m² | Proposed independent caps. Require final construction, individual mass/COM/inertia estimates and measurement. A negative/other-direction COM requires recalculation. |
| AER-01 | Relative airspeed ≤45 m/s, absolute resultant coefficient ≤2, absolute quarter-chord moment coefficient ≤0.30 | Proposed screening bounds only, not CFD results or established aerodynamic envelope. These imply 20.7380 N resultant and 0.118207 N m hinge moment per blade. Local pitch-motion velocity and inflow must fit the 45 m/s bound. |
| FRC-01 | Oscillatory bearing drag ≤0.002 N m per blade | Proposed aggregate for both blade supports; measure after assembly, cold/hot and after dwell. |
| FRC-02 | Guide breakaway ≤5 N each axis | Proposed. Includes supplied guide preload/retainer effects only after measurement. |
| OLD-01 | Oldham friction coefficient ≤0.15; 28 mm moment-arm scale; disk inertia reaction 7.305 N | Proposed contact model; disk mass 6.946 g from retained CAD. Sliding/contact force distribution, minimum lever, pressure, creep, PV, Coriolis terms and transients still require verification. |
| BAL-01 | Residual unbalance ≤5 g mm total, measured in two planes | Proposed commissioning limit; force scale 0.38215 N at target. Also check couple unbalance and component retention; this is not an equipment balance grade. |
| DUT-01 | ≤10 s each powered target-speed run; ≤600 s cumulative target-speed operation before teardown | Proposed short-run research duty. 600 s gives 26400 rotor cycles; not fatigue life qualification. Start/stop cycles counted separately. |
| TMP-01 | Ambient 15..30°C; component stop at 45°C absolute or 15°C rise, whichever first | Proposed instrumentation stop rule. A lower supplier/material limit governs. Cool to within 5°C of initial ambient before restart; temperature alone does not demonstrate lubricant/adhesive suitability. |
| PCH-01 | Maximum-eccentricity positive and negative pitch peaks: +35°±1° and −35°±1° | Proposed loaded tolerance. 35° is nominal, not an absolute maximum. At other eccentricities, compare measured pitch with the nominal mechanism curve within ±1°, not with an exact sine wave. |
| CLR-01 | Rotor/frame minimum loaded clearance ≥3.5 mm | Retained documented minimum. Inspect with all tolerances, vibration, runout, deflection and retention hardware included. |
| CLR-02 | Centre-post and coupling/fastener loaded gaps remain positive; proposed minimum 0.25 mm | Proposed. Earlier 50 N pedestal screen cannot substantiate the new load study. Recalculate before release. |
| AXI-01 | Proposed operating total blade endfloat 0.15..0.45 mm | Still provisional. Select shims after measuring stack; thermal/load/wear allocation below must be justified. |
| PRF-01 | 1.5× final approved operating load, static 10 s, each load direction | Proposed proof procedure for retained parts/joints only after analytical checks and fixture definition. No yield, slip, pullout, loosening or measurable permanent change. Does not establish fatigue or impact survival. |
| LIFE-01 | Witness joints: ≥100000 representative loaded pitch cycles, including temperature/articulation extremes | Proposed development test, longer than declared bench operating cycle count. Sample count and acceptance scatter remain external test-plan inputs. No service-life claim. |
| STP-01 | No intentional full-speed hard-jam test | Stored rotational energy needs containment/retention analysis. Controller current limit or motor torque limiter alone does not bound a jam. |

`MECHANICAL_LOAD_ENVELOPE.json` preserves input scenarios and sampled results. With the independent BLD-01 caps, triangle bounds on the included blade terms and the proposed aerodynamic/friction inputs give approximately **164.09 N rod load, 1.8722 N m hinge torque, 6.4846 N m ring torque, 509.63 N per carriage axis and 6.167 N m at the existing R12 horn**. These deliberately permit independent blade mass moments; they are broader than the matched-blade case. They are **not final requirements**: geometry sampling, unverified contact assumptions and omitted distributed linkage/command loads remain. Do not buy an actuator solely from these values or equate catalog stall torque with continuous/44 Hz holding capacity.

With a provisional total rotor inertia of 0.002 kg m², stored energy is 76.43 J at 2640 RPM. Average inertial stop torque is 1.106 N m over 0.5 s, versus 552.92 N m over 1 ms. Neither value bounds local impact force or a rebound. Actual inertia, stop dynamics, fragment energy, fixture anchorage and containment remain required inputs.

## Pitch-error allocation

Proposed arithmetic worst-direction allocation, in blade-angle degrees. Each limit includes tolerance, reversal and temperature effects attributable to that interface; no root-sum-square credit is taken.

| Contribution | Allocation | First-order dimensional consequence |
| --- | ---: | --- |
| Nominal calibration / geometric approximation | 0.02° | Nominal sampled peak error is about 0.011°; sample refinement/calibration still needed. |
| Oldham phase, pins and attachment play | 0.25° | At gain1.37906, ring-phase play ≤0.1813°. Existing 0.20463° coupling play screen alone maps to about0.2822° blade error and exceeds this allocation. |
| Two ball joints per rod, including mounting play | 0.20° | Combined effective rod-direction lost motion ≤0.03353 mm using9.60555 mm minimum moment arm. Existing two D5/D5.05 joint clearances can contribute up to0.10 mm reversal travel before mounting play; not accepted. |
| Assembled rod centre distance and thermal growth | 0.20° | Effective length error ≤0.03353 mm; allocation must include tube/bond/ball-centre stack. |
| Guide translation and bearing location | 0.10° | Allowed effective endpoint displacement ≤0.01676 mm in the adverse direction; actual mapping must use the XY Jacobian. |
| Elastic deflection of blade/trunnion/arm/rod/frame | 0.15° | Requires final-load compliance calculation and loaded measurement. |
| Residual thermal / wear drift beyond explicit interface budgets | 0.05° | Requires measured running temperatures and wear. |
| Measurement uncertainty | 0.03° | Required uncertainty of the assembled angle measurement, not just encoder resolution. |
| **Total** | **1.00°** | Proposed acceptance; not released tolerances. |

The existing 0.1 mm Oldham width difference must not be simply divided by the number of interfaces: preserve separate phase, axial and wear budgets. A reduced width difference could be studied, but supplier process capability, lubricant film, thermal growth and sliding freedom must be established before a fit is released. No CAD clearance was tightened in this step.

## Endfloat and supplier fits

An example **allocation to investigate**, not an approved stack: target measured ambient endfloat0.300 mm, acceptable0.280..0.320; uncertainty0.005, differential thermal change0.100, loaded axial change0.020, wear/set0.005 mm. Arithmetic extremes are0.150..0.450 mm. This leaves no unallocated reserve. Validate the actual structural temperature/CTE paths and measurement method; otherwise widen the operating window or redesign the retention stack. Selectable shims must act on the intended ring/contact lands, never bearing shields. Do not fabricate the provisional shaft/shoulder stack from this example.

The [SMB F693ZZ drawing](https://www.smbbearings.com/firebrick/ckeditor/plugins/upload/Uploads/Documents/bearingpdfs/F693ZZ-flanged-miniature-bearing-3x8x4mm.pdf) confirms nominal3×8×4, flange9.5×0.9 and P0 bore/OD deviation+0/−0.008 mm, width+0/−0.120 mm. Thus a nominal D3 shaft described only as h7/0..−0.010 can range from0.008 mm interference to0.010 mm clearance against that bore. It is not a defined clearance fit. Confirm the selected grade/clearance and fits with the supplier before grinding journals or machining housings. The same drawing's static rating is176.52 N; no oscillatory-life approval follows.

The [EZO F693ZZ table](https://www.ezo-brg.co.jp/english/product/spec.php?eid=00229) lists a3.9..4.3 mm inner-ring abutment diameter and0.15 mm maximum fillet radius. This supports investigating the existing OD4 spacer **only if that exact bearing is selected**. It does not transfer EZO load ratings/contact details to an unidentified SMB-supplied bearing. Outer-ring cap/shoulder contact land and shield relief still need the actual supplier section/drawing.

## Release-critical open inputs and consequences

1. Define the actual blade skin/core/spar and metal trunnion load path; determine mass, first mass moment about the pivot, Jp and component temperatures. Native Part1 is a single material/connected-solid proxy with an internal-cut feature and geometric volume4838.47 mm³. It must not be described as a filled solid airfoil or accepted as a laminate definition. Its geometric COM is X17.85474 mm, versus pivotX9.5; applying a uniform density to it would still leave an8.35474 mm aft COM offset. No measured blade inertia exists.
2. Obtain aerodynamic hinge/resultant bounds, inflow assumptions and transient factors or approve explicit conservative bounds. The proposed45 m/s / coefficient values above are not validated CFD. Structural certification remains outside scope.
3. Include the real arms, rods, sockets, bearing friction and moving Oldham dynamics, and specify commanded XY speed/acceleration. Recompute both actuator axes over actual allowed travel. Supplier torque-speed, continuous holding, thermal duty, backlash, current, horn/spline and retention interfaces remain unselected.
4. Reopen the earlier arm/pin/bond/bearing and centre-post strength screens. The old16 N rod screen and50 N post case are insufficient evidence for the corrected model. At the broad proposed hinge bound, an equivalent torque force at1.5 mm pin radius is about1248 N, already above the historical600 N supplier pin shear figure even before proof/fatigue. Do not infer that every actual blade design fails: narrow the mass-moment envelope or revise the load path, then verify.
5. Resolve the shaft definition (calculationD6×260; original CADD6×275 with2 mm nose removal; CAD4340 normalized versus specification4130). Retain the calculation inputs and document an independently selected manufactured shaft, including holes/grooves/fillets and fatigue checks.
6. Identify the supplied guide rail/block suffix, allowable load/moment and screw insertion depths; current approximately1 mm engagements are unqualified. Close G10 edge/clamp limits, socket cap locking, lubrication and qualified bond processes.
7. Define drive hardware and instrumented fixture/guard from measured/estimated final rotor inertia and torque. Select documented components before making a priced purchase list. No purchase is authorized or implied by this register.

Fabrication approval requires closed component definitions, tolerances and proof plans. Powered-test approval additionally requires supplied-part inspection, retained/bonded joint evidence, actuator duty qualification, balance, containment and explicit approved limits. None has been satisfied by the calculations above.

## Verification performed

`python CAD/Design_Completion/automation/mechanical_load_envelope.py` checks analytic linkage acceleration against periodic finite differences (maximum difference2.91e−7 in radians per azimuth-radian squared), reproduces the historical J-only rod force15.959495 N, verifies the centred orbital torque analytically, checks RPM-squared scaling, closure and sampled branch continuity, and compares36000/72000-point azimuth rod peaks (difference2.43e−8 N). These checks validate implementation consistency; they do not validate physical loads. No native rebuild/motion/continuous-clearance check or physical test was performed in this checkpoint.
