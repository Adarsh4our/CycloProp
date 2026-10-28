# CycloProp Bench Prototype — Master CAD, Motion & Structural Verification Summary (`DOC-003` / `MFG-001`)

**Updated:** 28 October 2026  
**Workspace Folder:** `CAD/Design_Completion/Bench_Prototype/`  
**Top-Level Assembly:** `BA_Bench_Actuation_Layout.SLDASM` (`19.2329 kg` active mass, `486` active solid leaf components in `"Default"`, `211` in `"Motion_Fast_Playback"`)  
**Rotor & 400W Drive Subassembly:** `Bench_Rotor/BD_Bench_Development_Source.SLDASM` (`3.0590 kg` active mass)  
**Baseline Configuration (Untouched):** [config/baseline.json](../../../config/baseline.json) (`SHA-256: 2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f`)

---

## 1. Master File & SHA-256 Manifest

### 1.1 Top-Level & Sub-Assemblies (`CAD/Design_Completion/Bench_Prototype/`)

| File Path (Relative to `Bench_Prototype/`) | Role / Description | Active Mass | Current On-Disk SHA-256 (`Post-SIM-001C`) | Pre-`SIM-001C` / Post-`CAD-003C` SHA-256 |
| :--- | :--- | :---: | :--- | :--- |
| `BA_Bench_Actuation_Layout.SLDASM` | Top-level Bench Prototype assembly (`"Default"` & `"Motion_Fast_Playback"`, `"Motion Study 1"`) | `19.2329 kg` (`19,232.87 g`) | `512f00201d447e933d6bbe7b04abf279d25868e749840efa0857394c395f5ed4` | `1cbf3166364813e508064d95a655f0d2f7d242ce4df03811b0a4bcfbf61308df` |
| `Bench_Rotor/BD_Bench_Development_Source.SLDASM` | Bench Rotor + 400W IDS motor drive subassembly (`"Default"` & `"Motion_Fast_Playback"`) | `3.0590 kg` (`3,059.00 g`) | `b437626576bdf4ffd99d83b2f246a90f77f30f380308f757490eebca58466e52` | `58e9b5612a95bb9111f3c3bdfb6e5ff1794b11b72b2caafea3bc0dd19811da35` (`SIM-001A`) / `eefe8e65f1e15e9a077b223fccbc19e134a933dcd2c788ed9ceb233500b1e835` (`CAD-003C`) |
| `Bench_Rotor/BD_RB_Assem3.SLDASM` | Eccentric inner carriage & outer control ring subassembly | `141.97 g` | `8bf62186cd3ca77976fab9cae0f94e272ba2c544cab796f41b24cf4a8d8989b5` | `8bf62186cd3ca77976fab9cae0f94e272ba2c544cab796f41b24cf4a8d8989b5` |
| `Bench_Rotor/BD_RB_6806.SLDASM` | 6806 thin-section control ring ball bearing (`AISI 4340` assigned) | `23.7936 g` | `a1afe833820c20e2e05ab0c09f997608df9d4038ea749087884e342cb73aed97` | `a1afe833820c20e2e05ab0c09f997608df9d4038ea749087884e342cb73aed97` |
| `Bench_Rotor/BD_RB_Blade_Bearing_Cartridge_Set_PROTOTYPE.SLDASM` | Blade root/tip bearing cartridge subassembly (8x instances) | `4.12 g` each | `2a298a3210929f2be4fa5c51abb04bddbd2c2e441d4caf62b3cf2a233ebde8e6` | `2a298a3210929f2be4fa5c51abb04bddbd2c2e441d4caf62b3cf2a233ebde8e6` |

*(Note: All `123` `.SLDPRT` files across `Bench_Rotor/`, `Actuation_Models/`, and `Hardware_Models/` are verified bit-for-bit identical to the `CAD-003C` / `SIM-001A` 123-part manifest recorded in `SIM001A_MOTION_STATE.json`).*

### 1.2 Completion States, Reports, Datasets, Plots & Videos

