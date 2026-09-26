# CycloProp — Advanced 360° Thrust-Vectoring Cycloidal Rotor UAV Propulsion Module

**PUSHPAK Grand Challenge 2026**  
*Organized by MeitY, Government of India & IIT Bombay Aerospace Department*  
*Evaluators: Prof. Arnab Maity & Dr. Dhwanil Shukla*

---

## What is CycloProp?

CycloProp is an indigenous **cycloidal rotor (cyclorotor)** propulsion module designed for high-agility VTOL UAVs. A cyclorotor spins blades around a horizontal axis while simultaneously pitching each blade cyclically — allowing it to vector thrust **instantly in any direction (360°)** without tilting the vehicle body.

This repository contains the complete **Stage 1 Technical Design Report** deliverables:
- Aerodynamic simulation code (BEMT solver)
- Mechanical design (SolidWorks CAD assembly)
- Engineering analysis figures
- Bill of Materials

---

## Key Performance Metrics (Rev 3.0 Baseline)

| Parameter | Value |
|:---|:---:|
| Net Hover Thrust | **11.76 N** (hover) / **15.0 N** (burst) |
| Total Module Mass | **301.4 g** |
| Thrust-to-Weight Ratio | **4.06** |
| Rotor Speed | **2640 RPM** (44.0 Hz) |
| Blade Tip Speed | **26.3 m/s** |
| Figure of Merit (FM) | **0.768** |
| Electrical Power Loading | **5.83 g/W** |
| Electrical Power (hover) | **209.8 W** |
| Motor Current (hover) | **14.2 A** on 4S LiPo |
| Rotor Radius | **95 mm** |
| Blade Span | **220 mm** |
| Blade Chord | **38 mm** |
| Number of Blades | **4** |
| Airfoil | **NACA 0012** |
| Rotor Solidity (σ) | **0.509** |
| Blade Aspect Ratio | **5.79** |
| Pitch Amplitude (θ₀) | **± 35°** |

---

## System Architecture

The rotor consists of 4 NACA 0012 blades arranged radially at 90° intervals, mounted between two hub endplates on a central drive shaft. Each blade pivots about its quarter-chord axis via trunnion pins riding in Igus Iglide J polymer flanged bushings.

A **2-DOF eccentric ring pitch mechanism** at the top of the assembly translates the pitch eccentricity in X and Y using two KST X08 V5 micro servos, producing a sinusoidal cyclic pitch schedule:

$$\theta(\psi) = \theta_0 \sin(\psi - \phi_0)$$

By controlling the direction of eccentricity, thrust can be vectored to any azimuth at full magnitude — with a servo response latency of **12–18 ms**.

### Drivetrain
- **Motor:** T-Motor MN3508 380KV outrunner
- **ESC:** BLHeli_32 35A with DShot1200
- **Shaft:** Ø6 mm × 260 mm precision ground 4130 Chromoly steel
- **Coupling:** D19L25 flexible jaw coupler (motor shaft Ø4 mm → rotor shaft Ø6 mm)

---

## Engineering Innovations (Rev 3.0)

### 1. Teardrop Pillar Aerodynamic Fairings
Rectangular structural pillars in the rotor inflow field create turbulent wakes that reduce thrust. Rev 3.0 adds symmetric teardrop fairings over each 11 mm pillar, reducing the effective blockage factor from 0.92 to 0.96 and recovering **+0.48 N** of thrust at zero additional power.

### 2. NACA 0012 Airfoil
At Re ≈ 85,000–110,000 and cyclic pitch up to ±35°, the NACA 0012 (t/c = 12%) outperforms the NACA 0015 (t/c = 15%) due to a lower zero-lift profile drag coefficient:
- NACA 0015: Cd₀ = 0.020
- NACA 0012: Cd₀ = 0.016

This reduces blade profile drag power and improves FM from **0.744 → 0.768**.

### 3. Igus Iglide J Polymer Trunnion Bushings
Miniature ball bearings oscillating at ±35° / 44 Hz suffer false brinelling (lubricant expulsion and race indentation). Rev 3.0 replaces them with **Igus Iglide J flanged polymer bushings (JFM-0306-04)**:
- Operating PV = **0.336 MPa·m/s** (rated: 1.20 MPa·m/s → **3.57× margin**)
- Centrifugal axial compressive stress = **2.49 MPa** (yield: 35 MPa → **14.0× margin**)
- False brinelling risk: **zero** (solid polymer matrix)

### 4. Asymmetric Cam-Track Pitch Schedule
A 3rd-harmonic cam profile was analytically formulated:

$$\theta_\text{cam}(\psi) = \theta_0 \left[\frac{\sin(\psi - \phi_0) + 0.15\sin(3(\psi - \phi_0))}{\max|\cdot|}\right]$$

This produces a flattened pitch dwell at the advancing arc, delivering **+9.2% more thrust (12.84 N)** at the same RPM. Proposed as a Phase 2 prototype upgrade via a precision CNC cam groove replacing the circular eccentric ring.

### 5. Motor Cooling Scoop
A 3D-printed PETG duct routes a portion of the rotor's 7.5 m/s downwash into the open motor bell stator windows:
- Stator steady-state temperature: **49.4°C** (Class-H insulation limit: 120°C → **2.4× thermal margin**)

---

## Structural Analysis Summary

| Check | Value | Safety Factor |
|:---|:---:|:---:|
| Blade centrifugal force (per blade @ 2640 RPM) | 92.5 N | — |
| Trunnion pin tensile stress (Ti-6Al-4V, Ø3 mm) | 13.08 MPa | **67.3×** |
| Blade spanwise bending deflection | 0.124 mm | **28.2× vs 3.5 mm air gap** |
| Bushing PV factor | 0.336 MPa·m/s | **3.57×** |
| Bushing axial compressive stress | 2.49 MPa | **14.0×** |
| Servo torque (KST X08 V5) | 2.8 kg·cm | **3.71× vs 0.76 kg·cm peak** |

---

## Repository Structure

```
CycloProp/
│
├── cyclorotor_sizing.py              # Core BEMT aerodynamic solver
│   ├── Multi-airfoil polar model (NACA 0015, 0012, Eppler E374)
│   ├── Dynamic stall + virtual camber corrections
│   ├── Parametric sweeps (R, b, c, RPM, θ₀)
│   └── Airfoil & cam-track trade study (4-panel publication figure)
│
├── cyclorotor_bom_motorspec.py       # Bill of Materials & compliance checker
│   ├── Rev 3.0 BOM (16 line items, 301.4 g total)
│   ├── Igus Iglide J polymer bushing PV validation
│   └── Motor & servo specification tables
│
├── generate_engineering_drawings.py  # 4-view GA orthographic drawing generator
├── generate_kinematics_plot.py       # Multi-blade cyclic pitch phase plot
├── test_configs.py                   # Automated configuration verification
│
├── figures/                          # All generated publication-grade figures
│   ├── airfoil_and_cam_pitch_study.png
│   ├── thrust_power_vs_rpm.png
│   ├── figure_of_merit_power_loading.png
│   ├── geometric_parameter_sweeps.png
│   ├── azimuth_aerodynamics_detailed.png
│   ├── bom_budget_chart.png
│   ├── cycloprop_engineering_ga_drawing.png
│   └── Fig_Kinematics_Plot.png
│
└── CAD/                              # SolidWorks Assembly & Part Files
    ├── Assem9.SLDASM                 # Master assembly
    ├── 1-Blade_NACA0015.SLDPRT
    ├── 2-Endplate_Hub.SLDPRT
    ├── 3-Drive_Shaft.SLDPRT
    ├── 4-Inner_Carriage_Plate.SLDPRT
    ├── 4-Outer_Control_Ring.SLDPRT
    ├── 5-Pushrod_Linkage.SLDPRT
    ├── 6-Mounting_Chassis_Frame.SLDPRT
    ├── Blade_Pitch_Arm.SLDPRT
    └── [COTS models: T-Motor MN3508, Savox SH-0257MG]
```

---

## How to Run the Aerodynamic Simulation

**Requirements:** Python 3.9+, NumPy, Matplotlib

```bash
pip install numpy matplotlib
python cyclorotor_sizing.py             # Full BEMT sweep + trade study
python cyclorotor_bom_motorspec.py      # BOM & structural validation
python generate_kinematics_plot.py      # Multi-blade pitch kinematics
python generate_engineering_drawings.py # 4-view GA engineering drawing
```

All figures are saved to the `figures/` directory automatically.

---

## Team

**Adarsh Singh** — B.Tech. Mathematics and Computing, IIT Ropar (2025MCB1458)

---

## Competition Reference

- **Challenge:** PUSHPAK Grand Challenge 2026
- **Organizers:** MeitY (Government of India) & IIT Bombay Drone Centre
- **Stage:** Stage 1 — Technical Design Report

---

*All simulation results are generated by open-source Python code in this repository and are fully reproducible.*
