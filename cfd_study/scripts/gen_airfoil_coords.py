"""
CycloProp — Airfoil Coordinate Generator (FIXED v2)
=====================================================
Generates .dat files for CFD import (OpenFOAM / ANSYS Fluent).

NACA 0009, 0012, 0015, 0018: Standard NACA 4-digit formula (NACA Report 460)
NACA 63-012A: REAL tabulated data from UIUC Airfoil Database (NACA Report 824)

All airfoils are SYMMETRIC (zero camber) — required for cyclorotor use.

Operating condition: Re = 95,000 | c = 38 mm | V_inlet = 36.8 m/s
"""

import numpy as np
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "airfoil_coords")
os.makedirs(OUT_DIR, exist_ok=True)


def naca_4digit_symmetric(thickness_ratio: float, n: int = 200) -> np.ndarray:
    """
    Standard NACA 4-digit symmetric airfoil (NACA Report 460).
    This is the CORRECT, universally accepted formula.
    
    Args:
        thickness_ratio: max thickness fraction (0.12 for NACA 0012)
        n: points per surface (total = 2n)
    Returns:
        (x, y) coordinates, upper LE→TE then lower TE→LE, chord = 1.0
    """
    t = thickness_ratio
    beta = np.linspace(0, np.pi, n)
    x = 0.5 * (1 - np.cos(beta))  # cosine spacing — dense near LE

    yt = (t / 0.2) * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4   # open trailing edge (standard)
    )

    upper = list(zip(x, yt))
    lower = list(zip(x[::-1], -yt[::-1]))
    return np.array(upper + lower)


def naca_63012a_from_uiuc() -> np.ndarray:
    """
    REAL NACA 63-012A coordinates from the UIUC Airfoil Data Site.
    Source: https://m-selig.ae.illinois.edu/ads/coord/n63012a.dat
    Originally tabulated in NACA Report 824 (Abbott & von Doenhoff, 1945).
    
    These are NOT generated from any formula — they are the actual
    published wind-tunnel-validated coordinates.
    
    26 points per surface, interpolated to 200 via cubic spline for CFD.
    """
    # EXACT tabulated upper surface from UIUC (26 points)
    x_tab = np.array([
        0.000000, 0.005000, 0.007500, 0.012500, 0.025000, 0.050000,
        0.075000, 0.100000, 0.150000, 0.200000, 0.250000, 0.300000,
        0.350000, 0.400000, 0.450000, 0.500000, 0.550000, 0.600000,
        0.650000, 0.700000, 0.750000, 0.800000, 0.850000, 0.900000,
        0.950000, 1.000000
    ])
    y_tab = np.array([
        0.000000, 0.009730, 0.011730, 0.014920, 0.020780, 0.028950,
        0.035040, 0.039940, 0.047470, 0.052870, 0.056640, 0.059010,
        0.059950, 0.059570, 0.057920, 0.055170, 0.051480, 0.047000,
        0.041860, 0.036210, 0.030260, 0.024260, 0.018260, 0.012250,
        0.006250, 0.000250
    ])
    
    # Interpolate to 200 points using cubic spline for smooth CFD mesh
    from scipy.interpolate import CubicSpline
    
    # Use cosine-spaced x for better LE resolution
    beta = np.linspace(0, np.pi, 200)
    x_fine = 0.5 * (1 - np.cos(beta))
    
    # Cubic spline interpolation of upper surface
    cs = CubicSpline(x_tab, y_tab, bc_type='natural')
    y_fine = cs(x_fine)
    
    # Ensure LE is at (0, 0)
    y_fine[0] = 0.0
    
    upper = list(zip(x_fine, y_fine))
    lower = list(zip(x_fine[::-1], -y_fine[::-1]))   # symmetric
    return np.array(upper + lower)


def naca_63012a_no_scipy() -> np.ndarray:
    """
    Fallback: NACA 63-012A using numpy linear interpolation (no scipy needed).
    Less smooth than cubic spline but still uses the REAL tabulated data.
    """
    x_tab = np.array([
        0.000000, 0.005000, 0.007500, 0.012500, 0.025000, 0.050000,
        0.075000, 0.100000, 0.150000, 0.200000, 0.250000, 0.300000,
        0.350000, 0.400000, 0.450000, 0.500000, 0.550000, 0.600000,
        0.650000, 0.700000, 0.750000, 0.800000, 0.850000, 0.900000,
        0.950000, 1.000000
    ])
    y_tab = np.array([
        0.000000, 0.009730, 0.011730, 0.014920, 0.020780, 0.028950,
        0.035040, 0.039940, 0.047470, 0.052870, 0.056640, 0.059010,
        0.059950, 0.059570, 0.057920, 0.055170, 0.051480, 0.047000,
        0.041860, 0.036210, 0.030260, 0.024260, 0.018260, 0.012250,
        0.006250, 0.000250
    ])
    
    beta = np.linspace(0, np.pi, 200)
    x_fine = 0.5 * (1 - np.cos(beta))
    y_fine = np.interp(x_fine, x_tab, y_tab)
    y_fine[0] = 0.0
    
    upper = list(zip(x_fine, y_fine))
    lower = list(zip(x_fine[::-1], -y_fine[::-1]))
    return np.array(upper + lower)