| Artifact File | Task ID | Size (Bytes) | SHA-256 Hash |
| :--- | :---: | :---: | :--- |
| [CAD003A_COMPLETION_STATE.json](CAD003A_COMPLETION_STATE.json) | `CAD-003A` | `45,400` | `afd7a52096e3ddeca66b52805135d8cf24f916b7101400bd9e535d0360350d79` |
| [CAD003B_COMPLETION_STATE.json](CAD003B_COMPLETION_STATE.json) | `CAD-003B` | `49,384` | `1c60c910acd6e283a4196348f5a4393f50ec2d5bcd6d6a6edfae91908d29dec5` |
| [CAD003C_COMPLETION_STATE.json](CAD003C_COMPLETION_STATE.json) | `CAD-003C` | `20,669` | `af42f57f1466e353c81360135de9f40ddaa63bc9ac5eb25dd71f53783e118094` |
| [SIM001A_MOTION_STATE.json](SIM001A_MOTION_STATE.json) | `SIM-001A` | `664,515` | `4744354ef8a6a1894978e44f4af6a9541b78cda35140ee0c21699b923b0261c8` |
| [SIM001B_STRUCTURAL_STATE.json](SIM001B_STRUCTURAL_STATE.json) | `SIM-001B` | `68,175` | `1f0a04503c8cf3555b070ed575e1a2c9165a7b32153aa182ef436bfc4e23698c` |
| [SIM001C_MOTION_STUDY_STATE.json](SIM001C_MOTION_STUDY_STATE.json) | `SIM-001C` | `2,053` | `11550e8078063e363e6922d068ee9c3d2831ec3fb0c6151238b1ca9623245c50` |
| [Motion_Study/SIM001_MOTION_AND_STRUCTURAL_REPORT.md](Motion_Study/SIM001_MOTION_AND_STRUCTURAL_REPORT.md) | `SIM-001B` | `14,628` | `b16ad1d53273583af10097f41c749a882adc1483829a66903ce547c708b4c563` |
| [Motion_Study/sim001a_caseB_1900rpm_hover_e4p914.csv](Motion_Study/sim001a_caseB_1900rpm_hover_e4p914.csv) | `SIM-001A` | `1,410,966` | `3decfb0e2b413e449b78b0c473ee3e92fc73078926a150590fc55242ce46b429` |
| [Motion_Study/sim001a_caseC_1900rpm_max_e6p880.csv](Motion_Study/sim001a_caseC_1900rpm_max_e6p880.csv) | `SIM-001A` | `1,404,023` | `a4b6af934af8baed59c268c90953e00073690c2902b1edf6910a8ec0af7941ae` |
| [Motion_Study/sim001a_caseD_2100rpm_burst_e6p880.csv](Motion_Study/sim001a_caseD_2100rpm_burst_e6p880.csv) | `SIM-001A` | `1,402,827` | `df3d2651858fa015016fae2e56c1a5a9ab21669fc2129796826623d64b3860b6` |
| [Motion_Study/sim001a_interactive_line_sim.html](Motion_Study/sim001a_interactive_line_sim.html) | `SIM-001A` | `7,689` | `fe00ae31aad7d81da488702181524f9cf7f2587fcd6e59ba358d6d9e1d95121c` |
| [Motion_Study/sim001a_line_sim_overview.png](Motion_Study/sim001a_line_sim_overview.png) | `SIM-001A` | `585,574` | `76e05a3fc2aa512ea87d7709ff9795c5d476da0dd7c1d9048d50d22be3a61432` |
| [Motion_Study/sim001b_structural_safety_overview.png](Motion_Study/sim001b_structural_safety_overview.png) | `SIM-001B` | `481,559` | `eea65d6acf9dbbbd24f63f2a284ab5c049e5738a3f16e760508b1ff0286c647c` |
| [Motion_Study/sim001c_solidworks_native_motion.mp4](Motion_Study/sim001c_solidworks_native_motion.mp4) | `SIM-001C` | `608,838` | `2ee1f7d8a7834dac49280e2ec53c471f39260269e317d3346f99e1a3427241df` |
| [Motion_Study/sim001c_solidworks_native_motion.avi](Motion_Study/sim001c_solidworks_native_motion.avi) | `SIM-001C` | `3,829,516` | `ced812214f3851a7133a2034672cf6a83ffaa7095d8282bfe09fbc7d05b6c0d5` |
| [Motion_Study/sim001c_live_window_playing.png](Motion_Study/sim001c_live_window_playing.png) | `SIM-001C` | `390,154` | `646cf44ce284fd5265ea22fccc2c9c8422228540fd94562de74e51f4392dfd4c` |
| [Motion_Study/sim001c_live_window_verified.png](Motion_Study/sim001c_live_window_verified.png) | `SIM-001C` | `397,126` | `b7c9105ab9c05bb38c776939ac80d632aae8ad6564ae59c495fcd5669004e93e` |
| [Deliverable_D1_Manufacturing/MFG001_PROGRESS_CHECKPOINT.json](Deliverable_D1_Manufacturing/MFG001_PROGRESS_CHECKPOINT.json) | `MFG-001` | `4,821` | Export checkpoint: 18 STEP AP214 files, 5 DXF flat patterns, 6 assembly views, 22 part renders, geometry & BOM JSON dumps |

