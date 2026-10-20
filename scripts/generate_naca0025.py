"""
NACA 0025 Teardrop Fairing Profile Generator for CycloProp Rev 3.0
Chord c = 32.00 mm, t/c = 0.25, max thickness = 8.00 mm.
Max thickness is at x = 0.30 * c = 9.60 mm from LE.
We place origin (0, 0) at the center of the structural standoff (x = 9.60 mm).
"""

import numpy as np

c = 32.00  # chord in mm
t = 0.25   # thickness ratio (25%)
x_standoff = 0.30 * c  # 9.60 mm from LE

beta = np.linspace(0, np.pi, 60)
x_norm = 0.5 * (1.0 - np.cos(beta))
x = x_norm * c

yt = 5.0 * t * c * (
    0.2969 * np.sqrt(x_norm)
    - 0.1260 * x_norm
    - 0.3516 * (x_norm ** 2)
    + 0.2843 * (x_norm ** 3)
    - 0.1036 * (x_norm ** 4)
)

x_shifted = x - x_standoff

upper_x = x_shifted[::-1]
upper_y = yt[::-1]
lower_x = x_shifted[1:]
lower_y = -yt[1:]

all_x = np.concatenate([upper_x, lower_x])
all_y = np.concatenate([upper_y, lower_y])

curve_file = r"c:\Users\Adarsh Singh\CycloProp\scripts\naca0025_chord32mm_solidworks.txt"
with open(curve_file, "w") as f:
    for xi, yi in zip(all_x, all_y):
        f.write(f"{xi:.6f}\t{yi:.6f}\t0.000000\n")

print(f"Total fairing points: {len(all_x)}")
print(f"X range: [{all_x.min():.2f}, {all_x.max():.2f}] mm (Total chord: {all_x.max() - all_x.min():.2f} mm)")
print(f"Y range: [{all_y.min():.2f}, {all_y.max():.2f}] mm (Max thickness: {2*yt.max():.2f} mm)")
print(f"Thickness at standoff (x=9.6mm): {2*yt[np.argmin(np.abs(x - 9.6))]:.2f} mm")
print(f"Exported fairing curve to: {curve_file}")
