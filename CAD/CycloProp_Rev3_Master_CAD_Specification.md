> **Mass correction, 20 October 2026:** The solid steel shaft mass allocation is corrected below. The current preliminary module estimate is 331.108 g. CAD binary mass, interfaces and clearance remain unverified; reconcile these against `config/baseline.json` before production drawing release.

# CycloProp Rev 3.0 — Master CAD Assembly Design Specification
**Indigenous 360° Thrust-Vectoring Cycloidal Rotor Propulsion Module**  
*PUSHPAK Grand Challenge 2026 — MeitY & IIT Bombay Aerospace*

---

## 1. Global System Parameters & Master Equations

All dimensional relationships must be driven by equations linked to a primary skeleton part: `00_Master_Skeleton.SLDPRT`.

| Parameter Symbol | Equation / Nominal Value | Description |
| :--- | :--- | :--- |
| `R_ROTOR` | `95.00 mm` | Rotor Pitch Radius (trunnion pivot axis to central rotation axis) |
| `B_SPAN` | `220.00 mm` | Aerodynamic blade span (between inner faces of hub endplates) |
| `C_CHORD` | `38.00 mm` | Blade chord length (NACA 0012 profile) |
| `N_BLADES` | `4` | Number of rotor blades (spaced at exact 90.0° intervals) |
| `D_SHAFT` | `6.00 mm` (h7: -0.000 / -0.012) | Central drive shaft diameter (4130 Chromoly) |
| `L_SHAFT` | `260.00 mm` | Total central drive shaft length |
| `GAP_TIP` | `3.50 mm` | Nominal running air gap between blade tips and stationary frame pillars |
| `THETA_MAX` | `35.0 deg` | Maximum cyclic pitch amplitude |
| `E_MAX` | `6.88 mm` | Maximum eccentric carriage stroke travel from central axis |
| `SPAR_LOC` | `0.25 * C_CHORD` (`9.50 mm`) | Blade pitch trunnion axis location from aerodynamic leading edge |
| `HORN_RADIUS`| `12.00 mm` | Blade pitch arm effective moment arm (pivot axis to ball stud center) |

---

## 2. Top-Down Master Skeleton (`00_Master_Skeleton.SLDPRT`)

Create this file first. Insert no solid bodies; create only reference planes, axes, coordinate systems, and 2D/3D layout sketches.

### Reference Planes & Coordinate System
1. **Front Plane:** Mid-span symmetry plane ($Z = 0$).
2. **Top Plane:** Horizontal reference plane ($Y = 0$).
3. **Right Plane:** Central rotation axis ($X = 0$).
4. **Plane_DriveEnd:** Offset from Front Plane by $+110.00\text{ mm}$ ($+B\_SPAN / 2$).
5. **Plane_MechEnd:** Offset from Front Plane by $-110.00\text{ mm}$ ($-B\_SPAN / 2$).
6. **Plane_MotorMount:** Offset from `Plane_DriveEnd` by $+25.00\text{ mm}$ (motor interface).
7. **Plane_CarriageMount:** Offset from `Plane_MechEnd` by $-20.00\text{ mm}$ (servo carriage interface).

### Master Sketches
* **Sketch_RotorCircle (Right Plane):**
  * Center on Origin $(0,0)$.
  * Construction circle diameter $\varnothing 190.00\text{ mm}$ ($2 \times R\_ROTOR$).
  * 4 radial construction lines at $0^\circ, 90^\circ, 180^\circ, 270^\circ$.
  * Endpoints define trunnion pivot axes: `Point_Blade_1` through `Point_Blade_4`.
* **Sketch_KinematicEccentricity (Plane_MechEnd):**
  * Movable control point $(e_x, e_y)$ bounded inside circle of radius $E\_MAX = 6.88\text{ mm}$.
  * Control circle $\varnothing 30.00\text{ mm}$ centered on $(e_x, e_y)$ (represents outer ring bearing race).
  * 4 pushrod linkage lines of fixed length $L_{pushrod}$ connecting ring periphery to blade pitch horn points.
* **Sketch_ChassisEnvelope (Right Plane):**
  * Rectangle centered on Origin: Length $= 271.50\text{ mm}$ (X), Height $= 263.50\text{ mm}$ (Y).
  * 4 standoff pillar location points at the corners with $GAP\_TIP \ge 3.50\text{ mm}$ clearance envelope.

---

## 3. Detailed Part-by-Part Modeling Guide

### Part 01: `01_Rotor_Blade_NACA0012.SLDPRT`
* **Material:** CFRP Skin ($1.55\text{ g/cm}^3$) over XPS Foam Core ($0.035\text{ g/cm}^3$). Target Mass: **12.5 g** per blade.
* **Loft / Extrusion:**
  * Import NACA 0012 coordinate curve points (100+ points) scaled to $C\_CHORD = 38.00\text{ mm}$.
  * Extrude symmetrical mid-plane along span: $B\_SPAN = 220.00\text{ mm}$ (from $-110\text{ mm}$ to $+110\text{ mm}$).
