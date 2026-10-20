import re
import sys
from pathlib import Path

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    kb_path = Path("CYCLOPROP_MASTER_KNOWLEDGE_BASE.md")
    content = kb_path.read_text(encoding="utf-8")

    print(f"Original content length: {len(content)} characters, {len(content.splitlines())} lines")

    # -------------------------------------------------------------
    # 1. Clean corrupted LaTeX control characters
    # -------------------------------------------------------------
    replacements = {
        '\x0barnothing': r'\varnothing',
        '\x0crac': r'\frac',
        '\x07lpha': r'\alpha',
        '\x07pprox': r'\approx',
        '\text': r'\text',
        '\theta': r'\theta',
        '\times': r'\times',
        '\tau': r'\tau',
        '\to': r'\to',
        'von Krmn': 'von Kármán',
        '49.4C (thermal margin 2.4x': '49.4°C (thermal margin 2.4×',
        'Class-H 120C limit': 'Class-H 120°C limit',
        '< 80C': '< 80°C',
        '65C for 6 hours': '65°C for 6 hours',
        '80C; snap-on': '80°C; snap-on',
        '< 50C': '< 50°C',
        '2.4x thermal margin': '2.4× thermal margin',
        '2.4x vs Class-H': '2.4× vs Class-H',
    }

    for bad, good in replacements.items():
        content = content.replace(bad, good)

    # Clean double horizontal rules
    content = re.sub(r'---\s*\n\s*\n\s*---\s*\n', '---\n\n', content)

    # -------------------------------------------------------------
    # 2. Fix Section 6.5.1: Consolidate Drive Shaft Tables
    # -------------------------------------------------------------
    # In Section 6.5.1, replace the dual consecutive tables (260mm and 275mm)
    # with a single, clear, authoritative As-Built 275mm table.
    old_dual_tables_regex = r'###### Complete As-Built Drive Shaft Feature & Coordinate Map \(\$Z = -20\.00\$ to \$\+240\.00\\text\{ mm\}\).*?###### Final As-Built Drive Shaft Extension \(275\.00 mm Overall Length, \$Z = -20\.00\$ to \$\+255\.00\\text\{ mm\}\)\s*\n\s*Under the Rev 2\.0 / Rev 3\.0 As-Built Freeze \(incorporating the \$Z = 239\.63\\text\{ mm\}\$ Inner Carriage Plate hard boundary discovery\), the Drive Shaft was extended from \*\*\$260\.00\\text\{ mm\}\$ to \$275\.00\\text\{ mm\}\*\* along the \$Z\$-axis, providing structural bearing seating inside Pillar 2 \(\$Z = 241\.50\\text\{ to \} 252\.50\\text\{ mm\}\):\s*\n\s*\| Feature Name \| As-Built Z-Start \(mm\) \| As-Built Z-End \(mm\) \| Length \(mm\) \| Outer \$\\varnothing\$ / Feature \| Position from Left End \(mm\) \| Function & Mating Component \|\s*\n\| :--- \| :---: \| :---: \| :---: \| :---: \| :---: \| :--- \|\s*\n(?:\|.*?\n)+'

    new_single_table = """###### Canonical As-Built Drive Shaft Feature & Coordinate Map (275.00 mm Overall Length, $Z = -20.00$ to $+255.00\\text{ mm}$)

> **Engineering Design Evolution Note:** Under the Rev 2.0 / Rev 3.0 As-Built Freeze (following measurement of the $Z = 239.63\\text{ mm}$ Inner Carriage Plate hard boundary in SolidWorks), the Drive Shaft was extended by $+15.00\\text{ mm}$ from **$260.00\\text{ mm}$ to $275.00\\text{ mm}$** ($Z = -20.00\\text{ mm} \\to +255.00\\text{ mm}$). In the preliminary $260.00\\text{ mm}$ concept, Groove 3 ($Z = 226.00\\text{ mm}$) and Groove 4 ($Z = 231.95\\text{ mm}$) sat inside the carriage zone; the 275 mm extension shifted the upper bearing journal outward to $Z = 242.00\\text{--}247.00\\text{ mm}$, providing solid, rigid bearing seating centered inside Pillar 2 ($Z = 241.50\\text{ to } 252.50\\text{ mm}$).

| Feature Name | As-Built Z-Start (mm) | As-Built Z-End (mm) | Length (mm) | Outer $\\varnothing$ / Feature | Position from Left End (mm) | Prelim Rev 1.1 Z (mm) | Function & Mating Component |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Motor Drive D-Flats** | $-20.00$ | $-13.00$ | $7.00$ | Flat-to-flat: $5.00\\text{ mm}$ | $0.00\\text{--}7.00$ | $0.00\\text{--}7.00$ | Flex-coupler clamping ($0.5\\text{ mm}$ cut per side) |
| **Cylindrical Shoulder** | $-13.00$ | $-12.00$ | $1.00$ | $\\varnothing 6.00\\text{ mm}$ | $7.00\\text{--}8.00$ | $7.00\\text{--}8.00$ | Solid land separating drive flat from Groove 1 |
| **Groove 1 (Circlip)** | $-12.00$ | $-11.20$ | $0.80$ | $\\varnothing 5.00\\text{ mm}$ root | $8.00\\text{--}8.80$ | $8.00\\text{--}8.80$ | DIN 471 retaining ring (outer side of Lower Bearing) |
| **Lower Bearing Seat** | $-11.20$ | $-6.05$ | $5.15$ | $\\varnothing 6.00\\text{ mm}$ (j6 fit) | $8.80\\text{--}13.95$ | $8.80\\text{--}13.95$ | Chassis Lower MR686ZZ Bearing (center at **$Z = -8.63\\text{ mm}$**) |
| **Groove 2 (Circlip)** | $-6.05$ | $-5.25$ | $0.80$ | $\\varnothing 5.00\\text{ mm}$ root | $13.95\\text{--}14.75$ | $13.95\\text{--}14.75$ | DIN 471 retaining ring (inner side of Lower Bearing) |
| **Hub Spacer Land** | $-5.25$ | $-1.50$ | $3.75$ | $\\varnothing 6.00\\text{ mm}$ | $14.75\\text{--}18.50$ | $14.75\\text{--}18.50$ | Clearance land to lower endplate outer face |
| **Lower Disc Seat** | $-1.50$ | $0.00$ | $1.50$ | $\\varnothing 6.00\\text{ mm}$ | $18.50\\text{--}20.00$ | $18.50\\text{--}20.00$ | Lower Endplate (Disc 1) web structural seating |
| **ACTIVE BLADE SPAN** | **$0.00$** | **$220.00$** | **$220.00$** | **$\\varnothing 6.00\\text{ mm}$** | **$20.00\\text{--}240.00$** | **$20.00\\text{--}240.00$** | **Aerodynamic Rotor Blade Span ($b = 220.00\\text{ mm}$)** |
| **Upper Disc Seat** | $220.00$ | $221.50$ | $1.50$ | $\\varnothing 6.00\\text{ mm}$ | $240.00\\text{--}241.50$ | $240.00\\text{--}241.50$ | Upper Endplate (Disc 2) web structural seating |
| **Pitch Mechanism Land**| $221.50$ | $241.20$ | $19.70$ | $\\varnothing 6.00\\text{ mm}$ | $241.50\\text{--}261.20$ | $241.50\\text{--}246.00$ | Clear passage through Control Ring & Carriage Plate ($Z \\le 239.63$) |
| **Groove 3 (Circlip)** | $241.20$ | $242.00$ | $0.80$ | $\\varnothing 5.00\\text{ mm}$ root | $261.20\\text{--}262.00$ | $246.00\\text{--}246.80$* | DIN 471 retaining ring (inner side of Upper Bearing) |
| **Upper Bearing Seat** | $242.00$ | $247.00$ | $5.00$ | $\\varnothing 6.00\\text{ mm}$ (j6 fit) | $262.00\\text{--}267.00$ | $246.80\\text{--}251.95$* | Chassis Upper MR686ZZ Bearing (seated in Pillar 2) |
| **Groove 4 (Circlip)** | $247.00$ | $247.80$ | $0.80$ | $\\varnothing 5.00\\text{ mm}$ root | $267.00\\text{--}267.80$ | $251.95\\text{--}252.75$* | DIN 471 retaining ring (outer side of Upper Bearing) |
| **Shaft Terminus Tip** | $247.80$ | $255.00$ | $7.20$ | $\\varnothing 6.00\\text{ mm}$ tip | $267.80\\text{--}275.00$ | $252.75\\text{--}260.00$* | Upper terminus extension with $0.3\\text{ mm} \\times 45^\\circ$ lead-in chamfer |
"""

    if re.search(old_dual_tables_regex, content, re.DOTALL):
        content = re.sub(old_dual_tables_regex, new_single_table, content, count=1, flags=re.DOTALL)
        print("Successfully consolidated Section 6.5.1 Drive Shaft tables!")
    else:
        print("Warning: regex for Section 6.5.1 dual tables did not match exactly, searching alternate...")

    # -------------------------------------------------------------
    # 3. Deduplicate Section 11 Rev 3.0 summary bullets
    # -------------------------------------------------------------
    # Notice lines 1880-1884 vs lines 1891-1895:
    duplicate_rev3_block = r"""- \*\*Autonomous Agent Prompts for Linux & IIT Ropar:\*\* Authored and version-controlled v3 autonomous handoff prompts: `docs/OpenFOAM_Agent_Prompt\.md` \(for headless execution on Ubuntu Linux\) and `docs/ANSYS_Fluent_Agent_Prompt\.md` \(for ANSYS Fluent execution on IIT Ropar lab workstations\)\.\s*\n- \*\*Airfoil Switch to NACA 0012:\*\* Profile drag reduced \(\$C_\{d0\} = 0\.016\$\), raising Figure of Merit from \$0\.744 \\to 0\.768\$\.\s*\n- \*\*Bushings Solution:\*\* Replaced trunnion miniature ball bearings with Igus Iglide J polymer bushings to eliminate false brinelling failures\.\s*\n- \*\*Aerodynamic Fairings:\*\* Added teardrop fairings over chassis pillars, reducing flow blockage from \$0\.92 \\to 0\.96\$ \(\$\+0\.48\\text\{ N\}\$ thrust recovered\)\.\s*\n- \*\*Cooling Scoop:\*\* Added 3D printed rotor downwash duct to maintain motor coil temperatures < 50°C\.\s*\n- \*\*Mass Reduction:\*\* Rigorous mass budget established at \$301\.4\\text\{--\}307\.4\\text\{ g\}\$, achieving \$T/W = 3\.98\\text\{--\}4\.06\$ at hover and \$4\.98\\text\{--\}5\.08\$ at burst\."""

    replacement_block = """- **Autonomous Agent Prompts for Linux & IIT Ropar:** Authored and version-controlled v3 autonomous handoff prompts: `docs/OpenFOAM_Agent_Prompt.md` (for headless execution on Ubuntu Linux) and `docs/ANSYS_Fluent_Agent_Prompt.md` (for ANSYS Fluent execution on IIT Ropar lab workstations)."""

    if re.search(duplicate_rev3_block, content):
        content = re.sub(duplicate_rev3_block, replacement_block, content, count=1)
        print("Successfully removed duplicate Rev 3.0 summary bullets in Section 11!")
    else:
        print("Note: duplicate Rev 3.0 block search did not match verbatim, checking alternate pattern...")

    # -------------------------------------------------------------
    # 4. Deduplicate Section 14 File Registry Table
    # -------------------------------------------------------------
    # The 16 CFD rows repeated twice back-to-back:
    duplicate_sec14_rows = r"""(\| \*\*Individual Airfoil Polar CSVs \(5x\)\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\results\\naca0012_openfoam_Re95k\.csv` \| Clean tabulated polar files \(\$C_l, C_d, C_m\$ vs \$\\alpha\$\) for NACA 0009, 0012, 0015, 0018, and 63-012A\. \|\s*\n)\| \*\*CFD Airfoil Coordinates Generator\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\gen_airfoil_coords\.py` \| Generates verified \.dat and \.txt coordinate files for all 5 airfoils; includes UIUC Report 824 cubic spline interpolation for NACA 63-012A\. \|\s*\n\| \*\*CFD Coordinate Verification Audit\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\audit_coords\.py` \| Quantifies contour errors between generated airfoil curves and experimental UIUC wind tunnel datasets\. \|\s*\n\| \*\*OpenFOAM Structured Mesh Generator\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\generate_mesh\.py` \| Generates high-resolution structured C-grid blockMeshDict with wall clustering \(\$y\^\+ < 1\$\) across arbitrary angles of attack\. \|\s*\n\| \*\*C-Grid BlockMesh Utility Script\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\generate_cgrid\.py` \| Supporting blockMesh generator script creating 2D computational flow domains for simpleFoam\. \|\s*\n\| \*\*OpenFOAM Master Sweep Automation\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\run_openfoam_sweep\.py` \| Orchestrates multi-blade, multi-angle OpenFOAM simpleFoam sweeps across all 85 simulation cases\. \|\s*\n\| \*\*Blade 1 \(NACA 0012\) Sweep Runner\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\run_blade1_sweep\.py` \| Dedicated sweep runner executing the 17-angle sweep for NACA 0012 with automated mesh and solver execution\. \|\s*\n\| \*\*Blade 2–5 Dedicated Sweep Runners\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\run_blade2_sweep\.py` to `run_blade5_sweep\.py` \| Dedicated automation scripts executing sweeps for NACA 0015, NACA 0018, NACA 63-012A, and NACA 0009\. \|\s*\n\| \*\*Iteration Data Logging Utility\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\log_iteration_data\.py` \| Parses `log\.simpleFoam` and `coefficient\.dat` to log residuals and aerodynamic force histories per iteration into CSVs\. \|\s*\n\| \*\*CFD Visual Dashboard Generator\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\plot_cfd_results\.py` \| Generates 4-panel aerodynamic dashboard visuals displaying residuals, \$C_l\$, \$C_d\$, and \$C_m\$ convergence per case\. \|\s*\n\| \*\*Airfoil Geometry Visual Comparison\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\plot_airfoil_comparison\.py` \| Generates 1:1 true-scale profile overlays and cross-sectional thickness distribution plots \(NACA 0012 vs NACA 0015\)\. \|\s*\n\| \*\*CFD Polar Integration & BEMT Tool\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\integrate_cfd_polars\.py` \| Loads CFD polar CSVs, runs cross-validation checks, and plugs polars into the BEMT solver via `CFDPolarAeroModel`\. \|\s*\n\| \*\*Cycle-Averaged BEMT Verification\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\scripts\\test_bemt_with_cfd\.py` \| Evaluates BEMT hover thrust and Figure of Merit using cycle-averaged CFD polars across all 5 candidate blades\. \|\s*\n\| \*\*Linux OpenFOAM Autonomous Prompt\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\docs\\OpenFOAM_Agent_Prompt\.md` \| Autonomous self-contained prompt guiding the Linux subagent through OpenFOAM installation, meshing, solving, and post-processing\. \|\s*\n\| \*\*ANSYS Fluent Lab Autonomous Prompt\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\docs\\ANSYS_Fluent_Agent_Prompt\.md` \| Autonomous prompt providing SpaceClaim modeling, meshing, and journal setup for ANSYS Fluent at the IIT Ropar lab\. \|\s*\n\| \*\*Master CFD Results Database\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\results\\master_cfd_results\.csv` \| Master database containing converged \$C_l, C_d, C_m\$, residual values, and log paths for all 85 simulation runs\. \|\s*\n\| \*\*Individual Airfoil Polar CSVs \(5x\)\*\* \| `c:\\Users\\Adarsh Singh\\CycloProp\\cfd_study\\results\\naca0012_openfoam_Re95k\.csv` \| Clean tabulated polar files \(\$C_l, C_d, C_m\$ vs \$\\alpha\$\) for NACA 0009, 0012, 0015, 0018, and 63-012A\. \|"""

    if re.search(duplicate_sec14_rows, content):
        content = re.sub(duplicate_sec14_rows, r'\1', content, count=1)
        print("Successfully removed duplicated CFD rows in Section 14 File Registry!")
    else:
        print("Warning: regex for Section 14 duplicate rows did not match verbatim.")

    # -------------------------------------------------------------
    # 5. Harmonize Dimensions & Specifications
    # -------------------------------------------------------------
    # Shaft length: Standardize 275.00 mm (with 260 mm noted as historical prelim)
    # Replace in Section 2.1 Table:
    content = content.replace(
        "| **Shaft Length** | $L$ | $260.0$ | **$260.0$** | mm |",
        "| **Shaft Length** | $L$ | $260.0$ | **$275.0$** | mm | Sized to $275.0\\text{ mm}$ ($Z = -20 \\to +255$) to seat upper bearing inside Pillar 2 |"
    )

    # In Section 6.1:
    content = content.replace(
        "`03_Drive_Shaft.SLDPRT` / `3-Drive_Shaft.SLDPRT` (Qty: 1) — $\\varnothing 6\\text{ mm} \\times 260\\text{ mm}$ precision-ground Ti-6Al-4V / 4130 steel shaft.",
        "`03_Drive_Shaft.SLDPRT` / `3-Drive_Shaft.SLDPRT` (Qty: 1) — $\\varnothing 6\\text{ mm} \\times 275.00\\text{ mm}$ precision-ground Ti-6Al-4V / 4130 steel shaft (extended from prelim $260\\text{ mm}$ to seat upper bearing in Pillar 2)."
    )

    # In Section 6.5.9 Master Equation Table:
    content = content.replace(
        "| `L_SHAFT` | `260.00 mm` | Total central drive shaft length along $Z$-axis |",
        "| `L_SHAFT` | `275.00 mm` | Total central drive shaft length along $Z$-axis ($Z = -20.00 \\to +255.00\\text{ mm}$; extended from prelim $260\\text{ mm}$) |"
    )

    # In Section 6.5.13:
    content = content.replace(
        "Ground cylinder **`Ø 6.00 mm`** h7 ($-0.000 / -0.012\\text{ mm}$) $\\times$ overall length **`260.00 mm`**.",
        "Ground cylinder **`Ø 6.00 mm`** h7 ($-0.000 / -0.012\\text{ mm}$) $\\times$ overall length **`275.00 mm`** ($Z = -20.00\\text{ to } +255.00\\text{ mm}$; extended from prelim $260.00\\text{ mm}$)."
    )

    # In Section 9.1 BOM table: Line 3
    content = content.replace(
        "| 3 | **Central Drive Shaft** | $\\varnothing 6\\text{ mm} \\times 260\\text{ mm}$, 4130 Chromoly / Ti | 1 | 28.00 | 28.00 | 9.29% | Drivetrain |",
        "| 3 | **Central Drive Shaft** | $\\varnothing 6\\text{ mm} \\times 275\\text{ mm}$, 4130 Chromoly / Ti | 1 | 28.00 | 28.00 | 9.29% | Drivetrain |"
    )

    # In Section 9.1 BOM table: Line 14 Chassis Frame
    content = content.replace(
        "| 14 | **Structural Chassis Frame** | PA12-CF30 U-channel ($230\\times 60\\times 70$) | 1 | 32.50 | 32.50 | 10.78% | Structure |",
        "| 14 | **Structural Chassis Frame** | PA12-CF30 Inverted-U cradle (Span $249.5\\text{ mm}$, width $271.5\\text{ mm}$) | 1 | 32.50 | 32.50 | 10.78% | Structure |"
    )

    # In Section 14 File Registry: Line for 3-Drive_Shaft.SLDPRT
    content = content.replace(
        "Rev 1.1 master shaft model ($\varnothing 6 \times 260\text{ mm}$, Ti-6Al-4V, DIN 471 grooves).",
        "As-Built Rev 3.0 shaft model ($\varnothing 6 \times 275.00\text{ mm}$, Ti-6Al-4V / 4130, DIN 471 grooves, $Z = -20 \\to +255\text{ mm}$)."
    )

    # In Section 14 File Registry: Line for 6-Mounting_Chassis_Frame.SLDPRT
    content = content.replace(
        "Structural cradle chassis frame ($230\times 60\times 70\text{ mm}$) with 4 bearing blocks, motor mount, and dual servo pockets.",
        "Inverted-U cradle chassis frame (Inside span $249.50\text{ mm}$, width $271.50\text{ mm}$, height $230\text{ mm}$) with 4 bearing blocks, motor cross-mount, and dual servo pockets."
    )

    # Clean up Section 6.5.8 heading to clarify it as Historical Rev 2.0
    content = content.replace(
        "#### 6.5.8 Part 6 — Mounting Chassis Frame Architecture & Dimensional Register (`06_Mounting_Chassis_Frame.SLDPRT` / `6-Mounting_Chassis_Frame.SLDPRT`)",
        "#### 6.5.8 Part 6 — Mounting Chassis Frame: Historical Rev 2.0 Box Frame vs. Superseded Baseline (`06_Mounting_Chassis_Frame.SLDPRT`)\n> [!WARNING]\n> **Historical Revision Notice:** The enclosed U-channel box ($230 \\times 60 \\times 70\\text{ mm}$) documented below was the preliminary Rev 2.0 concept. Interference evaluation under ECO-003 revealed that the $\\varnothing 200\\text{ mm}$ rotor collided through the floor and the bearing span was shorter than the blade span. This geometry is **completely superseded** by the **Inverted-U Goalpost Cradle Frame** ($249.50\\text{ mm}$ inside span, $271.50\\text{ mm}$ outside width) documented in Section 6.5.8.1."
    )

    kb_path.write_text(content, encoding="utf-8")
    print(f"Successfully wrote cleaned master knowledge base: {len(content)} characters, {len(content.splitlines())} lines")

if __name__ == '__main__':
    main()
