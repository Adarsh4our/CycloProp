"""
Generate NACA 0012 Outer Mold Line (OML) and Inner Cavity (IML) curves for SolidWorks
Chord c = 38.00 mm, thickness ratio t = 0.12.
Skin thickness t_wall = 0.25 mm (for CFRP prepreg skin + XPS core / through-spar clearance).
Generates both LE-origin and 25%-chord (spar)-origin curve files.
"""

import numpy as np
import os

CHORD = 38.00  # mm
T_RATIO = 0.12 # 12%
WALL_THICKNESS = 0.25 # mm
SPAR_LOC = 0.25 * CHORD # 9.50 mm from LE
NUM_PTS = 100

output_dir = r"c:\Users\Adarsh Singh\CycloProp\scripts"
os.makedirs(output_dir, exist_ok=True)

# ── NACA 0012 Half-Thickness Equation ──
def naca0012_yt(xc):
    # xc = x / c in [0, 1]
    # Standard formula with closed trailing edge (-0.1036)
    return 5.0 * T_RATIO * (
        0.2969 * np.sqrt(xc)
        - 0.1260 * xc
        - 0.3516 * (xc ** 2)
        + 0.2843 * (xc ** 3)
        - 0.1036 * (xc ** 4)
    )

def naca0012_dyt_dxc(xc):
    # Derivative d(yt)/d(xc)
    # At xc = 0, derivative is infinite (vertical slope at LE)
    xc_safe = np.maximum(xc, 1e-7)
    return 5.0 * T_RATIO * (
        0.2969 / (2.0 * np.sqrt(xc_safe))
        - 0.1260
        - 2.0 * 0.3516 * xc_safe
        + 3.0 * 0.2843 * (xc_safe ** 2)
        - 4.0 * 0.1036 * (xc_safe ** 3)
    )

# High-resolution grid for accurate normal offset
beta = np.linspace(0, np.pi, 1000)
xc_dense = 0.5 * (1.0 - np.cos(beta))
x_dense = xc_dense * CHORD
yt_dense = naca0012_yt(xc_dense) * CHORD

# Derivative dy/dx = d(yt)/d(xc) * (dxc/dx) = d(yt)/d(xc)
dydx = naca0012_dyt_dxc(xc_dense)

# Normal vector components for upper surface (outward normal is (-dy/dx, 1) / sqrt(1 + (dy/dx)^2))
# Inward normal for upper surface (pointing down and back): (dy/dx, -1) / sqrt(1 + (dy/dx)^2)
norm_mag = np.sqrt(1.0 + dydx**2)
nx_inward = dydx / norm_mag
ny_inward = -1.0 / norm_mag

# Offset surfaces
# Upper inner
upper_ix_dense = x_dense + WALL_THICKNESS * nx_inward
upper_iy_dense = yt_dense + WALL_THICKNESS * ny_inward

# Lower inner (by symmetry, y is mirrored)
lower_ix_dense = upper_ix_dense
lower_iy_dense = -upper_iy_dense

# Valid cavity range: where gap between upper and lower is positive (e.g. >= 0.2 mm)
cavity_gap = upper_iy_dense - lower_iy_dense
valid_indices = np.where(cavity_gap >= 0.20)[0]
i_start, i_end = valid_indices[0], valid_indices[-1]

# Subsample points for export
idx_oml = np.linspace(0, len(x_dense) - 1, NUM_PTS, dtype=int)
idx_iml = np.linspace(i_start, i_end, NUM_PTS, dtype=int)

# 1. Outer Mold Line (LE to TE)
oml_upper_x = x_dense[idx_oml]
oml_upper_y = yt_dense[idx_oml]
oml_lower_x = x_dense[idx_oml]
oml_lower_y = -yt_dense[idx_oml]

# 2. Inner Mold Line (LE to TE within valid cavity)
iml_upper_x = upper_ix_dense[idx_iml]
iml_upper_y = upper_iy_dense[idx_iml]
iml_lower_x = lower_ix_dense[idx_iml]
iml_lower_y = lower_iy_dense[idx_iml]

# Save LE-origin files (X = 0 at leading edge)
def save_curve(filepath, xs, ys):
    with open(filepath, 'w') as f:
        for x, y in zip(xs, ys):
            f.write(f"{x:.6f}\t{y:.6f}\t0.000000\n")

save_curve(os.path.join(output_dir, "naca0012_outer_upper_LE.txt"), oml_upper_x, oml_upper_y)
save_curve(os.path.join(output_dir, "naca0012_outer_lower_LE.txt"), oml_lower_x, oml_lower_y)
save_curve(os.path.join(output_dir, "naca0012_inner_upper_LE.txt"), iml_upper_x, iml_upper_y)
save_curve(os.path.join(output_dir, "naca0012_inner_lower_LE.txt"), iml_lower_x, iml_lower_y)

# Save Quarter-Chord origin files (X = 0 at 25% chord = 9.5 mm spar axis)
# Shift: X_new = X - 9.50
save_curve(os.path.join(output_dir, "naca0012_outer_upper_spar.txt"), oml_upper_x - SPAR_LOC, oml_upper_y)
save_curve(os.path.join(output_dir, "naca0012_outer_lower_spar.txt"), oml_lower_x - SPAR_LOC, oml_lower_y)
save_curve(os.path.join(output_dir, "naca0012_inner_upper_spar.txt"), iml_upper_x - SPAR_LOC, iml_upper_y)
save_curve(os.path.join(output_dir, "naca0012_inner_lower_spar.txt"), iml_lower_x - SPAR_LOC, iml_lower_y)

print("Successfully generated all NACA 0012 outer and inner curve files!")
print(f"Chord c = {CHORD} mm, Max outer thickness = {2*yt_dense.max():.2f} mm")
print(f"Outer thickness at spar (x = 9.50 mm): {2*naca0012_yt(0.25)*CHORD:.3f} mm")
print(f"Inner cavity thickness at spar: {2*upper_iy_dense[np.argmin(np.abs(x_dense - 9.50))]:.3f} mm")
print(f"Through-spar tube clearance: {2*upper_iy_dense[np.argmin(np.abs(x_dense - 9.50))] - 4.00:.3f} mm")
print(f"Cavity extent along chord: {iml_upper_x[0]:.2f} mm to {iml_upper_x[-1]:.2f} mm ({iml_upper_x[-1]-iml_upper_x[0]:.2f} mm length)")