* **Through-Spar Bore:**
  * Cylindrical bore $\varnothing 4.00\text{ mm}$ centered at $X = 9.50\text{ mm}$ (25% chord) and $Y = 0.00\text{ mm}$ (chord line) across the full $220.00\text{ mm}$ span.
* **Spar & Trunnion Stubs:**
  * Insert $\varnothing 4.00\text{ mm}$ UD carbon spar tube.
  * At both ends, insert stepped titanium/steel trunnion pins: $\varnothing 4.00\text{ mm}$ base shank bonded $25\text{ mm}$ deep into carbon tube, stepping down to ground $\varnothing 3.00\text{ mm}$ (h7: -0.000 / -0.010 mm) journal pin protruding $12.00\text{ mm}$ outward.
  * Pitch-mechanism end pin includes an anti-rotation flat ($0.5\text{ mm}$ flat depth, $6\text{ mm}$ length) to mate with the pitch horn clamp.

---

### Part 02: `02_Hub_Endplate.SLDPRT` (Qty: 2)
* **Material:** G10 FR4 Epoxy Glass Sheet ($1.85\text{ g/cm}^3$), thickness $= 1.50\text{ mm}$. Target Mass: **18.0 g** each.
* **Main Disc Profile:**
  * Circular plate $\varnothing 206.00\text{ mm}$ ($R = 103.00\text{ mm}$, providing $8\text{ mm}$ perimeter flange past blade trunnion centers).
  * Weight-reduction cutouts: 4 large triangular pockets with $3.00\text{ mm}$ structural web spokes between center hub and trunnion bosses.
* **Center Bore & Hub Mounting:**
  * Center pilot bore $\varnothing 14.00\text{ mm}$ (clears central shaft hub step).
  * 4-bolt M2.5 mounting pattern on PCD $\varnothing 22.00\text{ mm}$ for aluminum shaft drive flange.
* **Trunnion Bushing Pockets (4x on PCD $\varnothing 190.00\text{ mm}$):**
  * Counterbore to receive Igus Iglide J `JFM-0306-04`:
    * Through hole: $\varnothing 6.00\text{ mm}$ (+0.02 / +0.00 mm, H7 press-fit for bushing OD).
    * Outer counterbore: $\varnothing 8.00\text{ mm} \times 1.00\text{ mm}$ depth (seats the $1.0\text{ mm}$ thick bushing flange flush).

---

### Part 03: `03_Shaft_Drive_Hub_Adapter.SLDPRT` (Qty: 2)
* **Material:** 7075-T6 Aerospace Aluminum ($2.81\text{ g/cm}^3$).
* **Features:**
  * Cylindrical collar: OD $= 28.00\text{ mm}$, length $= 14.00\text{ mm}$.
  * Precision shaft bore: $\varnothing 6.00\text{ mm}$ (+0.012 / +0.000 mm, H7 slide fit over drive shaft).
  * Flange: $\varnothing 28.00\text{ mm} \times 3.00\text{ mm}$ with 4 threaded M2.5 holes on PCD $\varnothing 22.00\text{ mm}$.
  * Cross-pin hole: Reamed $\varnothing 2.00\text{ mm}$ hole through diameter for DIN 1481 hardened roll pin.

---

### Part 04: `04_Central_Drive_Shaft.SLDPRT`
* **Material:** 4130 Chromoly Alloy Steel ($7.85\text{ g/cm}^3$). Gross solid-stock calculated mass: **57.708 g** before machining; verify final material and volume in CAD.
* **Dimensions:**
  * Ground precision rod $\varnothing 6.00\text{ mm}$ (h7 tolerance), overall length $= 260.00\text{ mm}$.
  * Two cross-drilled $\varnothing 2.00\text{ mm}$ holes spaced at $Z = \pm 110.00\text{ mm}$ for hub roll pins.
  * Circlip retaining grooves: DIN 471 $\varnothing 5.70\text{ mm} \times 0.80\text{ mm}$ wide adjacent to main bearing locations.
  * Drive-end key flat / D-cut: length $= 12.00\text{ mm}$, depth $= 0.50\text{ mm}$ for Oldham jaw coupler clamp.

---

### Part 05: `05_Blade_Pitch_Horn.SLDPRT` (Qty: 4)
* **Material:** SLS PA12 Nylon / 7075-T6 CNC. Target Mass: **1.8 g** each.
* **Features:**
  * Clamping boss: Bore $\varnothing 3.00\text{ mm}$ with $0.8\text{ mm}$ slit and M2 pinch screw clamping onto trunnion D-flat.
  * Lever arm: Offset length $= 12.00\text{ mm}$ from trunnion axis to ball stud axis.
  * Ball stud mounting: M2 threaded hole to mount precision brass ball link stud.

---

### Part 06: `06_2DOF_Pitch_Carriage_Mechanism` (Sub-Assembly)
1. **Inner X-Carriage Plate (7075-T6 CNC Al, 6.0 g):**
   * Guided along precision dual miniature steel rails ($\varnothing 3.00\text{ mm}$) oriented along X-axis.
   * Driven by Servo 1 via a zero-backlash linkage slot.