# ── Velocity table ────────────────────────────────────────────────────────────
ALPHAS_DEG = np.arange(-35, 36, 5)
V_INLET    = 36.8

def velocity_components(alpha_deg, V=V_INLET):
    a = np.radians(alpha_deg)
    return V * np.cos(a), V * np.sin(a)


# ── Build 63-012A with best available method ──────────────────────────────────
try:
    from scipy.interpolate import CubicSpline  # noqa: F811
    naca63012a_coords = naca_63012a_from_uiuc()
    interp_method = "cubic spline (scipy)"
except ImportError:
    naca63012a_coords = naca_63012a_no_scipy()
    interp_method = "linear interpolation (numpy)"


# ── Main ──────────────────────────────────────────────────────────────────────
AIRFOILS = {
    "naca0009":  (naca_4digit_symmetric(0.09),  "NACA 0009 | t/c=9%  | Thinnest structural limit",           "NACA 4-digit formula (Report 460)"),
    "naca0012":  (naca_4digit_symmetric(0.12),  "NACA 0012 | t/c=12% | CycloProp Rev 3.0 CHOSEN [SELECTED]", "NACA 4-digit formula (Report 460)"),
    "naca0015":  (naca_4digit_symmetric(0.15),  "NACA 0015 | t/c=15% | Original baseline",                   "NACA 4-digit formula (Report 460)"),
    "naca0018":  (naca_4digit_symmetric(0.18),  "NACA 0018 | t/c=18% | Cyclorotor literature candidate",     "NACA 4-digit formula (Report 460)"),
    "naca63012": (naca63012a_coords,            "NACA 63-012A | t/c=12% | 6-series laminar",                 f"UIUC tabulated data ({interp_method})"),
}

CHORD_MM = 38.0

print("=" * 75)
print("CycloProp Airfoil Coordinate Generator (v2 FIXED)")
print(f"Chord = {CHORD_MM} mm | Re = 95,000 | V_inlet = {V_INLET} m/s")
print("=" * 75)

for name, (coords, desc, source) in AIRFOILS.items():
    # Normalised (chord = 1.0)
    path_norm = os.path.join(OUT_DIR, f"{name}_normalized.dat")
    header = (f"# {desc}\n"
              f"# Source: {source}\n"
              f"# Normalised chord (x in [0,1])\n"
              f"# x_norm   y_norm")
    np.savetxt(path_norm, coords, fmt="%.8f", delimiter="\t", header=header, comments="")

    # Scaled to actual chord in mm
    coords_mm = coords * CHORD_MM
    path_mm = os.path.join(OUT_DIR, f"{name}_chord38mm.dat")
    header_mm = (f"# {desc}\n"
                 f"# Source: {source}\n"
                 f"# Chord = {CHORD_MM} mm (actual blade chord)\n"
                 f"# x_mm     y_mm")
    np.savetxt(path_mm, coords_mm, fmt="%.5f", delimiter="\t", header=header_mm, comments="")

    t_max = coords[:, 1].max()
    x_at_tmax = coords[np.argmax(coords[:, 1]), 0]
    print(f"\n  {name.upper()}")
    print(f"    Description : {desc}")
    print(f"    Data source : {source}")
    print(f"    Max t/c     : {t_max:.6f} at x/c = {x_at_tmax:.4f}")
    print(f"    Max thickness: {t_max * CHORD_MM:.2f} mm")
    print(f"    Saved: {os.path.basename(path_mm)}")

print("\n" + "=" * 75)
print("Velocity components at each angle (V = 36.8 m/s, Re = 95,000):")
print(f"  {'Alpha (deg)':>12} | {'Vx (m/s)':>10} | {'Vy (m/s)':>10}")
print("  " + "-" * 38)
for a in ALPHAS_DEG:
    vx, vy = velocity_components(a)
    print(f"  {a:>12.0f} | {vx:>10.4f} | {vy:>10.4f}")
print("=" * 75)
print("\nAll coordinate files saved to: cfd_study/airfoil_coords/")
