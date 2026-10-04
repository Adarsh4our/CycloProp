"""
CycloProp — Airfoil Coordinate Generator
=========================================
Generates NACA 4-digit + 6-series airfoil .dat files for CFD import.
Compatible with: OpenFOAM blockMeshDict splines, ANSYS SpaceClaim import.

Airfoils studied:
  NACA 0009  — thinnest structural limit (t/c = 9%)
  NACA 0012  — CycloProp Rev 3.0 CHOSEN airfoil (t/c = 12%)
  NACA 0015  — original baseline (t/c = 15%)
  NACA 0018  — cyclorotor literature candidate (t/c = 18%)
  NACA 63-012 — 6-series laminar flow (t/c = 12%, different pressure dist.)

All airfoils are SYMMETRIC (zero camber) — required for cyclorotor use.
Cambered airfoils (E374, Clark Y etc.) would produce asymmetric thrust.

Operating condition: Re = 95,000 | c = 38 mm | V_inlet = 36.8 m/s

Usage:
  python gen_airfoil_coords.py
  Outputs: airfoil_coords/<name>_chord38mm.dat  (in mm)
           airfoil_coords/<name>_normalized.dat  (chord = 1.0)
"""

import numpy as np
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "airfoil_coords")
os.makedirs(OUT_DIR, exist_ok=True)


def naca_4digit_symmetric(thickness_ratio: float, n: int = 200) -> np.ndarray:
    """
    Generate symmetric NACA 00tt airfoil coordinates using cosine spacing.

    Args:
        thickness_ratio: max thickness as fraction of chord (e.g. 0.12 for NACA 0012)
        n: number of points per surface (total = 2n)

    Returns:
        Array of (x, y) coordinates: upper surface LE→TE then lower TE→LE
        x in [0, 1] (normalised chord)
    """
    t = thickness_ratio
    beta = np.linspace(0, np.pi, n)
    x = 0.5 * (1 - np.cos(beta))  # cosine spacing — dense near LE

    # NACA 4-digit thickness distribution (open trailing edge)
    yt = (t / 0.2) * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4  # open TE: yt(1) ≈ 0.0013 * t/0.2
    )

    upper = list(zip(x,        yt))
    lower = list(zip(x[::-1], -yt[::-1]))
    return np.array(upper + lower)


def naca_63_012(n: int = 200) -> np.ndarray:
    """
    Generate NACA 63-012 airfoil (6-series, symmetric, t/c=12%).
    Uses modified trailing-edge coefficient for closed TE (TN-824 data).

    Key difference from NACA 0012:
      - Pressure recovery is more gradual (designed for laminar flow)
      - Minimum Cd can be lower at Re~100K if laminar bucket is maintained
      - More sensitive to surface roughness
    """
    t = 0.12
    beta = np.linspace(0, np.pi, n)
    x = 0.5 * (1 - np.cos(beta))

    # 63-series uses slightly different aft coefficients (closed TE)
    yt = (t / 0.2) * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1036 * x**4  # closed TE: -0.1036 vs -0.1015
    )
    # 6-series has a slightly more forward maximum thickness location
    # Approximate with a small sinusoidal correction
    correction = 0.006 * np.sin(np.pi * x)
    yt = yt + correction

    upper = list(zip(x,        yt))
    lower = list(zip(x[::-1], -yt[::-1]))
    return np.array(upper + lower)


# ── Velocity table at Re=95,000, c=38mm, V=36.8 m/s ──────────────────────────
ALPHAS_DEG = np.arange(-35, 36, 5)   # -35° to +35° in 5° steps
V_INLET    = 36.8                     # m/s

def velocity_components(alpha_deg: float, V: float = V_INLET):
    """Return (Vx, Vy) for given angle of attack in degrees."""
    a = np.radians(alpha_deg)
    return V * np.cos(a), V * np.sin(a)


# ── Main: generate all airfoil files ──────────────────────────────────────────
AIRFOILS = {
    "naca0009":  (naca_4digit_symmetric(0.09), "NACA 0009 | t/c=9%  | Thinnest structural limit"),
    "naca0012":  (naca_4digit_symmetric(0.12), "NACA 0012 | t/c=12% | CycloProp Rev 3.0 CHOSEN [SELECTED]"),
    "naca0015":  (naca_4digit_symmetric(0.15), "NACA 0015 | t/c=15% | Original baseline"),
    "naca0018":  (naca_4digit_symmetric(0.18), "NACA 0018 | t/c=18% | Cyclorotor literature candidate"),
    "naca63012": (naca_63_012(),               "NACA 63-012 | t/c=12% | 6-series laminar (high reward)"),
}

CHORD_MM = 38.0   # actual blade chord

print("=" * 65)
print("CycloProp Airfoil Coordinate Generator")
print(f"Chord = {CHORD_MM} mm | Re = 95,000 | V_inlet = {V_INLET} m/s")
print("=" * 65)

for name, (coords, desc) in AIRFOILS.items():
    # Normalised (chord = 1.0)
    path_norm = os.path.join(OUT_DIR, f"{name}_normalized.dat")
    header = (f"# {desc}\n"
              f"# Normalised chord (x in [0,1])\n"
              f"# x_norm   y_norm")
    np.savetxt(path_norm, coords, fmt="%.8f", delimiter="\t", header=header, comments="")

    # Scaled to actual chord in mm
    coords_mm = coords * CHORD_MM
    path_mm = os.path.join(OUT_DIR, f"{name}_chord38mm.dat")
    header_mm = (f"# {desc}\n"
                 f"# Chord = {CHORD_MM} mm (actual blade chord)\n"
                 f"# x_mm     y_mm")
    np.savetxt(path_mm, coords_mm, fmt="%.5f", delimiter="\t", header=header_mm, comments="")

    t_max     = coords[:, 1].max()
    x_at_tmax = coords[np.argmax(coords[:, 1]), 0]
    print(f"\n  {name.upper():<12} | {desc}")
    print(f"               Max t/c = {t_max:.4f}  at x/c = {x_at_tmax:.3f}")
    print(f"               Max thickness = {t_max * CHORD_MM:.2f} mm at chord = {CHORD_MM} mm")
    print(f"               Saved: {os.path.basename(path_mm)}")

print("\n" + "=" * 65)
print("Velocity components at each angle (V = 36.8 m/s, Re = 95,000):")
print(f"  {'Alpha (deg)':>12} | {'Vx (m/s)':>10} | {'Vy (m/s)':>10}")
print("  " + "-" * 38)
for a in ALPHAS_DEG:
    vx, vy = velocity_components(a)
    print(f"  {a:>12.0f} | {vx:>10.4f} | {vy:>10.4f}")
print("=" * 65)
print("\nAll coordinate files saved to: cfd_study/airfoil_coords/")
