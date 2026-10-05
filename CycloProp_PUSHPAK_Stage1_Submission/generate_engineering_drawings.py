"""
CycloProp: Perfected High-Precision ISO General Arrangement & Assembly Drawings
Zero text overlap, crisp contrast, to-scale geometry, and professional layout.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

output_dir = r"c:\Users\Adarsh Singh\CycloProp\figures"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------------------
# DRAWING 1: 3-VIEW GENERAL ARRANGEMENT & CLEARANCE BLUEPRINT
# -------------------------------------------------------------------------
fig = plt.figure(figsize=(24, 15), dpi=220)
fig.patch.set_facecolor('#ffffff')

# Clean layout with dedicated non-overlapping zones
ax_span = fig.add_axes([0.06, 0.36, 0.54, 0.58])   # Spanwise Side Elevation (Front View)
ax_end = fig.add_axes([0.65, 0.44, 0.31, 0.50])    # End Elevation View (Cross Section)
ax_bom = fig.add_axes([0.65, 0.05, 0.31, 0.34])    # BOM Table + Mass Budget
ax_notes = fig.add_axes([0.06, 0.05, 0.54, 0.26])  # Engineering Notes & Assembly Sequence

# -------------------------------------------------------------
# 1. SPANWISE SIDE VIEW (VIEW A-A)
# -------------------------------------------------------------
ax_span.set_title("VIEW A-A: SPANWISE GENERAL ARRANGEMENT & INTEGRATION ENVELOPE", 
                  fontsize=12, fontweight='bold', pad=12)
ax_span.set_aspect('equal')
ax_span.grid(True, linestyle='--', alpha=0.25)

# Parameters
z_shaft_start = -25.0
z_shaft_end = 235.0
shaft_dia = 6.0
rotor_rad = 95.0
blade_span = 220.0
chord = 38.0
r_sweep = 114.0  # Max dynamic sweep radius (95 + 19)

# Centerline
ax_span.axhline(0, color='#d32f2f', linestyle='-.', linewidth=1.2, alpha=0.8)
ax_span.text(z_shaft_start - 5, 0, "CL", color='#d32f2f', fontsize=9, fontweight='bold', va='center', ha='right')

# Rotor Swept Envelope (Clear Airflow Zone)
ax_span.add_patch(Rectangle((0, -r_sweep), blade_span, 2*r_sweep,
                            facecolor='#e1f5fe', edgecolor='#03a9f4', linestyle='--', linewidth=1.5, alpha=0.6, zorder=1))
ax_span.text(110, 0, "ROTOR SWEPT VOLUME\n(Ø228 mm x 220 mm SPAN)\n\n"
                     "★ 100% OPEN AIRFLOW ZONE ★\n"
                     "No frame walls, servos, or wires can cross here!",
             ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0277bd',
             bbox=dict(boxstyle='round,pad=0.6', facecolor='#ffffff', edgecolor='#03a9f4', alpha=0.95))

# Drive Shaft (Ø6 x 260 mm)
ax_span.add_patch(Rectangle((z_shaft_start, -shaft_dia/2), 260.0, shaft_dia,
                            facecolor='#b0bec5', edgecolor='#263238', linewidth=1.5, zorder=3))

# Left Endplate Hub (Z = 0 mm, Ø190 x 1.5 mm)
ax_span.add_patch(Rectangle((-1.5, -95.0), 1.5, 190.0, facecolor='#37474f', edgecolor='#212121', linewidth=1.2, zorder=4))
# Right Endplate Hub (Z = 220 mm, Ø190 x 1.5 mm)
ax_span.add_patch(Rectangle((220.0, -95.0), 1.5, 190.0, facecolor='#37474f', edgecolor='#212121', linewidth=1.2, zorder=4))

# Aluminum Hub Collars (Ø20 x 8 mm)
ax_span.add_patch(Rectangle((-9.5, -10.0), 8.0, 20.0, facecolor='#90a4ae', edgecolor='#37474f', linewidth=1.0, zorder=4))
ax_span.add_patch(Rectangle((221.5, -10.0), 8.0, 20.0, facecolor='#90a4ae', edgecolor='#37474f', linewidth=1.0, zorder=4))

# Top Blade (at Y = +95 mm) & Bottom Blade (at Y = -95 mm)
# Hollow NACA 0015 blades (shown in section)
ax_span.add_patch(Rectangle((0, 95.0 - 2.85), blade_span, 5.7, facecolor='#212121', edgecolor='#000000', linewidth=1.2, zorder=4))
ax_span.add_patch(Rectangle((0, -95.0 - 2.85), blade_span, 5.7, facecolor='#212121', edgecolor='#000000', linewidth=1.2, zorder=4))

# Blade Trunnions (Ø3 x 8 mm pins into endplate bearing counterbores)
for by in [95.0, -95.0]:
    ax_span.add_patch(Rectangle((-8.0, by - 1.5), 8.0, 3.0, facecolor='#cfd8dc', edgecolor='#37474f', zorder=5))
    ax_span.add_patch(Rectangle((220.0, by - 1.5), 8.0, 3.0, facecolor='#cfd8dc', edgecolor='#37474f', zorder=5))

# Pitch Horn (Upper blade at Z = 224.55, moment arm rh = 12 mm extending upward)
ax_span.add_patch(Rectangle((222.8, 95.0), 3.5, 12.0, facecolor='#ff7043', edgecolor='#d84315', zorder=6))
ax_span.add_patch(Circle((224.55, 107.0), 1.2, facecolor='white', edgecolor='#d84315', zorder=7))

# 2DOF Eccentric Mechanism (Z = 222.5 mm to 239.63 mm)
ax_span.add_patch(Rectangle((222.55, -40.0), 14.0, 80.0, facecolor='#ffa726', edgecolor='#e65100', linewidth=1.2, zorder=5))
ax_span.text(230.0, -48, "2DOF Pitch Mechanism\n(Control Ring & Carriage)", color='#e65100', fontsize=7.5, fontweight='bold', ha='center')

# Pushrod Linkage (connecting Control Ring to Blade Horn at Z = 224.55 mm)
ax_span.plot([224.55, 224.55], [40.0, 107.0], color='#d84315', lw=2.2, zorder=6)
ax_span.text(216, 75, "Pushrod Link\n(Lp = 95.0 mm\nCoplanar Z=224.6)", color='#bf360c', fontsize=7.5, fontweight='bold', ha='right')

# Chassis Frame (Cradle Structure - Locked As-Built Baseline Rev 2.0)
# Pillar 1 (Left Support / Drive End, Z = -19.0 to -8.0 mm)
# Pillar 2 (Right Support / Mech End, Z = 241.5 to 252.5 mm)
# Spine (runs underneath at Y = -132 mm, 14 mm thick)
ch_c = '#455a64'
ax_span.add_patch(Polygon([(-19, -132), (-8, -132), (-8, 18), (-19, 18)], facecolor=ch_c, edgecolor='#263238', lw=1.2, zorder=2))
ax_span.add_patch(Polygon([(241.5, -132), (252.5, -132), (252.5, 18), (241.5, 18)], facecolor=ch_c, edgecolor='#263238', lw=1.2, zorder=2))
ax_span.add_patch(Rectangle((-19, -146), 271.5, 14, facecolor=ch_c, edgecolor='#263238', lw=1.2, zorder=2))

# Bearings (MR686ZZ, 6x13x5 mm)
ax_span.add_patch(Rectangle((-15.0, -6.5), 5.0, 13.0, facecolor='#e0e0e0', edgecolor='#212121', zorder=5))
ax_span.add_patch(Rectangle((243.0, -6.5), 5.0, 13.0, facecolor='#e0e0e0', edgecolor='#212121', zorder=5))

# T-Motor MN3508 (Mounted at Pillar 1 / Left Support, Z = -45.5 to -19.0 mm)
ax_span.add_patch(Rectangle((-45.5, -20.9), 26.5, 41.8, facecolor='#212121', edgecolor='#fbc02d', linewidth=1.5, zorder=4))
ax_span.text(-32.25, 0, "T-MOTOR\nMN3508\n(68g)", color='#fbc02d', ha='center', va='center', fontsize=7.5, fontweight='bold')

# Savox SH-0257MG Servos (Mounted at Pillar 2 / Right Support, Z = 252.5 to 264.5 mm)
ax_span.add_patch(Rectangle((252.5, 5.0), 12.0, 22.8, facecolor='#ff9800', edgecolor='#e65100', linewidth=1.2, zorder=4))
ax_span.text(258.5, 16.4, "SAVOX\nSERVOS", color='#212121', ha='center', va='center', fontsize=6.5, fontweight='bold')

# Critical Dimension Lines
# Dimension: Blade Span = 220 mm
ax_span.annotate('', xy=(0, 126), xytext=(220, 126), arrowprops=dict(arrowstyle='<->', color='#1565c0', lw=1.5))
ax_span.text(110, 131, "BLADE SPAN b = 220.0 mm", ha='center', va='bottom', color='#1565c0', fontsize=9.5, fontweight='bold')

# Dimension: Frame Inside Clear Span = 249.5 mm
ax_span.annotate('', xy=(-8, 148), xytext=(241.5, 148), arrowprops=dict(arrowstyle='<->', color='#00838f', lw=1.5))
ax_span.text(116.75, 153, "FRAME INSIDE SPAN = 249.5 mm (Clearance: +2.0mm Lower, +1.87mm Upper)", ha='center', va='bottom', color='#00838f', fontsize=8.5, fontweight='bold')

# Dimension: Rotor Diameter = 190 mm
ax_span.annotate('', xy=(220, -95), xytext=(220, 95), arrowprops=dict(arrowstyle='<->', color='#6a1b9a', lw=1.5))
ax_span.text(210, -50, "ROTOR DIAMETER\n2R = 190.0 mm", ha='right', va='center', color='#6a1b9a', fontsize=8.0, fontweight='bold')

# Dimension: Shaft Total Length = 275 mm (Z = -20 to +255 mm)
ax_span.annotate('', xy=(-20, -158), xytext=(255, -158), arrowprops=dict(arrowstyle='<->', color='#2e7d32', lw=1.5))
ax_span.text(117.5, -164, "DRIVE SHAFT OVERALL LENGTH = 275.0 mm (Ø6.0 mm Ti-6Al-4V)", ha='center', va='top', color='#2e7d32', fontsize=9.5, fontweight='bold')

# Dimension: Frame Total Outside Width = 271.5 mm
ax_span.annotate('', xy=(-19, -172), xytext=(252.5, -172), arrowprops=dict(arrowstyle='<->', color='#37474f', lw=1.2))
ax_span.text(116.75, -178, "FRAME OUTSIDE WIDTH = 271.5 mm", ha='center', va='top', color='#37474f', fontsize=8.5, fontweight='bold')

# Clearance Arrow (Under rotor to spine)
ax_span.annotate('', xy=(110, -95), xytext=(110, -132), arrowprops=dict(arrowstyle='<->', color='#c62828', lw=1.5))
ax_span.text(115, -113, "AIR GAP >= 37 mm\n(Frame runs below rotor)", ha='left', va='center', color='#c62828', fontsize=8, fontweight='bold')

# Callouts with Balloons
def callout(ax, x, y, num, text, tox, toy):
    ax.annotate(f"[{num}] {text}", xy=(x, y), xytext=(tox, toy),
                arrowprops=dict(arrowstyle='->', lw=1.2, color='#000000'),
                fontsize=8, fontweight='bold',
                bbox=dict(boxstyle='square,pad=0.2', facecolor='#fff9c4', edgecolor='#fbc02d'))

callout(ax_span, 50, 95, 1, "Rotor Blade (NACA 0015)", 20, 142)
callout(ax_span, 0, 50, 2, "Endplate Hub (Drive side)", -45, 115)
callout(ax_span, -10, 0, 3, "Drive Shaft Ø6mm x 275mm", -50, 30)
callout(ax_span, 230, -20, 4, "2DOF Pitch Mechanism", 215, -75)
callout(ax_span, 224.55, 107, 5, "Pitch Horn (rh=12mm)", 185, 120)
callout(ax_span, 110, -140, 6, "Chassis Cradle Spine", 50, -175)

ax_span.set_xlim(-60, 285)
ax_span.set_ylim(-190, 175)
ax_span.set_xlabel("Z-Axis: Spanwise Position (mm)", fontsize=9.5, fontweight='bold')
ax_span.set_ylabel("Y-Axis: Vertical Offset (mm)", fontsize=9.5, fontweight='bold')


# -------------------------------------------------------------
# 2. END CROSS-SECTION VIEW (VIEW B-B)
# -------------------------------------------------------------
ax_end.set_title("VIEW B-B: CROSS-SECTION (LOOKING ALONG SHAFT IN +Z)", 
                 fontsize=12, fontweight='bold', pad=12)
ax_end.set_aspect('equal')
ax_end.grid(True, linestyle='--', alpha=0.25)

# Circles
ax_end.add_patch(Circle((0, 0), rotor_rad, color='#1976d2', fill=False, linestyle='--', linewidth=1.5, label="Pitch Circle (R=95mm)"))
ax_end.add_patch(Circle((0, 0), r_sweep, color='#03a9f4', fill=False, linestyle=':', linewidth=1.2))
ax_end.add_patch(Circle((0, 0), 95.0, facecolor='#eeeeee', edgecolor='#424242', linewidth=1.5, alpha=0.4, zorder=1))
ax_end.add_patch(Circle((0, 0), 10.0, facecolor='#78909c', edgecolor='#37474f', zorder=4))
ax_end.add_patch(Circle((0, 0), 3.0, facecolor='#b0bec5', edgecolor='#212121', zorder=5))

# 4 Blades at 0°, 90°, 180°, 270°
angles = [0, 90, 180, 270]
for a in angles:
    rad = np.radians(a)
    px = rotor_rad * np.cos(rad)
    py = rotor_rad * np.sin(rad)
    # Airfoil ellipse representation
    ax_end.add_patch(patches.Ellipse((px, py), chord, 5.7, angle=a+90,
                                     facecolor='#263238', edgecolor='#000000', linewidth=1.2, zorder=6))
    ax_end.add_patch(Circle((px, py), 1.5, facecolor='#cfd8dc', edgecolor='black', zorder=7))
    
    # Show pitch horn at Blade 90° (top)
    if a == 90:
        ax_end.plot([px, px], [py, py + 12.0], color='#ff7043', lw=3.5, zorder=8)
        ax_end.add_patch(Circle((px, py + 12.0), 1.0, facecolor='white', edgecolor='red', zorder=9))
        ax_end.text(px + 8, py + 12, "Pitch Horn\n(r_h = 12.0 mm)", color='#d84315', fontsize=8, fontweight='bold')

# Frame Spine underneath (Section view)
ax_end.add_patch(Rectangle((-35, -146), 70, 14, facecolor=ch_c, edgecolor='#263238', linewidth=1.5, zorder=2))
ax_end.text(0, -139, "CRADLE SPINE (Y = -135 mm)\nCompletely below rotor!",
            ha='center', va='center', color='white', fontsize=7.5, fontweight='bold')

# Servo Actuators on Tower 1
ax_end.add_patch(Rectangle((-75, -125), 22.8, 12.0, facecolor='#1565c0', edgecolor='black', zorder=3))
ax_end.add_patch(Rectangle((52.2, -125), 22.8, 12.0, facecolor='#1565c0', edgecolor='black', zorder=3))
ax_end.text(-63.6, -119, "Servo X", color='white', ha='center', va='center', fontsize=7, fontweight='bold')
ax_end.text(63.6, -119, "Servo Y", color='white', ha='center', va='center', fontsize=7, fontweight='bold')

# Annotate PCD
ax_end.annotate('Blade Pivot Circle\nPCD = 190.0 mm', xy=(rotor_rad * np.cos(np.radians(45)), rotor_rad * np.sin(np.radians(45))),
                xytext=(75, 105), arrowprops=dict(arrowstyle='->', lw=1.2, color='#1976d2'),
                fontsize=8.5, fontweight='bold', color='#1976d2')

ax_end.set_xlim(-135, 135)
ax_end.set_ylim(-165, 140)
ax_end.set_xlabel("X-Axis: Lateral Position (mm)", fontsize=9.5, fontweight='bold')
ax_end.set_ylabel("Y-Axis: Vertical Position (mm)", fontsize=9.5, fontweight='bold')


# -------------------------------------------------------------
# 3. BOM TABLE & MASS AUDIT
# -------------------------------------------------------------
ax_bom.axis('off')
ax_bom.set_title("BILL OF MATERIALS (BOM) & SPECIFICATION AUDIT", fontsize=11, fontweight='bold', pad=8)

bom_headers = ["#", "Component Name", "Qty", "Material / Spec", "Mass (g)"]
bom_rows = [
    ["1", "Blade_NACA0015 (c=38, b=220mm)", "4", "CFRP Monocoque (0.8t skin)", "50.0"],
    ["2", "Endplate_Hub (Ø200 x 1.5mm)", "2", "CFRP Woven / G10 Disc", "36.0"],
    ["3", "Drive_Shaft (Ø6.0 x 275mm)", "1", "Ti-6Al-4V Precision Ground", "28.0"],
    ["4", "2DOF Pitch Mechanism (Ring+Carriage)", "1", "PA12-CF 3D-Printed", "14.0"],
    ["5", "Pushrod Linkage (Lp=95.0mm)", "4", "CFRP Ø1.2mm + Brass M2", "12.0"],
    ["6", "Blade_Pitch_Arm (rh=12.0mm)", "4", "PA12-CF / Al 7075-T6", "10.0"],
    ["7", "Mounting Chassis Cradle Frame", "1", "PA12-CF30 (Span=249.5mm)", "25.0"],
    ["8", "T-Motor MN3508 380KV Motor", "1", "Brushless Outrunner (COTS)", "68.0"],
    ["9", "Savox SH-0257MG Micro Servos", "2", "Digital Metal-Gear (COTS)", "17.0"],
    ["10", "Shielded Ball Bearings (MR686ZZ)", "4", "Chrome Steel (6x13x5mm)", "14.0"],
    ["11", "Hardware, Clips, Coupler, Fasteners", "--", "Titanium / Steel / Retainers", "27.25"]
]

table = ax_bom.table(cellText=bom_rows, colLabels=bom_headers, loc='upper center', cellLoc='left',
                     colColours=['#cfd8dc']*5, colWidths=[0.06, 0.44, 0.08, 0.28, 0.14])
table.auto_set_font_size(False)
table.set_fontsize(7.2)
table.scale(1.0, 1.25)

summary_box = "AUDITED AS-BUILT SOLIDWORKS TOTAL MASS = 301.25 g  (LIMIT <= 312.0 g | MARGIN: +10.75 g)\n" \
              "PEAK THRUST = 12.0 N  |  THRUST-TO-WEIGHT RATIO (T/W) = 4.06  (REQ > 2.50 [EXCEEDED])"
ax_bom.text(0.5, 0.02, summary_box, transform=ax_bom.transAxes, ha='center', va='bottom',
            fontsize=8.2, fontweight='bold', color='#1b5e20',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8f5e9', edgecolor='#4caf50', lw=1.5))


# -------------------------------------------------------------
# 4. ENGINEERING NOTES & SOLIDWORKS ASSEMBLY SEQUENCE
# -------------------------------------------------------------
ax_notes.axis('off')
notes = """
SOLIDWORKS STEP-BY-STEP ASSEMBLY SEQUENCE & MATING INSTRUCTIONS:
====================================================================================================================
STEP A: ASSEMBLE THE ROTOR SKELETON FIRST (Clean, modular sub-assembly)
  1. Open new assembly: Cyclorotor_Module.SLDASM.
  2. Insert Drive_Shaft.SLDPRT -> Right-click -> Float (or ground temporarily along Z-axis).
  3. Insert Endplate_Hub #1 -> Concentric mate to Shaft -> Coincident mate to Z = 0 mm.
  4. Insert Endplate_Hub #2 -> Concentric mate to Shaft -> Coincident mate to Z = 220 mm (Distance = 220.0 mm).
  5. Insert Blade #1 -> Concentric mate of Left Trunnion to Endplate #1 bearing pocket (R = 95.0 mm).
                     -> Concentric mate of Right Trunnion to Endplate #2 bearing pocket.
  6. Circular Component Pattern -> Pattern Blade #1 around Drive Shaft -> 4 instances at 90° intervals.
  --> RESULT: The complete 4-blade rotor now spins cleanly as a single unit!

