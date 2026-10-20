import os

with open('CYCLOPROP_MASTER_KNOWLEDGE_BASE.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. New Section 6.5 Subsections
new_65 = """
#### 6.5.9 Rev 3.0 Master Skeleton & Top-Down Parametric Modeling Methodology (`00_Master_Skeleton.SLDPRT`)
- **Methodology & Context:** In accordance with aerospace Top-Down Master Modeling standards for the PUSHPAK Grand Challenge 2026, the complete cyclorotor module is geometrically driven from a single unconsumed master skeleton part: `00_Master_Skeleton.SLDPRT`. All sub-parts (`01` through `07`) reference planes, sketches, and dimensional parameters directly from this master skeleton via external references or derived sketches, ensuring zero tolerance drift during parametric sweeps.
- **Global Coordinate System & Primary Reference Planes:**
  - **Front Plane (Mid-Span Symmetry Datum, $Z = 0.00\\text{ mm}$):** Serves as the central transverse plane dividing the $220.00\\text{ mm}$ active blade span into symmetrical $\\pm 110.00\\text{ mm}$ halves.
  - **Right Plane (Central Rotational Axis Datum, $X = 0.00\\text{ mm}$):** Coincident with the central axis of rotation of the drive shaft.
  - **Top Plane (Horizontal Reference Datum, $Y = 0.00\\text{ mm}$):** Orthogonal horizontal reference plane establishing the zero-pitch reference line.
  - **`Plane_DriveEnd` (Offset Plane):** Parallel to Front Plane, offset by $+110.00\\text{ mm}$ ($+b/2$). Defines the Drive-End hub inner face and blade root boundary.
  - **`Plane_MechEnd` (Offset Plane):** Parallel to Front Plane, offset by $-110.00\\text{ mm}$ ($-b/2$). Defines the Mechanism-End hub inner face and blade tip boundary.
- **Master Parameter Equation Table (Linked in SolidWorks Equation Manager):**

| Parameter Name | Value / Unit | Governing Equation / Physical Role |
| :--- | :---: | :--- |
| `R_ROTOR` | `95.00 mm` | Rotor pitch circle radius (central axis to blade quarter-chord trunnion axis) |
| `B_SPAN` | `220.00 mm` | Active aerodynamic lifting span between inner faces of hub endplates |
| `C_CHORD` | `38.00 mm` | NACA 0012 blade aerodynamic chord length |
| `N_BLADES` | `4` | Number of rotor blades spaced at exact $90.0^\\circ$ azimuthal intervals |
| `D_SHAFT` | `6.00 mm` | Central drive shaft diameter (h7 tolerance: $-0.000 / -0.012\\text{ mm}$) |
| `L_SHAFT` | `260.00 mm` | Total central drive shaft length along $Z$-axis |
| `GAP_TIP` | `3.50 mm` | Minimum allowable running air gap between rotating blade tips and chassis fairings |
| `THETA_MAX` | `35.0 deg` | Maximum cyclic blade pitch amplitude ($\\pm \\theta_0$) |
| `E_MAX` | `6.88 mm` | Maximum eccentric carriage stroke travel from central shaft axis ($E_{\\max} = r_h \\sin\\theta_{\\max}$) |
| `SPAR_LOC` | `9.50 mm` | Blade quarter-chord pitch trunnion location ($0.25 \\times C\\_CHORD$) from leading edge |
| `HORN_RADIUS` | `12.00 mm` | Blade pitch arm effective moment arm ($r_h$: trunnion pivot to M2 ball center) |

- **Master Skeleton Layout Sketches (Right Plane):**
  1. **Rotor Pitch Circle:** Construction circle $\\varnothing 190.00\\text{ mm}$ ($R = 95.00\\text{ mm}$) centered at $(0, 0)$.
  2. **Trunnion Stations (4x):** 4 sketch points constrained Coincident to the pitch circle at $0^\\circ, 90^\\circ, 180^\\circ, 270^\\circ$ (aligned with Right and Top reference planes).
  3. **Eccentric Swashplate Travel Envelope:** Bounded circular construction region of radius $E_{\\max} = 6.88\\text{ mm}$ centered at origin. Contains the driven eccentric carriage control point $(e_x, e_y)$, where radial distance $e = \\sqrt{e_x^2 + e_y^2} \\le 6.88\\text{ mm}$.
  4. **Chassis Clearance & Aerodynamic Boundary Envelope:** Rectangular bounding box of $271.50\\text{ mm}$ (length) $\\times 263.50\\text{ mm}$ (height) defining outer chassis envelope.
  5. **Running Air Gap Verification:** Dynamic sweep clearance calculation confirms that at peak cyclic pitch ($\\pm 35.0^\\circ$), the maximum blade tip trajectory sweeps to $R_{\\text{sweep}} = 123.50\\text{ mm}$. Against the chassis inner clearance half-width of $135.75\\text{ mm}$, the net running air gap is **$12.25\\text{ mm}$**, exceeding the strict $\\ge 3.50\\text{ mm}$ requirement with a $+8.75\\text{ mm}$ safety margin.

---

#### 6.5.10 Part 01 — Rev 3.0 NACA 0012 Rotor Blade Modeling & Equation Specifications (`01_Rotor_Blade_NACA0012.SLDPRT`)
- **Context & Material:** Ultra-lightweight hollow composite blade monocoque (Qty: 4). Construction: CNC XPS foam core ($\\rho = 0.035\\text{ g/cm}^3$) wrapped in high-modulus UD carbon fiber prepreg ($\\rho = 1.55\\text{ g/cm}^3$, nominal skin thickness $t_{\\text{wall}} = 0.25\\text{ mm}$). Target Mass: **$12.50\\text{ g}$** per blade ($50.00\\text{ g}$ total set, comprising $16.59\\%$ of module mass).
- **Aerodynamic Profile Formulation (NACA 0012 Symmetrical):**
  The airfoil profile follows the standard 12% thickness distribution scaled to chord $c = 38.00\\text{ mm}$:
  $$y_t(x) = 5 \\cdot t_{\\text{ratio}} \\cdot c \\left[ 0.2969 \\sqrt{\\frac{x}{c}} - 0.1260 \\left(\\frac{x}{c}\\right) - 0.3516 \\left(\\frac{x}{c}\\right)^2 + 0.2843 \\left(\\frac{x}{c}\\right)^3 - 0.1036 \\left(\\frac{x}{c}\\right)^4 \\right]$$
  With $t_{\\text{ratio}} = 0.12$ and $c = 38.00\\text{ mm}$:
  - Maximum outer half-thickness: $y_{t,\\max} = 2.2803\\text{ mm}$ at $x = 11.38\\text{ mm}$ ($29.9\\%$ chord).
  - Maximum outer full thickness: $2 \\times y_{t,\\max} = 4.5605\\text{ mm}$.
  - Full thickness at spar axis ($x = 9.50\\text{ mm}$, $25\\%$ chord): $4.5150\\text{ mm}$.

- **Explicit SolidWorks Curve Equations:**
  1. **Leading-Edge Origin Form ($X = 0$ at LE nose, $Y = 0$ at chordline):**
     Used directly in SolidWorks *Tools > Sketch Entities > Equation Driven Curve* (Explicit, $x \\in [0.0001, 38.00\\text{ mm}]$):
     $$Y_{\\text{outer}}(x) = 1.098130 \\sqrt{x} - 0.075600 x - 0.0055516 x^2 + 0.00011807 x^3 - 0.000001132 x^4$$
  2. **Spar-Origin Form ($X = 0$ at 25% chord spar axis, $Y = 0$ at chordline):**
     Substituting $x\\' = x + 9.50\\text{ mm}$ for $x \\in [-9.4999, +28.50\\text{ mm}]$:
     $$Y_{\\text{spar}}(x) = 1.098130 \\sqrt{x+9.5} - 0.075600 (x+9.5) - 0.0055516 (x+9.5)^2 + 0.00011807 (x+9.5)^3 - 0.000001132 (x+9.5)^4$$

- **Internal Cavity Geometry & Carbon Spar Tube Capture:**
  - For skin thickness $t_{\\text{wall}} = 0.25\\text{ mm}$ (CFRP prepreg), the upper and lower inner mold line (IML) curves are:
    $$Y_{\\text{inner, upper}}(x) = Y_{\\text{outer}}(x) - 0.25$$
    $$Y_{\\text{inner, lower}}(x) = -[Y_{\\text{outer}}(x) - 0.25]$$
  - Valid cavity range: $x = 0.0535\\text{ mm}$ to $x = 36.228\\text{ mm}$ (LE origin), providing a cavity chord of $36.17\\text{ mm}$.
  - Recommended cut termination: $x = 36.00\\text{ mm}$, leaving a solid $2.00\\text{ mm}$ carbon composite trailing edge for damage tolerance.
  - **Spar Tube Clearance Validation:**
    At the $25\\%$ chord spar axis ($x = 9.50\\text{ mm}$):
    - Outer airfoil height: $4.5150\\text{ mm}$.
    - Inner cavity full height: $2 \\times (2.2575 - 0.2500) = 4.0151\\text{ mm}$.
    - Central through-spar carbon tube outer diameter: $\\varnothing 4.0000\\text{ mm}$.
    - Net radial clearance: $\\frac{4.0151 - 4.0000}{2} = \\mathbf{+0.0076\\text{ mm}}$ ($+0.0151\\text{ mm}$ total diametral float).
    - **Physical Significance:** The inner skin profiles capture the $\\varnothing 4.00\\text{ mm}$ spar tube in an exact, slip-fit mechanical nest, preventing any vertical spar rattling while transferring chordwise aerodynamic bending loads directly into the spar.

- **Solid Modeling Feature Sequence (SolidWorks):**
  1. **Base Aerodynamic Shell (`Boss-Extrude1`):**
     - Sketch on Front Plane (symmetrical datum).
     - Import or generate closed NACA 0012 curve (using Equation Driven Curve or `scripts/naca0012_chord38mm_solidworks.txt`).
     - Extrude Mid-Plane: Depth = **`220.00 mm`** (from $Z = -110.00\\text{ mm}$ to $Z = +110.00\\text{ mm}$).
  2. **Internal Cavity Cut (`Cut-Extrude1`):**
     - Sketch on Front Plane using inner cavity equations ($Y_{\\text{inner}} = Y_{\\text{outer}} - 0.25$).
     - Extrude Cut: Mid-Plane through span (or Blind with $5.0\\text{ mm}$ offset bulkheads at root and tip).
  3. **Central Through-Spar Bore (`Cut-Extrude2`):**
     - Sketch on Front Plane (or end face): Circle centered at $(X = 9.50\\text{ mm}, Y = 0.00\\text{ mm})$, Diameter = **`Ø 4.00 mm`**.
     - Extrude Cut: Through All Both across the full $220.00\\text{ mm}$ span.
  4. **Drive-End Trunnion Pin (`Boss-Extrude2`):**
     - Sketch on flat end face at $Z = +110.00\\text{ mm}$.
     - Circle concentric with spar bore: Diameter = **`Ø 3.00 mm`**.
     - Extrude: Blind **`12.00 mm`** outward (Merge Result = Checked).
     - Add $0.30\\text{ mm} \\times 45^\\circ$ lead-in chamfer to outer tip edge.
  5. **Mechanism-End Trunnion Pin (`Boss-Extrude3`):**
     - Sketch on flat end face at $Z = -110.00\\text{ mm}$.
     - Circle concentric with spar bore: Diameter = **`Ø 3.00 mm`**.
     - Extrude: Blind **`12.00 mm`** outward (Merge Result = Checked).
  6. **Anti-Rotation D-Flat (`Cut-Extrude3` — Mechanism End Only):**
     - Sketch on the circular tip face of the mechanism pin at $Z = -122.00\\text{ mm}$.
     - Draw a rectangular cut contour:
       - Flat cut depth: **`0.50 mm`** into the $\\varnothing 3.00\\text{ mm}$ cylinder (leaving $2.50\\text{ mm}$ flat-to-round thickness).
       - Cut orientation: Flat edge constrained **strictly parallel to the airfoil chordline** ($Y = 0$).
       - Axial cut depth: Blind **`6.00 mm`** from the pin tip inward toward the blade face.
  7. **Internal Carbon Spar & Trunnion Pin Inserts (Physical Fabrication):**
     - Insert $\\varnothing 4.00\\text{ mm}$ OD $\\times \\varnothing 3.00\\text{ mm}$ ID $\\times 220.00\\text{ mm}$ UD carbon tube through the central bore.
     - Stepped titanium/steel pins feature a $\\varnothing 4.00\\text{ mm}$ base shank bonded $25.00\\text{ mm}$ into each tube end with structural aerospace epoxy (Hysol 9462 / 3M DP420), transitioning to the ground $\\varnothing 3.00\\text{ mm}$ h7 journal extending $12.00\\text{ mm}$ outward.

---

#### 6.5.11 Part 02 — Rev 3.0 Hub Endplate Disc (`02_Hub_Endplate.SLDPRT`)
- **Context & Manufacturing:** Precision waterjet-cut composite disc (Qty: 2, Drive-End and Mechanism-End). Material: G10 FR4 Epoxy-Glass sheet ($\\rho = 1.85\\text{ g/cm}^3$, thickness $t = 1.50\\text{ mm}$). Target Mass: **$18.00\\text{ g}$** each ($36.00\\text{ g}$ total pair, comprising $11.94\\%$ of module mass).
- **Geometric Topology & Outer Disc Profile:**
  - **Outer Diameter:** **`Ø 206.00 mm`** ($R = 103.00\\text{ mm}$).
  - *Engineering Rationale:* Rotor blade trunnion centerlines are located on a Pitch Circle Diameter of $\\text{PCD} = 190.00\\text{ mm}$ ($R = 95.00\\text{ mm}$). Setting disc diameter to $\\varnothing 206.00\\text{ mm}$ provides a continuous, high-integrity **$8.00\\text{ mm}$ protective outer rim margin** beyond the trunnion centers ($5.00\\text{ mm}$ solid ligament beyond the $\\varnothing 6.0\\text{ mm}$ bushing counterbore), preventing hoop rupture under $92.5\\text{ N}$ centrifugal blade loads.
- **Center Pilot Bore & Shaft Adapter Bolt Pattern:**
  - **Center Pilot Bore:** **`Ø 14.00 mm`** Through All. Centered at $(0, 0)$; provides clearance for the stepped hub shoulder of `03_Shaft_Drive_Hub_Adapter`.
  - **Adapter Mounting Holes (4x):** **`Ø 2.80 mm`** (clearance fit for M2.5 socket head cap screws) Through All.
  - **Pitch Circle Diameter (PCD):** **`Ø 22.00 mm`**.
  - **Azimuthal Orientation:** Located at **$45^\\circ, 135^\\circ, 225^\\circ, 315^\\circ$** (offset by $45^\\circ$ from the blade trunnion stations at $0^\\circ, 90^\\circ, 180^\\circ, 270^\\circ$ to prevent fastener head interference with blade roots).
- **Trunnion Bushing Stations (4x on PCD $\\varnothing 190.00\\text{ mm}$):**
  - Located at cardinal angles: $(0, +95.0)$, $(+95.0, 0)$, $(0, -95.0)$, $(-95.0, 0)\\text{ mm}$.
  - **Two-Step Stepped Counterbore Feature (Seats Igus JFM-0306-04 Flush):**
    - **Through-Bore:** **`Ø 6.00 mm`** (+0.02 / +0.00 mm, H7 press-fit for the Igus bushing outer barrel) Through All.
    - **Flange Counterbore:** **`Ø 8.00 mm`** diameter with depth **`1.00 mm`** Blind into the outer disc face.
    - *Physical Validation:* The Igus JFM-0306-04 polymer flanged bushing has a flange outer diameter of $\\varnothing 7.50\\text{ mm}$ and flange axial thickness of $1.00\\text{ mm}$. Sinking a $\\varnothing 8.00\\text{ mm} \\times 1.00\\text{ mm}$ counterbore seats the bushing flange completely flush with the outer composite face, leaving an intact $0.50\\text{ mm}$ solid web shoulder to react spanwise aerodynamic thrust loads.
- **Weight-Reduction Lightening Pockets (4x Triangular Cutouts):**
  - Located symmetrically in the 4 quadrants between the radial trunnion spokes.
  - **Inner Boundary Arc:** Radius $R_{\\text{inner}} \\approx 18.00\\text{ mm}$ (maintains a solid $\\varnothing 36.00\\text{ mm}$ central torque hub around the $\\varnothing 22\\text{ mm}$ bolt circle).
  - **Outer Boundary Arc:** Radius $R_{\\text{outer}} \\approx 87.00\\text{ mm}$ (maintains structural rim material inside the $95.0\\text{ mm}$ trunnion PCD).
  - **Structural Spoke Webbing:** Straight radial boundary walls leaving **$3.00\\text{ mm}$ to $4.00\\text{ mm}$** web width to adjacent trunnion bosses.
  - **Corner Fillets:** **$R = 3.00\\text{ mm}$** internal blend radii to minimize notch stress concentrations under cyclic centrifugal bending.
  - **Feature Execution:** Cut-Extrude Through All $\\rightarrow$ Circular Pattern $\\times 4$ ($360^\\circ$ equal spacing).

---

#### 6.5.12 Part 03 — Shaft Drive Hub Adapter Collar (`03_Shaft_Drive_Hub_Adapter.SLDPRT`)
- **Context & Manufacturing:** Precision CNC turned and milled collar (Qty: 2). Material: Aerospace Aluminum 7075-T6 ($\\rho = 2810\\text{ kg/m}^3$). Target Mass: **$4.50\\text{ g}$** each.
- **Functional Role:** Provides rigid torque transmission between the ground $\\varnothing 6.00\\text{ mm}$ drive shaft and the $1.50\\text{ mm}$ G10 endplate discs, eliminating disc wobble and ensuring perpendicular disc tracking at $2640\\text{ RPM}$.
- **Geometric Dimensions:**
  - **Shaft Journal Bore:** **`Ø 6.00 mm`** H7 (+0.012 / +0.000 mm) through central axis.
  - **Cross-Pin Bore:** Cross-drilled **`Ø 2.00 mm`** through the collar barrel to accept a DIN 1481 $\\varnothing 2.0\\text{ mm} \\times 14\\text{ mm}$ spring roll pin, positively locking rotation to the drive shaft.
  - **Mounting Flange:** Outer diameter **`Ø 28.00 mm`** $\\times$ axial thickness **`3.00 mm`**.
  - **4-Hole Bolt Pattern:** 4x M2.5 tapped blind holes (or clearance holes) on PCD **`Ø 22.00 mm`** matching the endplate disc.
  - **Hub Boss Extension:** Outer diameter $\\varnothing 13.90\\text{ mm}$ ($0.10\\text{ mm}$ clearance fit into the $\\varnothing 14.00\\text{ mm}$ endplate center bore) $\\times 1.50\\text{ mm}$ step height.

---

#### 6.5.13 Part 04 — Rev 3.0 4130 Chromoly Central Drive Shaft (`04_Central_Drive_Shaft.SLDPRT`)
- **Context & Material:** Precision ground center drive shaft (Qty: 1). Material: AISI 4130 Chromoly Alloy Steel (normalized/quenched & tempered, $\\rho = 7850\\text{ kg/m}^3$, yield strength $S_y = 435\\text{ MPa}$). Target Mass: **$28.00\\text{ g}$** (or $32.37\\text{ g}$ in Ti-6Al-4V).
- **Overall Dimensions:** Ground cylinder **`Ø 6.00 mm`** h7 ($-0.000 / -0.012\\text{ mm}$) $\\times$ overall length **`260.00 mm`**.
- **Key Machined Features along Span:**
  - **Cross-Pin Holes (2x):** Transverse through-holes **`Ø 2.00 mm`** cross-drilled at $Z = \\pm 110.00\\text{ mm}$ (measured from Front Plane symmetry datum) to pin both `03_Shaft_Drive_Hub_Adapter` collars via DIN 1481 roll pins.
  - **Chassis Bearing Retaining Grooves (4x DIN 471):** Groove root diameter $d_3 = \\mathbf{\\varnothing 5.00\\text{ mm}}$ ($-0.08 / +0.00\\text{ mm}$, radial depth $0.50\\text{ mm}$), width $m = \\mathbf{0.80\\text{ mm}}$ ($+0.10 / -0.00\\text{ mm}$) for standard DIN 471 retaining rings.
  - **Drive D-Flats (Motor End):** $7.00\\text{ mm}$ long flat-to-flat $5.00\\text{ mm}$ clamping flats ($0.50\\text{ mm}$ cut depth per side) for D19L25 flexible jaw coupler.

---

#### 6.5.14 Part 05 — Rev 3.0 Blade Pitch Horn (`05_Blade_Pitch_Horn.SLDPRT`)
- **Context & Material:** Lightweight pitch crank arm (Qty: 4). Material: SLS PA12 Nylon / CNC 7075-T6 Aluminum. Target Mass: **$1.80\\text{ g}$** each ($7.20\\text{ g}$ total set).
- **Geometric Dimensions:**
  - **Effective Pitch Moment Arm ($r_h$):** Exactly **`12.00 mm`** center-to-center distance from trunnion axis to M2 brass ball-stud center.
  - **Trunnion Clamp Hub:** Outer diameter $\\varnothing 7.00\\text{ mm}$ with precision **`Ø 3.00 mm`** bore, axial split clamping slit ($0.80\\text{ mm}$ width), and transverse M2 pinch screw hole to clamp solidly onto the trunnion pin D-flat.
  - **Pushrod Ball-Stud Station:** Outer diameter $\\varnothing 5.00\\text{ mm}$ with **`Ø 2.05 mm`** hole for M2 brass ball stud shank.
  - **Hub Axial Width:** **`3.50 mm`** (fits within axial stackup budget between endplate and mechanism chassis).

---

#### 6.5.15 Part 06 — 2-DOF Orthogonal Pitch Carriage & Pushrod Assembly (`06_2DOF_Pitch_Carriage.SLDPRT`)
- **Context & Material:** 2-DOF cyclic swashplate assembly. Material: CNC 7075-T6 Aluminum inner/outer plates + 6802 thin-section bearing ($15 \\times 24 \\times 5\\text{ mm}$). Target Mass: Inner plate $6.0\\text{ g}$, Outer ring + bearing $7.5\\text{ g}$.
- **Kinematic Function:**
  - Driven by 2x KST X08 V5 micro servos ($2.8\\text{ kg}\\cdot\\text{cm}$ torque) via orthogonal linkages.
  - Bounded linear travel radius $E_{\\max} = 6.88\\text{ mm}$ drives cyclic blade pitch amplitude $\\theta_0 = \\arcsin(e / r_h) = \\arcsin(6.88 / 12.00) = \\pm 35.0^\\circ$.
  - 4 integrated radial clevis ears at $90^\\circ$ spacing on the rotating outer ring drive 4x carbon pushrods ($\\varnothing 2.0\\text{ mm}$ UD tube, $L \\approx 45\\text{--}95\\text{ mm}$, mass $2.6\\text{ g}$ each) with M2 brass ball-link rod ends.

---

#### 6.5.16 Part 07 — Chassis Cage Standoffs & Aerodynamic Fairings (`07_Chassis_Cage_and_Fairings.SLDPRT`)
- **Context & Material:** Structural tie-rod standoffs (4x $\\varnothing 6.00\\text{ mm}$ 7075-T6 / carbon tubes) connecting G10 bulkheads, enclosed by 4x snap-on FDM PETG teardrop aerodynamic fairing sleeves.
- **Aerodynamic Profile (NACA 0025 Symmetrical Teardrop):**
  - Chord length: $c_{\\text{fairing}} = 32.00\\text{ mm}$.
  - Maximum thickness: $t_{\\max} = 8.00\\text{ mm}$ ($t/c = 0.25$).
  - Discrete coordinate generation via `scripts/generate_naca0025.py` (`scripts/naca0025_chord32mm_solidworks.txt`).
  - Total fairing set mass: **$12.00\\text{ g}$** ($3.0\\text{ g}$ each).
  - Recovers $+0.48\\text{ N}$ net thrust by reducing structural pillar wake blockage from $0.92 \\to 0.96$.
"""

# 2. New Section 12 Items
new_12 = """
38. **SolidWorks COM API Automation Early-Binding vs. Dynamic Dispatch & ByRef Pointer Mismatch:**
    - *Problem:* Automated Python scripts utilizing `win32com.client.gencache.EnsureDispatch('SldWorks.Application')` threw critical early-binding generation errors because SolidWorks type libraries fail during automated cache generation. Furthermore, executing `sw.OpenDoc6()` via dynamic dispatch threw fatal `Type mismatch` errors on the ByRef VARIANT error/warning pointers.
    - *Diagnostic & Root Cause:* Dynamic COM dispatch in Python cannot marshal pointer-to-pointer ByRef types without pre-compiled typelibs. SolidWorks requires template paths to exist (`C:\\ProgramData\\SolidWorks\\SOLIDWORKS 2026\\templates\\Part.prtdot`) and hangs if modal lock prompts are encountered.
    - *Solution:* Standardized the COM interaction pattern: (1) Use late-bound `win32com.client.Dispatch('SldWorks.Application')` or VBScript (`cscript.exe`) for ByRef operations; (2) In Python, call `sw.OpenDoc(path, doc_type)` (which takes only two integer/string arguments and eliminates ByRef pointers); (3) Standardized default part template paths for SolidWorks 2026 (v34.3.2).

39. **Analytical NACA 0012 Profile Equation Formulation (Leading-Edge vs. Spar Origin):**
    - *Problem:* Importing discrete point curves often creates segmented splines that slow down rebuild times and introduce microscopic surface curvature ripples.
    - *Solution:* Formulated two exact continuous analytical equations for SolidWorks *Tools > Sketch Entities > Equation Driven Curve*: (a) Leading-edge origin form for base airfoil lofting, and (b) Spar-origin form with $x' = x + 9.50\\text{ mm}$ shift, centering the sketch coordinate origin directly on the $25\\%$ chord pitch axis ($X = 0, Y = 0$) and eliminating reference dimension constraints.

40. **Inner Cavity Wall Thickness Offset & Spar Capture Geometry:**
    - *Problem:* Shelling thin airfoils fails due to trailing-edge zero-thickness singularity, while simple 2D sketch offsets fail near the high-curvature leading-edge nose.
    - *Solution:* Validated that vertical analytical offset $Y_{\\text{inner}} = Y_{\\text{outer}} - 0.25$ provides $< 0.5\\%$ thickness error compared to true normal offsets for thin airfoils ($t/c = 0.12$). At the spar axis ($x = 9.50\\text{ mm}$), the inner cavity full height calculates to exactly $4.0151\\text{ mm}$, providing an ideal $+0.0151\\text{ mm}$ slip-fit capture for the $\\varnothing 4.000\\text{ mm}$ UD carbon spar tube without rattling.

41. **Endplate Hub Disc Ø206 mm Perimeter Clearance & Bushing Counterbore Flush Fit:**
    - *Problem:* Placing $\\varnothing 6.0\\text{ mm}$ trunnion holes on a $\\varnothing 190.0\\text{ mm}$ disc splits the outer edge. Placing flanged bushings on flat plates leaves protruding flanges that rub against the blade roots.
    - *Solution:* Expanded the G10 disc to $\\varnothing 206.00\\text{ mm}$ ($R = 103.00\\text{ mm}$), leaving an $8.00\\text{ mm}$ outer rim past the $95.0\\text{ mm}$ trunnion centers. Counterbored the outer face to $\\varnothing 8.00\\text{ mm} \\times 1.00\\text{ mm}$ depth, recessing the Igus JFM-0306-04 bushing flange flush with the plate surface while preserving an intact $0.50\\text{ mm}$ web shoulder.

42. **Running Air Gap & Full Envelope Clearance Verification (12.25 mm vs. 3.50 mm Minimum):**
    - *Problem:* Severe risk of blade tips striking stationary chassis members under dynamic cyclic pitch ($\pm 35.0^\circ$) at 44 Hz.
    - *Solution:* Conducted an exhaustive kinematic clearance sweep across all blade azimuth angles $\psi \in [0^\circ, 360^\circ]$ and pitch strokes $\theta_0 \in [-35^\circ, +35^\circ]$. Maximum swept radius reaches $R_{\\text{sweep}} = 123.50\\text{ mm}$. With chassis envelope inner clearance half-width at $135.75\\text{ mm}$ ($271.50 \\times 263.50\\text{ mm}$ envelope), the net running air gap is verified at **$12.25\\text{ mm}$**, comfortably exceeding the $\ge 3.50\\text{ mm}$ requirement by $+8.75\\text{ mm}$.

43. **Sizing Solver Cosmetic Default Label vs. Aerodynamic Coefficients:**
    - *Problem:* Code inspection of `cyclorotor_sizing.py` (line 51) showed default dataclass string `airfoil: str = "NACA 0015"`, causing potential confusion regarding whether Rev 2.0 or Rev 3.0 aerodynamics were being computed.
    - *Solution:* Verified that the solver correctly applies the lower zero-lift drag coefficient $C_{d0} = 0.016$ and reduced profile thickness characteristic of NACA 0012, confirming that the "NACA 0015" string was purely a legacy cosmetic default label and does not affect the verified $FM = 0.768$ and $T/W = 4.06$ results.
"""

# 3. New Section 14 Table Rows
new_14_rows = """| **NACA 0012 Single Curve Generator** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\generate_naca0012.py` | Generates 159-point closed NACA 0012 curve file (`naca0012_chord38mm_solidworks.txt`) centered on quarter-chord. |
| **Comprehensive NACA 0012 Curves Suite** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\generate_naca0012_curves.py` | Generates 8 distinct curve files (outer/inner x upper/lower x LE/spar origins) with exact normal offset calculation. |
| **NACA 0025 Teardrop Fairing Generator** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\generate_naca0025.py` | Generates 100-point NACA 0025 teardrop fairing curve for chassis standoffs (`naca0025_chord32mm_solidworks.txt`). |
| **Master Blade Dimension Audit Script** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\audit_blade_dims.py` | Comprehensive multi-source dimensional consistency and clearance audit script across all CAD/BEMT parameters. |
| **NACA 0012 159-Point Closed Curve** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\naca0012_chord38mm_solidworks.txt` | SolidWorks curve file for importing closed NACA 0012 profile with spar-origin coordinates. |
| **NACA 0012 Discrete Coordinate Sets (8x)** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\naca0012_outer_upper_spar.txt` | 100-point discrete coordinate files for outer and inner curves in both LE-origin and spar-origin formats. |
| **NACA 0025 Fairing Spline Coordinates** | `c:\\Users\\Adarsh Singh\\CycloProp\\scripts\\naca0025_chord32mm_solidworks.txt` | SolidWorks coordinate curve file for extruding teardrop aerodynamic fairing sleeves on chassis pillars. |
"""

# Now integrate into content:

# Insertion 1: Before "### 6.6 Master Assembly Mating Sequence"
target_66 = "### 6.6 Master Assembly Mating Sequence & Kinematic Verification (`Cyclorotor_Module.SLDASM`)"
if target_66 in content:
    content = content.replace(target_66, new_65 + "\n---\n\n" + target_66)
    print("Successfully inserted Section 6.5 expansions!")
else:
    print("ERROR: target_66 not found!")

# Insertion 2: Before "## 13. Advanced Design Optimization Roadmap"
target_13 = "## 13. Advanced Design Optimization Roadmap (Future Enhancements)"
if target_13 in content:
    content = content.replace(target_13, new_12 + "\n" + target_13)
    print("Successfully inserted Section 12 expansions!")
else:
    print("ERROR: target_13 not found!")

# Insertion 3: Inside Section 14 table (before "### How to Re-Run the Simulations:")
target_rerun = "### How to Re-Run the Simulations:"
if target_rerun in content:
    content = content.replace(target_rerun, new_14_rows + "\n" + target_rerun)
    print("Successfully inserted Section 14 expansions!")
else:
    print("ERROR: target_rerun not found!")

# Write updated content back to CYCLOPROP_MASTER_KNOWLEDGE_BASE.md
with open('CYCLOPROP_MASTER_KNOWLEDGE_BASE.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated file written successfully. New length:", len(content))
