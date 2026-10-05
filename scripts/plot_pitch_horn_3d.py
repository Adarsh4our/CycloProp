import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# NACA 0015 profile
chord = 38.0
t = 0.15
beta = np.linspace(0, np.pi, 60)
xc = 0.5 * (1.0 - np.cos(beta))
x = xc * chord
yt = 5.0 * t * chord * (0.2969 * np.sqrt(xc) - 0.1260 * xc - 0.3516 * xc**2 + 0.2843 * xc**3 - 0.1015 * xc**4)

# Create 3D Blade section (spanwise from Z=0 to Z=50)
z_span = np.linspace(0, 45, 10)
X_blade = np.concatenate([x, x[::-1]])
Y_blade = np.concatenate([yt, -yt[::-1]])

# Plot blade end face at Z=0
ax.plot(X_blade, Y_blade, 0, 'k-', lw=2.0)
# Plot blade body edges
ax.plot(X_blade, Y_blade, 45, color='gray', lw=1.0)
for xi, yi in zip(X_blade[::8], Y_blade[::8]):
    ax.plot([xi, xi], [yi, yi], [0, 45], color='lightgray', lw=0.8)

# Trunnion Pin (Cylinder at X=9.5, Y=0, extending into -Z from 0 to -8)
z_trunnion = np.linspace(0, -8, 10)
theta_trunnion = np.linspace(0, 2*np.pi, 30)
Theta_grid, Z_grid = np.meshgrid(theta_trunnion, z_trunnion)
X_trunnion = 9.5 + 1.5 * np.cos(Theta_grid)
Y_trunnion = 0.0 + 1.5 * np.sin(Theta_grid)
ax.plot_surface(X_trunnion, Y_trunnion, Z_grid, color='#1f77b4', alpha=0.8)

# Pitch Horn (extending into -Z by 2.5 mm, from Y=0 to Y=12)
# Slot outline
r_horn = 3.0
h_horn = 12.0
x_p = 9.5
theta_top = np.linspace(0, np.pi, 25)
top_arc_x = x_p + r_horn * np.cos(theta_top)
top_arc_y = h_horn + r_horn * np.sin(theta_top)
theta_bot = np.linspace(np.pi, 2*np.pi, 25)
bot_arc_x = x_p + r_horn * np.cos(theta_bot)
bot_arc_y = 0.0 + r_horn * np.sin(theta_bot)

horn_x = np.concatenate([[x_p - r_horn, x_p - r_horn], top_arc_x, [x_p + r_horn, x_p + r_horn], bot_arc_x])
horn_y = np.concatenate([[0.0, h_horn], top_arc_y, [h_horn, 0.0], bot_arc_y])

# Extrude horn from Z=0 to Z=-2.5
ax.plot(horn_x, horn_y, 0, color='#d62728', lw=2)
ax.plot(horn_x, horn_y, -2.5, color='#d62728', lw=2)
for hx, hy in zip(horn_x[::4], horn_y[::4]):
    ax.plot([hx, hx], [hy, hy], [0, -2.5], color='#ff7f0e', lw=1.2)

# M2 hole at X=9.5, Y=12, from Z=0 to -2.5
theta_hole = np.linspace(0, 2*np.pi, 25)
ax.plot(x_p + 1.0*np.cos(theta_hole), 12.0 + 1.0*np.sin(theta_hole), -2.5, 'k-', lw=1.5)

# Annotations
ax.text(x_p, 12.0, -5, "M2 Ball-Stud Hole\n(Connects to Pushrod)", color='black', fontsize=9, fontweight='bold')
ax.text(x_p, 0.0, -10, "Trunnion Pin\n(MR63ZZ Bearing)", color='#1f77b4', fontsize=9, fontweight='bold')
ax.text(25, 0, 20, "Blade Body (NACA 0015)", color='#555555', fontsize=10)

ax.set_box_aspect((1.2, 0.8, 1))
ax.view_init(elev=25, azim=-60)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.set_title('3D Visual: Pitch Horn + Trunnion Assembly', fontsize=13, fontweight='bold')

plt.tight_layout()
fig3d_path = r"c:\Users\Adarsh Singh\CycloProp\figures\pitch_horn_3d_render.png"
plt.savefig(fig3d_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved: {fig3d_path}")