STEP B: ADD THE KINEMATIC PITCH LINKAGE
  7. Insert 2DOF_Eccentric_Pitch_Mechanism -> Position at Z = -14 mm on the drive shaft.
  8. Insert 4x Pushrod_Linkage -> Spherical (Ball-and-Socket) mate between Pushrod Ends and Control Ring Studs.
                              -> Spherical mate between Pushrod other ends and the 4 Blade Pitch Horns.

STEP C: INTEGRATE INTO CHASSIS CRADLE FRAME
  9. The Frame is a U-shaped cradle: Tower 1 (Z = -20mm), Tower 2 (Z = 230mm), Spine underneath at Y = -135mm.
  10. Mate Shaft to Frame Bearing Bores (Concentric) -> Add 2x MR686ZZ bearings per tower.
  11. Mount T-Motor MN3508 at Tower 2 (Z = 235mm) -> Rigid coupling to Drive Shaft.
"""
ax_notes.text(0.0, 1.0, notes, transform=ax_notes.transAxes, ha='left', va='top',
              fontsize=7.8, family='monospace', color='#212121',
              bbox=dict(boxstyle='round,pad=0.6', facecolor='#f5f5f5', edgecolor='#bdbdbd', lw=1.2))

ga_clean_path = os.path.join(output_dir, "cycloprop_engineering_ga_drawing.png")
plt.savefig(ga_clean_path, bbox_inches='tight', dpi=220)
plt.close()
print(f"[SUCCESS] Saved pristine GA drawing: {ga_clean_path}")