### 1.3 Automation Scripts (`CAD/Design_Completion/automation/`)

| Script Path | Task ID | Size (Bytes) | SHA-256 Hash |
| :--- | :---: | :---: | :--- |
| [../automation/complete_bench_rotor_cad003a.py](../automation/complete_bench_rotor_cad003a.py) | `CAD-003A` | `40,110` | `9b51aa0985df62e0fa922ae51b01ec9736b4595b279cde1f69c736856df89b3b` |
| [../automation/complete_bench_actuation_cad003b.py](../automation/complete_bench_actuation_cad003b.py) | `CAD-003B` | `63,603` | `7ba99ce762c1fba26ee81ace7ddc03128827054474ed40ee7806747faf079f1d` |
| [../automation/complete_bench_cleanup_cad003c.py](../automation/complete_bench_cleanup_cad003c.py) | `CAD-003C` | `33,993` | `d43d8328d2bde6fd5ff01a5ef35dc958dba50cb8c280f6592ab93a1881651d3e` |
| [../automation/run_bench_motion_study_sim001a.py](../automation/run_bench_motion_study_sim001a.py) | `SIM-001A` | `100,994` | `b56e98584540742a5f46f3e0ab7685030634265f37fbf3cdf001579deae98f42` |
| [../automation/run_bench_structural_fea_sim001b.py](../automation/run_bench_structural_fea_sim001b.py) | `SIM-001B` | `80,797` | `b8a46a062956014e5918aa66a02122228e07226b3df13fc0831c0647a7d9ed40` |
| [../automation/setup_native_motion_study_sim001c.py](../automation/setup_native_motion_study_sim001c.py) | `SIM-001C` | `17,150` | `c21f945871a143c0c0aa82c5aaf25fac5264f2af293ba0d9b9b5ca02b3411f75` |

---

## 2. Assembly Configurations & Native SolidWorks `Motion Study 1` Playback Guide (`SIM-001C`)

Both `BA_Bench_Actuation_Layout.SLDASM` and `Bench_Rotor/BD_Bench_Development_Source.SLDASM` contain two synchronized SolidWorks configurations:

| Configuration Property | `"Default"` (Full Manufacturing & Clearance Audit) | `"Motion_Fast_Playback"` (Interactive Animation) |
| :--- | :---: | :---: |
| **Active Solid Leaf Components** | `486` | `211` |
| **Suppressed Decorative Fasteners / Washers / Nuts / Pins** | `0` (only 70 legacy flight Savox parts suppressed) | `275` (`65` top-level + `210` rotor subassembly) |
| **Active Assembly Mates** | `1,133` (`224` top + `909` sub) | `498` kinematic & structural mates (`635` fastener mates bypassed) |
| **Mate Errors / Warnings** | `0` | `0` |
| **Rotor Lock Mate (`RevB_SETUP_Rotor_Angle`)** | Active (locks shaft azimuth for deterministic pose sweeps) | **Suppressed** (frees main shaft for continuous $360^\circ$ rotation) |
| **Commanded Eccentricity ($e_X, e_Y$)** | $(0.00, 0.00)\text{ mm}$ home | $(+6.88, 0.00)\text{ mm}$ ($\pm 34.991^\circ$ cyclic pitch) |
| **Subassembly Solving (`BD_Bench_Development_Source-1`, `BD_RB_Assem3-1`)** | Flexible | Flexible |

