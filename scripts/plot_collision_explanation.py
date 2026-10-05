"""
Visual comparison explaining why the previous CAD assembly collided,
and showing the exact, correct 3D arrangement of the 6 parts.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon

output_dir = r"c:\Users\Adarsh Singh\CycloProp\figures"
os.makedirs(output_dir, exist_ok=True)

fig, (ax_wrong, ax_right) = plt.subplots(1, 2, figsize=(20, 9), dpi=200)
fig.patch.set_facecolor('#ffffff')

# -------------------------------------------------------------
# LEFT: WHAT HAPPENED IN YOUR SCREENSHOT (THE ERROR)
# -------------------------------------------------------------
ax_wrong.set_title("WHAT HAPPENED IN YOUR SOLIDWORKS ASSEMBLY (COLLISION)", 
                   fontsize=12, fontweight='bold', color='#c62828', pad=12)
ax_wrong.set_aspect('equal')
ax_wrong.grid(True, linestyle='--', alpha=0.3)

# Shaft
ax_wrong.add_patch(Rectangle((-180, -3), 260, 6, facecolor='#b0bec5', edgecolor='#37474f', lw=1.5, zorder=2))
ax_wrong.text(-50, 8, "Drive Shaft Ø6 x 260mm", fontsize=8, color='#37474f', fontweight='bold')

# Frame Box in the middle
ax_wrong.add_patch(Rectangle((0, -70), 50, 140, facecolor='#ef9a9a', edgecolor='#b71c1c', lw=2.0, alpha=0.7, zorder=3))
ax_wrong.text(25, 0, "FRAME BOX\n(Walls in the middle\nof rotor span!)", 
              ha='center', va='center', fontsize=9, fontweight='bold', color='#b71c1c')

# Right Endplate
ax_wrong.add_patch(Rectangle((55, -95), 3, 190, facecolor='#424242', edgecolor='#212121', lw=1.5, zorder=4))
ax_wrong.text(62, 50, "Endplate Hub #1\n(Ø190 mm)", fontsize=8.5, fontweight='bold', color='#212121')

# Imaginary Left Endplate
ax_wrong.add_patch(Rectangle((-165, -95), 3, 190, facecolor='#9e9e9e', edgecolor='#616161', linestyle='--', lw=1.5, zorder=4))
ax_wrong.text(-160, 50, "Where Endplate #2\nwould need to go\n(220mm away)", fontsize=8, color='#616161')

# Blades chopping into the frame box!
ax_wrong.plot([-165, 55], [95, 95], color='#d32f2f', lw=3.0, linestyle='-', zorder=5)
ax_wrong.plot([-165, 55], [-95, -95], color='#d32f2f', lw=3.0, linestyle='-', zorder=5)

# Big red collision crosses
ax_wrong.scatter([25, 25], [95, -95], marker='X', s=350, color='#b71c1c', zorder=10)
ax_wrong.text(25, 110, "CRASH!\nBlade hits top of frame", ha='center', fontsize=9, fontweight='bold', color='#b71c1c')
ax_wrong.text(25, -115, "CRASH!\nBlade hits bottom of frame", ha='center', fontsize=9, fontweight='bold', color='#b71c1c')

# Explanation text box
bad_text = "ERROR DIAGNOSIS:\n" \
           "• The frame walls are sitting between Z = 0 and Z = 50 mm.\n" \
           "• But the 4 blades MUST span from Z = 0 to Z = 220 mm at R = 95 mm.\n" \
           "• As the shaft rotates, the blades smash directly into the frame box!"
ax_wrong.text(0.5, 0.05, bad_text, transform=ax_wrong.transAxes, ha='center', va='bottom',
              fontsize=8.5, family='monospace', color='#b71c1c',
              bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffebee', edgecolor='#ef5350', lw=1.5))

ax_wrong.set_xlim(-200, 100)
ax_wrong.set_ylim(-130, 140)
ax_wrong.set_xlabel("Z Position (mm)", fontsize=9, fontweight='bold')
ax_wrong.set_ylabel("Y Position (mm)", fontsize=9, fontweight='bold')


# -------------------------------------------------------------
# RIGHT: THE PROPER CRADLE FRAME ARCHITECTURE (NO COLLISIONS)
# -------------------------------------------------------------
ax_right.set_title("CORRECT ARCHITECTURE: CRADLE FRAME RUNS OUTSIDE ROTOR", 
                   fontsize=12, fontweight='bold', color='#2e7d32', pad=12)
ax_right.set_aspect('equal')
ax_right.grid(True, linestyle='--', alpha=0.3)

# Shaft
ax_right.add_patch(Rectangle((-20, -3), 260, 6, facecolor='#b0bec5', edgecolor='#37474f', lw=1.5, zorder=3))

# Left Endplate (Z = 0) & Right Endplate (Z = 220)
ax_right.add_patch(Rectangle((-1.5, -95), 1.5, 190, facecolor='#37474f', edgecolor='#212121', lw=1.2, zorder=4))
ax_right.add_patch(Rectangle((220, -95), 1.5, 190, facecolor='#37474f', edgecolor='#212121', lw=1.2, zorder=4))
ax_right.text(-5, 50, "Endplate #1\n(Z = 0)", ha='right', fontsize=8, fontweight='bold')
ax_right.text(225, 50, "Endplate #2\n(Z = 220)", ha='left', fontsize=8, fontweight='bold')

# 4 Blades spinning freely between endplates
ax_right.add_patch(Rectangle((0, 95 - 2.85), 220, 5.7, facecolor='#212121', edgecolor='#000000', lw=1.2, zorder=4))
ax_right.add_patch(Rectangle((0, -95 - 2.85), 220, 5.7, facecolor='#212121', edgecolor='#000000', lw=1.2, zorder=4))
ax_right.text(110, 0, "100% CLEAR AIRFLOW!\nBlades spin freely in open 220 mm space",
              ha='center', va='center', fontsize=9, fontweight='bold', color='#2e7d32',
              bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8f5e9', edgecolor='#81c784', lw=1.2))

# Cradle Frame (Towers at the ends, spine runs below)
c_c = '#455a64'
# Tower 1 (outside left endplate at Z = -18 mm)
ax_right.add_patch(Polygon([(-20, -135), (-12, -135), (-12, 15), (-20, 15)], facecolor=c_c, edgecolor='#263238', lw=1.2, zorder=2))
# Tower 2 (outside right endplate at Z = 228 mm)
ax_right.add_patch(Polygon([(228, -135), (236, -135), (236, 15), (228, 15)], facecolor=c_c, edgecolor='#263238', lw=1.2, zorder=2))
# Connecting spine below
ax_right.add_patch(Rectangle((-20, -145), 256, 10, facecolor=c_c, edgecolor='#263238', lw=1.2, zorder=2))
ax_right.text(110, -140, "CRADLE SPINE (Y = -140 mm): Connects both towers UNDER the rotor",
              ha='center', va='center', color='white', fontsize=7.5, fontweight='bold')

# T-Motor mounted at Tower 2
ax_right.add_patch(Rectangle((236, -18), 22, 36, facecolor='#212121', edgecolor='#fbc02d', lw=1.5, zorder=4))
ax_right.text(247, 0, "MOTOR", color='#fbc02d', ha='center', va='center', fontsize=7, fontweight='bold')

# Solution text box
good_text = "THE PROPER CAD SEQUENCE:\n" \
            "1. Assemble the ROTOR FIRST:\n" \
            "   Shaft + 2 Endplates (220mm apart) + 4 Blades.\n" \
            "2. That rotor forms a single rotating cage.\n" \
            "3. The FRAME only supports the shaft at the two OUTER ends!"
ax_right.text(0.5, 0.05, good_text, transform=ax_right.transAxes, ha='center', va='bottom',
              fontsize=8.5, family='monospace', color='#1b5e20',
              bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8f5e9', edgecolor='#4caf50', lw=1.5))

ax_right.set_xlim(-40, 270)
ax_right.set_ylim(-160, 140)
ax_right.set_xlabel("Z Position (mm)", fontsize=9, fontweight='bold')
ax_right.set_ylabel("Y Position (mm)", fontsize=9, fontweight='bold')

plt.tight_layout()
fix_path = os.path.join(output_dir, "cycloprop_collision_fix_visual.png")
plt.savefig(fix_path, bbox_inches='tight', dpi=200)
plt.close()
print(f"[SUCCESS] Saved collision fix visual: {fix_path}")