2. **Outer Y-Carriage Carrier:**
   * Slips within the X-carriage on orthogonal rails oriented along Y-axis, actuated by Servo 2.
   * Total allowable XY excursion: bounded within a circle of radius $e = 6.88\text{ mm}$.
3. **Eccentric Control Ring (`07_Control_Ring.SLDPRT`):**
   * Houses thin-section 6802 bearing (ID $15\text{ mm}$, OD $24\text{ mm}$, width $5\text{ mm}$).
   * Rotating outer housing features 4 perimeter clevis ears spaced at $90^\circ$ with M2 ball-joint pivots.
4. **Pushrods (4x):**
   * $\varnothing 2.00\text{ mm}$ pultruded carbon fiber tube ($L \approx 45.00\text{ mm}$) with threaded brass M2 ball-link ends.

---

### Part 07: `07_Chassis_Cage_and_Fairings.SLDPRT`
* **Structural Frame:**
  * Motor-side end bulkhead and mechanism-side end bulkhead waterjet from $2.00\text{ mm}$ G10 plate.
  * 4 structural corner tie-rods: $\varnothing 6.00\text{ mm}$ aluminum standoffs tapped M3 on both ends, length $= 230.00\text{ mm}$.
* **Teardrop Aerodynamic Fairing Sleeves (4x):**
  * 3D-printed PETG ($1.27\text{ g/cm}^3$), wall thickness $= 1.20\text{ mm}$.
  * Profile: NACA 0025 teardrop section ($t/c = 0.25$), chord $= 32.00\text{ mm}$, max thickness $= 8.00\text{ mm}$.
  * Internal snap-on cavity clips securely over the structural $\varnothing 6.00\text{ mm}$ standoff tie-rods.
  * Total fairing set mass: **12.0 g**.

---

## 4. SolidWorks Assembly Mating Chain (`CycloProp_Rev3.SLDASM`)

Follow this exact order of operations to prevent circular mate loops or over-constrained DOF errors:

```
[Master Skeleton] (Fixed at Origin)
   │
   ├──► [Central Drive Shaft] : Coincident Axis (Z) + Plane Symmetry
   │       │
   │       ├──► [Shaft Hub Adapters (2x)] : Concentric + Roll-Pin Alignment
   │       │       │
   │       │       └──► [Hub Endplates (2x)] : Coincident Face + PCD Bolt Alignment
   │       │               │
   │       │               └──► [Igus Bushings (8x)] : Concentric + Flange Flush
   │       │                       │
   │       │                       └──► [Rotor Blades (4x)] : Concentric (Pin-to-Bushing)
   │       │
   ├──► [Stationary Chassis Cage] : Mated to Skeleton Reference Planes
   │       │
   │       ├──► [T-Motor MN3508] : Flange Mated + 4x M3 Bolts
   │       │       │
   │       │       └──► [Jaw Coupler] : Mated to Motor Shaft & Central Shaft
   │       │
   │       └──► [KST X08 Servos (2x)] : Fastened to Mech-Side Bulkhead
   │               │
   │               └──► [2-DOF Carriage] : Linear Guide Mates along X and Y
   │                       │
   │                       └──► [Control Ring + 6802 Bearing]
   │                               │
   │                               └──► [4x Pushrods] : Ball-Joint Spherical Mates
   │                                       │
   │                                       └──► [Blade Pitch Horns] (Pinned to Blade Trunnions)
```

### Critical Mating Rules
1. **Blade Rotation:** Blades must have only **1 rotational degree of freedom** relative to the hub endplate (rotation about the trunnion axis). Restrict axial travel using bushing flange coincident mates.
2. **Pushrod Linkages:** Mate each pushrod using **Concentric (Spherical Center to Spherical Center)** mates at both ball studs. Allow the pushrod body to rotate about its own long axis (3-DOF ball joint behavior) to prevent binding.
3. **Eccentric Ring:** The inner race of the 6802 bearing is locked to the non-rotating 2-DOF carriage. The outer race is free to rotate with the rotor assembly, driven by the 4 pushrods.

---

## 5. Verification & Audit Checklist

Before exporting drawings or STEP packages for submission:

- [ ] **Running Air Gap Audit:** Run `Tools > Evaluate > Clearance Verification` between all 4 blade tips and the 4 teardrop frame fairings across a full $360^\circ$ rotation. Minimum clearance must be $\ge 3.50\text{ mm}$ everywhere.
- [ ] **Pitch Swing Angle Audit:** Displace carriage to $E\_MAX = 6.88\text{ mm}$. Rotate rotor through $360^\circ$ in SolidWorks Motion. Measure pitch angle $\theta(t)$ on each blade—confirm peak amplitude reaches exactly $\pm 35.0^\circ$ without linkage inversion or toggle lock.
- [ ] **Mass Budget Check:** Run `Tools > Evaluate > Mass Properties`. Ensure all materials are assigned correctly (CFRP, G10, 7075-T6, 4130 steel, PETG). Total assembly mass must not exceed **301.4 g** ($\pm 5.0\text{ g}$).
- [ ] **Fastener Head Interference:** Verify all M2/M2.5/M3 socket head cap screws have proper counterbores and do not foul on rotating hub spokes.