### How to Play `"Motion Study 1"` in SolidWorks 2026
1. Open `CAD/Design_Completion/Bench_Prototype/BA_Bench_Actuation_Layout.SLDASM` in SolidWorks 2026 (kept open as the single visible document window).
2. Ensure the active configuration in the ConfigurationManager tab is **`Motion_Fast_Playback`** (already active and saved by default).
3. Click the **`Motion Study 1`** tab at the bottom-left of the SolidWorks viewport to expand the MotionManager timeline:
   - **Motor:** `RotaryMotor1` (`30.0 RPM` constant speed on `BD_RB_3-Drive_Shaft-1`, completing `2` full revolutions over `4.0 s`).
   - **Cached Frames:** `61` pre-calculated frames at `15 FPS` (`0.168 s` total calculate wall time) driving simultaneous main-shaft rotation, Oldham floating-disk $2\Omega$ orbital sliding, outer control-ring 1:1 phase lock, and $\pm 34.991^\circ$ 4-bar cyclic blade pitching at $e_X = +6.88\text{ mm}$.
4. Click **Play from Start** (or **Play** in **Loop** mode) in the MotionManager toolbar for smooth real-time viewport playback, or view the exported standalone animations directly:
   - MP4: [Motion_Study/sim001c_solidworks_native_motion.mp4](Motion_Study/sim001c_solidworks_native_motion.mp4)
   - AVI: [Motion_Study/sim001c_solidworks_native_motion.avi](Motion_Study/sim001c_solidworks_native_motion.avi)

---

## 3. Summary of `SIM-001A` Dynamic Loads & Zaber `NA23C60-T4A` Actuation Margins

### 3.1 Coupled 3D Motion & Dynamic Load Regimes

| Operating Case | Speed (RPM) | Eccentricity $e$ (mm) | Pitch Range $[\theta_{\min}, \theta_{\max}]$ | Peak $|\dot{\theta}_p|$ (rad/s) | Peak $|\ddot{\theta}_p|$ ($\text{rad/s}^2$) | 4-Bar Whip Factor $K_\alpha$ | Peak Link Load $|F_{\text{link}}|$ (N) | Oldham $v_{\text{slide,max}}$ (m/s) | Peak Carriage Hold $F_X / F_Y$ (N) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Case A (Concentric)** | 1900 | $0.000$ | $[0.00^\circ, 0.00^\circ]$ | $0.00$ | $0.0$ | — | $21.92$ (orbital) | $0.000$ | $0.00 / 0.00$ |
| **Case B (Hover $25^\circ$)** | 1900 | $4.914$ | $[-24.12^\circ, +24.23^\circ]$ | $82.22$ | $19,399.6$ | $1.1588$ | $24.86$ ($9.75$ sin) | $0.978$ | $17.61 / 11.08$ |
| **Case C (Max $35^\circ$ Nom)** | 1900 | $6.880$ | $[-34.99^\circ, +34.99^\circ]$ | $116.57$ | $31,056.8$ | **$1.2846$** | **$27.56$** ($15.14$ sin) | $1.369$ | **$25.27 / 25.88$** |
| **Case D (Max $35^\circ$ Burst)** | 2100 | $6.880$ | $[-34.99^\circ, +34.99^\circ]$ | $128.84$ | $37,939.2$ | **$1.2846$** | **$33.67$** ($18.50$ sin) | $1.513$ | **$30.87 / 31.61$** |

### 3.2 Zaber `NA23C60-T4A` ($120\text{ N}$ Rated Thrust) X/Y Actuator Force & Safety Factor Audit

