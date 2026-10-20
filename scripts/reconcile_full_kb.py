import re
import sys
from pathlib import Path

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    kb_path = Path("CYCLOPROP_MASTER_KNOWLEDGE_BASE.md")
    content = kb_path.read_text(encoding="utf-8")

    # 1. Section 6.5.1 Drive Shaft Consolidation
    target_start = "###### Complete As-Built Drive Shaft Feature & Coordinate Map ($Z = -20.00$ to $+240.00\\text{ mm}$)"
    target_end_str = "| **Shaft Terminus Tip** | $247.80$ | $255.00$ | $7.20$ | $\\varnothing 6.00\\text{ mm}$ tip | $267.80\\text{--}275.00$ | Upper terminus extension with $0.3\\text{ mm} \\times 45^\\circ$ chamfer |"

    p1 = content.find(target_start)
    p2 = content.find(target_end_str)
    if p1 != -1 and p2 != -1:
        p2_end = p2 + len(target_end_str)
        replacement_table = """###### Canonical As-Built Drive Shaft Feature & Coordinate Map (275.00 mm Overall Length, $Z = -20.00$ to $+255.00\\text{ mm}$)

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
| **Shaft Terminus Tip** | $247.80$ | $255.00$ | $7.20$ | $\\varnothing 6.00\\text{ mm}$ tip | $267.80\\text{--}275.00$ | $252.75\\text{--}260.00$* | Upper terminus extension with $0.3\\text{ mm} \\times 45^\\circ$ lead-in chamfer |"""
        content = content[:p1] + replacement_table + content[p2_end:]
        print("Replaced Section 6.5.1 dual tables successfully!")

    # 2. Section 11 Duplicate 5 bullets
    dup_str = """- **Autonomous Agent Prompts for Linux & IIT Ropar:** Authored and version-controlled v3 autonomous handoff prompts: `docs/OpenFOAM_Agent_Prompt.md` (for headless execution on Ubuntu Linux) and `docs/ANSYS_Fluent_Agent_Prompt.md` (for ANSYS Fluent execution on IIT Ropar lab workstations).
- **Airfoil Switch to NACA 0012:** Profile drag reduced ($C_{d0} = 0.016$), raising Figure of Merit from $0.744 \\to 0.768$.
- **Bushings Solution:** Replaced trunnion miniature ball bearings with Igus Iglide J polymer bushings to eliminate false brinelling failures.
- **Aerodynamic Fairings:** Added teardrop fairings over chassis pillars, reducing flow blockage from $0.92 \\to 0.96$ ($+0.48\\text{ N}$ thrust recovered).
- **Cooling Scoop:** Added 3D printed rotor downwash duct to maintain motor coil temperatures $< 50^\\circ\\text{C}$.
- **Mass Reduction:** Rigorous mass budget established at $301.4\\text{--}307.4\\text{ g}$, achieving $T/W = 3.98\\text{--}4.06$ at hover and $4.98\\text{--}5.08$ at burst."""

    single_str = """- **Autonomous Agent Prompts for Linux & IIT Ropar:** Authored and version-controlled v3 autonomous handoff prompts: `docs/OpenFOAM_Agent_Prompt.md` (for headless execution on Ubuntu Linux) and `docs/ANSYS_Fluent_Agent_Prompt.md` (for ANSYS Fluent execution on IIT Ropar lab workstations)."""

    if dup_str in content:
        content = content.replace(dup_str, single_str)
        print("Replaced Section 11 duplicate bullets successfully!")

    # Write back
    kb_path.write_text(content, encoding="utf-8")
    print(f"Intermediate write completed: {len(content)} characters, {len(content.splitlines())} lines")

if __name__ == '__main__':
    main()
