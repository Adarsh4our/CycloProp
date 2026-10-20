"""
NACA 0012 Airfoil Profile Generator for CycloProp Rev 3.0
Chord c = 38.00 mm, Spar at 25% chord (9.50 mm from LE) placed at local origin (0, 0).
"""

import numpy as np

c = 38.00  # chord in mm
t = 0.12   # thickness ratio (12%)
x_spar = 0.25 * c  # 9.50 mm from leading edge

# Use cosine spacing for smooth leading-edge clustering
beta = np.linspace(0, np.pi, 80)
x_norm = 0.5 * (1.0 - np.cos(beta))  # 0 to 1
x = x_norm * c

# NACA 0012 standard thickness distribution (with closed trailing edge)
# yt = 5 * t * c * [0.2969*sqrt(x/c) - 0.1260*(x/c) - 0.3516*(x/c)^2 + 0.2843*(x/c)^3 - 0.1036*(x/c)^4]
yt = 5.0 * t * c * (
    0.2969 * np.sqrt(x_norm)
    - 0.1260 * x_norm
    - 0.3516 * (x_norm ** 2)
    + 0.2843 * (x_norm ** 3)
    - 0.1036 * (x_norm ** 4)
)

# Shift X so origin (0, 0) is at the 25% spar center
x_shifted = x - x_spar

# Upper surface from TE to LE
upper_x = x_shifted[::-1]
upper_y = yt[::-1]

# Lower surface from LE to TE (skip LE point to avoid duplicate)
lower_x = x_shifted[1:]
lower_y = -yt[1:]

all_x = np.concatenate([upper_x, lower_x])
all_y = np.concatenate([upper_y, lower_y])

print(f"Total airfoil points: {len(all_x)}")
print(f"X range: [{all_x.min():.2f}, {all_x.max():.2f}] mm (Total chord: {all_x.max() - all_x.min():.2f} mm)")
print(f"Y range: [{all_y.min():.2f}, {all_y.max():.2f}] mm (Max thickness: {2*yt.max():.2f} mm)")
print(f"Thickness at origin (spar, x_chord=9.5mm): {2*yt[np.argmin(np.abs(x - 9.5))]:.2f} mm")

# Write out XYZ curve file in mm (Z = 0)
curve_file = r"c:\Users\Adarsh Singh\CycloProp\scripts\naca0012_chord38mm_solidworks.txt"
with open(curve_file, "w") as f:
    for xi, yi in zip(all_x, all_y):
        f.write(f"{xi:.6f}\t{yi:.6f}\t0.000000\n")

print(f"Exported airfoil curve to: {curve_file}")