| Operating Regime (`13.76 mm` Full-Stroke Slew in `0.25 s`, $v_{\text{slew}} = 82.56\text{ mm/s}$) | Axis | Steady Hold Peak (N) | Peak Slew Force — Lubricated $\mu=0.12$ (N) | Peak Slew Force — Dry $\mu=0.18$ (N) | Continuous RMS Force (N) | Peak Safety Factor (Lub / Dry) | Continuous RMS Safety Factor |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nominal (`1900 RPM`, $e = 6.88\text{ mm}$)** | **X-Axis** (`m_slew = 446.84 g`) | $25.27$ | $34.40$ | **$35.95$** | $19.91$ | **$3.49\times$ / $3.34\times$** | **$6.03\times$** |
| **Nominal (`1900 RPM`, $e = 6.88\text{ mm}$)** | **Y-Axis** (`m_slew = 404.49 g`) | $25.88$ | $30.68$ | **$32.23$** | $19.04$ | **$3.91\times$ / $3.72\times$** | **$6.30\times$** |
| **Burst (`2100 RPM`, $e = 6.88\text{ mm}$)** | **X-Axis** (`m_slew = 446.84 g`) | $30.87$ | $41.89$ | **$43.79$** | $24.30$ | **$2.86\times$ / $2.74\times$** | **$4.94\times$** |
| **Burst (`2100 RPM`, $e = 6.88\text{ mm}$)** | **Y-Axis** (`m_slew = 404.49 g`) | $31.61$ | $37.36$ | **$39.26$** | $23.24$ | **$3.21\times$ / $3.06\times$** | **$5.16\times$** |

---

## 4. Summary of `SIM-001B` Critical-Part Structural Safety Factors & Deflection Budgets

