"""
Generate NACA 0015 inner cavity as TWO separate open curves (upper + lower).
This avoids SolidWorks' self-intersection error with closed spline loops.
User connects them with 2 short lines in the sketch.
"""

import numpy as np
import os

WALL_THICKNESS = 0.80
CHORD = 38.0
NUM_PTS = 80  # per surface — enough for smooth spline, few enough to avoid errors

OUTPUT_DIR = r"c:\Users\Adarsh Singh\CycloProp"
UPPER_FILE = os.path.join(OUTPUT_DIR, "inner_cavity_upper.txt")
LOWER_FILE = os.path.join(OUTPUT_DIR, "inner_cavity_lower.txt")

# ── NACA 0015 half-thickness ──
def naca0015_yt(xc):
    t = 0.15
    return 5.0 * t * (0.2969*np.sqrt(xc) - 0.1260*xc - 0.3516*xc**2 + 0.2843*xc**3 - 0.1015*xc**4)

# Cosine spacing
beta = np.linspace(0, np.pi, 500)
xc = 0.5 * (1.0 - np.cos(beta))
x_full = xc * CHORD
yt_full = naca0015_yt(xc) * CHORD

# ── Offset each surface inward ──
def offset_surface(x_pts, y_pts, wall_t, sign):
    """sign=+1 for upper (push Y down), sign=-1 for lower (push Y up)"""
    n = len(x_pts)
    ox, oy = np.zeros(n), np.zeros(n)
    for i in range(n):
        if i == 0:
            dx, dy = x_pts[1]-x_pts[0], y_pts[1]-y_pts[0]
        elif i == n-1:
            dx, dy = x_pts[-1]-x_pts[-2], y_pts[-1]-y_pts[-2]
        else:
            dx, dy = x_pts[i+1]-x_pts[i-1], y_pts[i+1]-y_pts[i-1]
        tlen = np.sqrt(dx**2 + dy**2)
        if tlen < 1e-15:
            ox[i], oy[i] = x_pts[i], y_pts[i]
            continue
        tx, ty = dx/tlen, dy/tlen
        # For upper (Y>0, increasing X): inward normal = (ty, -tx)
        nx, ny = sign*ty, -sign*tx
        ox[i] = x_pts[i] + wall_t*nx
        oy[i] = y_pts[i] + wall_t*ny
    return ox, oy

upper_ix, upper_iy = offset_surface(x_full, yt_full, WALL_THICKNESS, +1)
lower_ix, lower_iy = offset_surface(x_full, -yt_full, WALL_THICKNESS, -1)

# Verify inner is inside
mid = len(x_full)//2
print(f"Sanity: outer_upper={yt_full[mid]:.3f}, inner_upper={upper_iy[mid]:.3f} -> {'OK' if upper_iy[mid] < yt_full[mid] else 'FLIP NEEDED'}")

# ── Filter valid region (where gap > 0.2 mm) ──
gap = upper_iy - lower_iy
valid = gap > 0.2
vi = np.where(valid)[0]
i_start, i_end = vi[0], vi[-1]
print(f"Valid X range: {x_full[i_start]:.2f} to {x_full[i_end]:.2f} mm")

# ── Subsample to NUM_PTS evenly spaced indices within valid range ──
indices = np.linspace(i_start, i_end, NUM_PTS, dtype=int)

upper_x_out = upper_ix[indices]
upper_y_out = upper_iy[indices]
lower_x_out = lower_ix[indices]
lower_y_out = lower_iy[indices]

# ── Write upper inner curve (LE to TE, increasing X) ──
with open(UPPER_FILE, 'w') as f:
    for i in range(NUM_PTS):
        f.write(f"{upper_x_out[i]:.6f}\t{upper_y_out[i]:.6f}\t0.000000\n")

# ── Write lower inner curve (LE to TE, increasing X) ──
with open(LOWER_FILE, 'w') as f:
    for i in range(NUM_PTS):
        f.write(f"{lower_x_out[i]:.6f}\t{lower_y_out[i]:.6f}\t0.000000\n")

print(f"\nUpper inner curve: {UPPER_FILE}")
print(f"  {NUM_PTS} points, X: {upper_x_out[0]:.2f} to {upper_x_out[-1]:.2f} mm")
print(f"  Start point: ({upper_x_out[0]:.3f}, {upper_y_out[0]:.3f})")
print(f"  End point:   ({upper_x_out[-1]:.3f}, {upper_y_out[-1]:.3f})")

print(f"\nLower inner curve: {LOWER_FILE}")
print(f"  {NUM_PTS} points, X: {lower_x_out[0]:.2f} to {lower_x_out[-1]:.2f} mm")
print(f"  Start point: ({lower_x_out[0]:.3f}, {lower_y_out[0]:.3f})")
print(f"  End point:   ({lower_x_out[-1]:.3f}, {lower_y_out[-1]:.3f})")

print(f"\nIn SolidWorks:")
print(f"  1. Import upper curve: Insert > Curve > Curve Through XYZ Points > inner_cavity_upper.txt")
print(f"  2. Import lower curve: Insert > Curve > Curve Through XYZ Points > inner_cavity_lower.txt")
print(f"  3. Sketch on front face > Convert Entities both curves")
print(f"  4. Draw a short Line from upper LE end to lower LE end")
print(f"  5. Draw a short Line from upper TE end to lower TE end")
print(f"  6. Sketch should shade light blue (closed loop)")
print(f"  7. Features > Extruded Cut > Through All")

# ── Verification plot ──
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

ax = axes[0]
ax.plot(x_full, yt_full, 'b-', lw=2, label='Outer NACA 0015')
ax.plot(x_full, -yt_full, 'b-', lw=2)
ax.plot(upper_x_out, upper_y_out, 'r-', lw=1.5, label='Inner Upper')
ax.plot(lower_x_out, lower_y_out, 'r-', lw=1.5, label='Inner Lower')
# Show the two lines user will draw
ax.plot([upper_x_out[0], lower_x_out[0]], [upper_y_out[0], lower_y_out[0]], 'g--', lw=1.5, label='Lines you draw')
ax.plot([upper_x_out[-1], lower_x_out[-1]], [upper_y_out[-1], lower_y_out[-1]], 'g--', lw=1.5)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_title('Full View: 2 Imported Curves + 2 Lines You Draw')
ax.legend(loc='upper right', fontsize=9)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(x_full, yt_full, 'b-', lw=2, label='Outer')
ax2.plot(x_full, -yt_full, 'b-', lw=2)
ax2.plot(upper_x_out, upper_y_out, 'r-', lw=1.5, label='Inner Upper')
ax2.plot(lower_x_out, lower_y_out, 'r-', lw=1.5, label='Inner Lower')
ax2.plot([upper_x_out[0], lower_x_out[0]], [upper_y_out[0], lower_y_out[0]], 'g--', lw=2, label='Line to draw')
ax2.set_xlim(-1, 8)
ax2.set_ylim(-3, 3)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_title('Zoomed LE: Connect endpoints with a Line')
ax2.legend(fontsize=9)
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'figures', 'blade_cavity_two_curves.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"\nFigure: {fig_path}")
