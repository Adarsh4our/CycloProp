import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Coordinates of outer NACA 0015
chord = 38.0
t = 0.15
beta = np.linspace(0, np.pi, 200)
xc = 0.5 * (1.0 - np.cos(beta))
x = xc * chord
yt = 5.0 * t * chord * (0.2969 * np.sqrt(xc) - 0.1260 * xc - 0.3516 * xc**2 + 0.2843 * xc**3 - 0.1015 * xc**4)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={'width_ratios': [1.2, 1]})

# --- Subplot 1: 2D Face View (Exact SolidWorks Sketch) ---
# Outer airfoil
ax1.plot(x, yt, 'k-', linewidth=2.5, label='Blade Airfoil Outline')
ax1.plot(x, -yt, 'k-', linewidth=2.5)
ax1.fill(x, yt, color='#d0d7de', alpha=0.5)
ax1.fill(x, -yt, color='#d0d7de', alpha=0.5)

# Chord centerline
ax1.axhline(0, color='gray', linestyle='-.', linewidth=1.0, alpha=0.7)

# Trunnion center (9.5, 0)
x_p = 9.5
y_p = 0.0

# Pitch Horn Slot: from (9.5, 0) to (9.5, 12.0), width = 6.0 mm (radius = 3.0 mm)
r_horn = 3.0
h_horn = 12.0

# Draw Pitch Horn contour
theta_top = np.linspace(0, np.pi, 50)
top_arc_x = x_p + r_horn * np.cos(theta_top)
top_arc_y = y_p + h_horn + r_horn * np.sin(theta_top)

theta_bot = np.linspace(np.pi, 2*np.pi, 50)
bot_arc_x = x_p + r_horn * np.cos(theta_bot)
bot_arc_y = y_p + r_horn * np.sin(theta_bot)

horn_x = np.concatenate([[x_p - r_horn, x_p - r_horn], top_arc_x, [x_p + r_horn, x_p + r_horn], bot_arc_x])
horn_y = np.concatenate([[y_p, y_p + h_horn], top_arc_y, [y_p + h_horn, y_p], bot_arc_y])

ax1.fill(horn_x, horn_y, color='#ff7f0e', alpha=0.7, label='Pitch Horn Body (Extrude 2.5 mm)')
ax1.plot(horn_x, horn_y, color='#d62728', linewidth=2.0)

# Trunnion pin circle Ø3 mm
trunnion = patches.Circle((x_p, y_p), 1.5, edgecolor='#1f77b4', facecolor='#4682b4', linewidth=2, zorder=5, label='Trunnion Pin (Ø3.0 mm)')
ax1.add_patch(trunnion)

# M2 hole Ø2 mm
m2_hole = patches.Circle((x_p, y_p + h_horn), 1.0, edgecolor='black', facecolor='white', linewidth=2, zorder=5, label='M2 Ball-Stud Hole (Ø2.0 mm)')
ax1.add_patch(m2_hole)

# Dimensions & Annotations
# Pivot to M2 hole dimension
ax1.annotate('', xy=(x_p - 4.5, y_p), xytext=(x_p - 4.5, y_p + h_horn),
             arrowprops=dict(arrowstyle='<->', color='red', lw=1.8))
ax1.text(x_p - 11.5, y_p + h_horn/2 - 0.5, r'$r_h = 12.0\ \mathrm{mm}$' + '\nMoment Arm', color='red', fontsize=11, fontweight='bold')

# Origin to Pivot dimension
ax1.annotate('', xy=(0, -4.5), xytext=(x_p, -4.5),
             arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
ax1.text(x_p/2 - 3.5, -6.2, r'$X = 9.5\ \mathrm{mm}$' + '\n(0.25c)', color='blue', fontsize=10, fontweight='bold')

# Width dimension
ax1.annotate('', xy=(x_p - 3.0, y_p + h_horn + 4.5), xytext=(x_p + 3.0, y_p + h_horn + 4.5),
             arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
ax1.text(x_p - 2.5, y_p + h_horn + 5.2, 'Width 6.0 mm', color='green', fontsize=10, fontweight='bold')

# Label M2 hole
ax1.annotate('M2 Ball-Stud Hole\n(Connects to Pushrod Link)', 
             xy=(x_p, y_p + h_horn), xytext=(x_p + 7, y_p + h_horn + 2),
             arrowprops=dict(arrowstyle='->', color='black', lw=1.5), fontsize=10, fontweight='bold')

# Label Trunnion
ax1.annotate('Pivot Center\n(Trunnion Pin Ø3.0 mm)', 
             xy=(x_p, y_p), xytext=(x_p + 7, y_p - 3),
             arrowprops=dict(arrowstyle='->', color='black', lw=1.5), fontsize=10, fontweight='bold')

ax1.set_xlim(-5, 42)
ax1.set_ylim(-8, 19)
ax1.set_aspect('equal')
ax1.set_xlabel('X Coordinate along Chord (mm)', fontsize=11)
ax1.set_ylabel('Y Coordinate (mm)', fontsize=11)
ax1.set_title('SKETCH VIEW (Normal to Flat End Face)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower right', fontsize=9)

# --- Subplot 2: 3D Perspective Explanatory Diagram ---
ax2.axis('off')
explanation_text = """
WHAT IS THE PITCH HORN?
-------------------------------------------------
Think of a rudder horn or a bell-crank lever:

• PURPOSE:
  When the cyclorotor spins, the Pushrod Linkage
  pushes and pulls on this horn to tilt (pitch)
  the blade by ±35° for thrust vectoring.

• WORKING MECHANICS:
  Pushrod Force ──► M2 Hole at Y = 12 mm
                           │
                           │ Moment Arm = 12 mm
                           ▼
                    Rotates Blade about
                    Trunnion at Y = 0 mm

• SOLIDWORKS STEPS:
  1. Click the flat end face of the blade.
  2. Select 'Straight Slot' tool.
  3. First click: center of Trunnion (9.5, 0).
  4. Second click: move 12 mm UP (9.5, 12).
  5. Pull outward to make width = 6 mm.
  6. Place a Circle (Ø2.0 mm) at the top point.
  7. Boss-Extrude: 2.5 mm outward!
"""
ax2.text(0.05, 0.95, explanation_text, fontsize=11, family='monospace', verticalalignment='top',
         bbox=dict(boxstyle='round,pad=1.0', facecolor='#f8f9fa', edgecolor='#ced4da', lw=1.5))

plt.tight_layout()
fig_path = r"c:\Users\Adarsh Singh\CycloProp\figures\pitch_horn_visualization.png"
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved: {fig_path}")