| Component Group & Bottleneck Feature | Material ($\sigma_y$ / $\sigma_u$) | 1900 RPM Peak Stress (MPa) | 1900 RPM Safety Factor ($SF_y$ / $SF_{\text{buck}}$) | 2100 RPM Burst Stress (MPa) | 2100 RPM Burst Safety Factor | Elastic Deflection (1900 / 2100 RPM) | Status ($SF \ge 1.5$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1A. Lower Bearing Pedestal ($Z=8.5\text{ mm}$ `R0.30` Fillet — Steady Hold)** | AISI 4340 Norm ($710 / 1110\text{ MPa}$) | $138.08\text{ MPa}$ ($K_t$) / $120.70\text{ MPa}$ ($K_f$) | **$5.14\times$ ($K_t$) / $5.88\times$ ($K_f$)** ($SF_{\text{Goodman}} = 6.92\times$) | $168.34\text{ MPa}$ ($K_t$) / $147.12\text{ MPa}$ ($K_f$) | **$4.22\times$ ($K_t$) / $4.83\times$ ($K_f$)** ($SF_{\text{Goodman}} = 5.68\times$) | $\delta_{\text{tip}} = 0.0349 / 0.0426\text{ mm}$ | **PASS** |
| **1B. Lower Bearing Pedestal ($Z=8.5\text{ mm}$ `R0.30` Fillet — Rapid Slew)** | AISI 4340 Norm ($710 / 1110\text{ MPa}$) | $191.28\text{ MPa}$ ($K_t$) / $167.13\text{ MPa}$ ($K_f$) | **$3.71\times$ ($K_t$) / $4.25\times$ ($K_f$)** ($SF_{\text{Goodman}} = 5.09\times$) | $232.66\text{ MPa}$ ($K_t$) / $203.25\text{ MPa}$ ($K_f$) | **$3.05\times$ ($K_t$) / $3.49\times$ ($K_f$)** ($SF_{\text{Goodman}} = 4.19\times$) | $\delta_{\text{tip}} = 0.0485 / 0.0591\text{ mm}$ | **PASS** |
| **2A-1. Blade Root $D3.0\text{ mm}$ Trunnion Net Section at $D1.0\text{ mm}$ Crosshole** | 7075-T6 Al ($505 / 572\text{ MPa}$) | $144.82\text{ MPa}$ (clamp-assisted $K_f$) | **$3.49\times$** (assisted $K_f$) / $1.90\times$ (unassisted $K_f$) | $198.84\text{ MPa}$ (clamp-assisted $K_f$) | **$2.54\times$** (assisted $K_f$) / $1.56\times$ (unassisted $K_f$) | — | **PASS** |
| **2A-2. ISO 8750 $D1\times 8\text{ mm}$ Heavy-Duty Coiled Pin Double Shear** | ISO 8750 Spring Steel ($750\text{ N}$ min break) | $\tau = 150.92\text{ MPa}$ ($67.91\text{ MPa}$ assisted) | **$3.16\times$ Ult / $2.53\times$ Yield** ($5.62\times$ assisted) | $\tau = 184.37\text{ MPa}$ ($99.48\text{ MPa}$ assisted) | **$2.59\times$ Ult / $2.07\times$ Yield** ($3.84\times$ assisted) | — | **PASS** |
| **2B. Blade $OD6.0 \times ID4.0\text{ mm}$ Carbon-Epoxy Spar ($L=220\text{ mm}$)** | UD Carbon/Epoxy ($E=70\text{ GPa}, \sigma_u=600\text{ MPa}$) | $106.11\text{ MPa}$ (mid-span peak) | **$5.65\times$** | $129.62\text{ MPa}$ (mid-span peak) | **$4.63\times$** | $\delta_{\text{mid}} = 2.55 / 3.11\text{ mm}$ ($L/86.4$) | **PASS** |
| **3A. Offset Blade Pitch Arm ($Z = -22.075\text{ mm}$ Cantilever Web)** | 7075-T6 Al ($505\text{ MPa}$) | $26.98\text{ MPa}$ ($K_t$) / $19.55\text{ MPa}$ (nom) | **$18.71\times$ ($K_t$) / $25.83\times$ (nom)** | $32.96\text{ MPa}$ ($K_t$) / $23.89\text{ MPa}$ (nom) | **$15.32\times$ ($K_t$) / $21.14\times$ (nom)** | $\delta_{\text{ball}} = 0.0109 / 0.0133\text{ mm}$ | **PASS** |
| **3B. Pitch-Link $OD2.0 \times ID1.0\text{ mm}$ Carbon Tube Euler Buckling** | Carbon/Epoxy ($P_{\text{cr}} = 159.2\text{ N}$ pin / $220.4\text{ N}$ eff) | $11.70\text{ MPa}$ ($27.56\text{ N}$ comp) | **$5.78\times$ (pinned) / $8.00\times$ (eff)** ($10.55\times$ sin) | $14.29\text{ MPa}$ ($33.67\text{ N}$ comp) | **$4.73\times$ (pinned) / $6.54\times$ (eff)** ($8.64\times$ sin) | — | **PASS** |
| **3C. Oldham Floating Disk Tongues ($R_{\min} = 28\text{ mm}$ Engagement)** | POM Delrin ($\sigma_y = 63\text{ MPa}$) | $\sigma_{\text{vm}} = 1.74\text{ MPa}$, $p_c = 1.48\text{ MPa}$ | **$36.27\times$ (root) / $42.66\times$ (contact)** | $\sigma_{\text{vm}} = 2.12\text{ MPa}$, $p_c = 1.80\text{ MPa}$ | **$29.70\times$ (root) / $34.93\times$ (contact)** | $PV = 2.02 / 2.73\text{ MPa}\cdot\text{m/s}$ | **PASS** |
| **4A. X Actuator Drop Link (`BA_X_Actuator_Drop_Link`)** | 7075-T6 Al ($505\text{ MPa}$) [6061: $275\text{ MPa}$] | $10.49\text{ MPa}$ ($K_t$) / $7.39\text{ MPa}$ (nom) | **$48.15\times$** [6061: $26.22\times$] | $12.78\text{ MPa}$ ($K_t$) / $9.00\text{ MPa}$ (nom) | **$39.53\times$** [6061: $21.53\times$] | $\Delta e_X = 0.00453 / 0.00552\text{ mm}$ | **PASS** |
| **4B. Y Cross-Slot Drop Link (`BA_Y_Cross_Slot_Drop_Link`) & Bronze Shoe** | 7075-T6 Al ($505\text{ MPa}$) + C93200 Shoe | $3.89\text{ MPa}$ ($K_t$), $p_{\text{shoe}} = 0.308\text{ MPa}$ | **$129.90\times$** [6061: $70.74\times$], $PV = 0.025\text{ MPa}\cdot\text{m/s}$ | $4.74\text{ MPa}$ ($K_t$), $p_{\text{shoe}} = 0.376\text{ MPa}$ | **$106.61\times$** [6061: $58.06\times$], $PV = 0.031\text{ MPa}\cdot\text{m/s}$ | $\Delta e_Y = 0.01358 / 0.01653\text{ mm}$ | **PASS** |

---

## 5. Mandatory Shop-Drawing & Fabrication Notes (`SIM-001B`)

1. **Lower Stepped Bearing Pedestal Material (`Bench_Rotor/BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT`):**
   - **Mandatory Alloy:** Fabricate from **AISI 4140 / 4340 Quenched & Tempered Alloy Steel ($28\text{–}32\text{ HRC}$, $\sigma_y \ge 710\text{ MPa}$)** or **17-4PH Condition H900 ($\sigma_y = 1170\text{ MPa}$)**, and inspect the `R0.30 mm` step fillets at $Z = 8.5, 12.5, 17.5\text{ mm}$ (`Bench_Step_Transitions_Fillet_R0p30`, which reduce peak bending notch stress at $Z = 8.5\text{ mm}$ by $-46.3\%$).
   - **Do NOT Substitute Annealed 303/304 Austenitic Stainless Steel:** Annealed 303/304 SS ($\sigma_y = 240\text{ MPa}$) drops to $SF_y = 1.26\times$ under `1900 RPM` rapid slew, $1.03\times$ under `2100 RPM` burst slew, and $0.78\times$ at the `2640 RPM` adverse-tolerance proof bound.
2. **Blade Root Pitch-Arm Split Clamp & ISO 8750 $D1\times 8\text{ mm}$ Coiled Pin Assembly (`BD_RB_Part1.SLDPRT`):**
   - Torque the M2 split-clamp socket cap screw on `BD_RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE.SLDPRT` to achieve the $1200\text{ N}$ clamp preload ($0.360\text{–}0.540\text{ N}\cdot\text{m}$ friction slip capacity) before seating the **ISO 8750 $D1\times 8\text{ mm}$ heavy-duty coiled spring pin** ($750\text{ N}$ double-shear breaking capacity = $1.125\text{ N}\cdot\text{m}$ positive form-lock backup).
3. **Tribological Lubrication Protocol for Oldham Tongue Slots & Y Cross-Slot Bronze Shoe:**
   - **POM Delrin Oldham Floating Disk (`BD_RB_Oldham_Floating_Disk_PROTOTYPE.SLDPRT`):** Apply a light **PTFE/silicone synthetic grease** to the $4.00\text{ mm}$ tongues and $4.03\text{ mm}$ mating slots ($0.015\text{ mm}$ per-side clearance) prior to high-eccentricity runs ($v_{\text{slide,max}} = 1.37\text{–}1.51\text{ m/s}$, $p_c = 1.48\text{–}1.80\text{ MPa}$, $PV = 2.02\text{–}2.73\text{ MPa}\cdot\text{m/s}$) to maintain $\mu_{\text{Oldham}} \le 0.08$ and prevent thermal wear.
   - **Y Cross-Slot Sliding Shoe (`BA_Y_Bronze_Sliding_Shoe.SLDPRT`) & D8 Guide Bushings (`BA_Bronze_Bush_10_8_L15.SLDPRT`):** Machine the sliding shoe from **SAE 660 / UNS C93200 Bearing Bronze** (or oil-impregnated sintered bronze) and lightly lubricate the $8.00\text{ mm}$ cross-slot walls in `BA_Y_Cross_Slot_Drop_Link.SLDPRT` and the two $D8\text{ mm}$ guide shafts (`BA_D8_Guide_Shaft_L126.SLDPRT`) to keep $\mu \le 0.12$.
