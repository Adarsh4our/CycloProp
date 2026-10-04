"""
CycloProp — CFD Polar Integration Tool
=======================================
Loads Cl/Cd polar CSV files from CFD (OpenFOAM or ANSYS Fluent)
and plugs them into the CycloProp BEMT solver as lookup tables,
replacing the analytical estimates in cyclorotor_sizing.py.

Usage:
  python integrate_cfd_polars.py

Input files expected in:  cfd_study/results/
  naca0012_openfoam_Re95k.csv
  naca0012_fluent_Re95k.csv
  naca0015_openfoam_Re95k.csv   (etc.)

Expected CSV columns:
  alpha_deg, Cl, Cd, Cm

Output:
  Prints cross-validation comparison table
  Saves averaged polars: results/naca0012_averaged_Re95k.csv
  Runs BEMT with CFD polars and compares against analytical model
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add parent directory to path so we can import cyclorotor_sizing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cyclorotor_sizing import CyclorotorGeometry, CyclorotorAeroModel

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "figures")
os.makedirs(RESULTS_DIR, exist_ok=True)


# ── CFD Polar Loader ───────────────────────────────────────────────────────────

def load_polar(csv_path: str) -> dict:
    """
    Load a Cl/Cd polar CSV file from CFD output.
    Returns dict with 'alpha', 'Cl', 'Cd', 'Cm' arrays (alpha in radians).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Polar file not found: {csv_path}\n"
                                 "Run CFD first and place results in cfd_study/results/")
    df = pd.read_csv(csv_path, comment="#")
    df.columns = [c.strip() for c in df.columns]
    return {
        "alpha_deg": df["alpha_deg"].values.astype(float),
        "alpha":     np.radians(df["alpha_deg"].values.astype(float)),
        "Cl":        df["Cl"].values.astype(float),
        "Cd":        df["Cd"].values.astype(float),
        "Cm":        df["Cm"].values.astype(float) if "Cm" in df else np.zeros(len(df)),
        "source":    os.path.basename(csv_path),
    }


def average_polars(polar_a: dict, polar_b: dict) -> dict:
    """
    Average two polar datasets (same alpha points assumed).
    Used to combine OpenFOAM + Fluent results for high-confidence polars.
    """
    assert np.allclose(polar_a["alpha_deg"], polar_b["alpha_deg"], atol=0.5), \
        "Alpha arrays don't match — interpolate first"
    return {
        "alpha_deg": polar_a["alpha_deg"],
        "alpha":     polar_a["alpha"],
        "Cl":        0.5 * (polar_a["Cl"] + polar_b["Cl"]),
        "Cd":        0.5 * (polar_a["Cd"] + polar_b["Cd"]),
        "Cm":        0.5 * (polar_a["Cm"] + polar_b["Cm"]),
        "source":    "averaged (OpenFOAM + Fluent)",
    }


def cross_validate(polar_a: dict, polar_b: dict, name: str = ""):
    """
    Print cross-validation table comparing two polar datasets.
    Flags angles where disagreement exceeds 5% (Cl) or 10% (Cd).
    """
    print(f"\n{'='*75}")
    print(f"  CROSS-VALIDATION: {name}")
    print(f"  A: {polar_a['source']}")
    print(f"  B: {polar_b['source']}")
    print(f"{'='*75}")
    print(f"  {'Alpha':>6} | {'Cl_A':>8} | {'Cl_B':>8} | {'Cl_diff%':>9} | "
          f"{'Cd_A':>8} | {'Cd_B':>8} | {'Cd_diff%':>9} | Status")
    print(f"  {'-'*73}")

    all_ok = True
    for i, a in enumerate(polar_a["alpha_deg"]):
        # Find matching alpha in B
        idx_b = np.argmin(np.abs(polar_b["alpha_deg"] - a))
        cl_a, cl_b = polar_a["Cl"][i],  polar_b["Cl"][idx_b]
        cd_a, cd_b = polar_a["Cd"][i],  polar_b["Cd"][idx_b]

        cl_diff = abs(cl_a - cl_b) / (abs(cl_a) + 1e-6) * 100
        cd_diff = abs(cd_a - cd_b) / (abs(cd_a) + 1e-6) * 100

        ok_cl = cl_diff < 5.0
        ok_cd = cd_diff < 10.0
        status = "✅ OK" if (ok_cl and ok_cd) else "⚠️  CHECK"
        if not (ok_cl and ok_cd):
            all_ok = False

        print(f"  {a:>6.1f} | {cl_a:>8.4f} | {cl_b:>8.4f} | {cl_diff:>8.1f}% | "
              f"{cd_a:>8.5f} | {cd_b:>8.5f} | {cd_diff:>8.1f}% | {status}")

    print(f"{'='*75}")
    if all_ok:
        print("  ✅ All values agree within tolerance. Results are VALIDATED.")
    else:
        print("  ⚠️  Some values exceed tolerance. Check mesh y+, BC settings.")


# ── CFD Polar in BEMT solver ───────────────────────────────────────────────────

class CFDPolarAeroModel(CyclorotorAeroModel):
    """
    Extended BEMT model that uses interpolated CFD polars
    instead of the analytical Leishman-Beddoes model.
    """
    def __init__(self, polars: dict, **kwargs):
        super().__init__(**kwargs)
        self.cfd_polars = polars  # dict: {airfoil_name: polar_dict}

    def get_airfoil_polars(self, alpha_eff, Re, k_reduced, dalpha_dt,
                            aspect_ratio, airfoil="NACA 0012"):
        """
        Override: look up Cl, Cd from CFD table via interpolation.
        Falls back to analytical model if CFD polar not available.
        """
        key = airfoil.lower().replace(" ", "").replace("-", "")
        if key in self.cfd_polars:
            polar = self.cfd_polars[key]
            Cl = np.interp(alpha_eff, polar["alpha"], polar["Cl"],
                           left=polar["Cl"][0], right=polar["Cl"][-1])
            Cd = np.interp(np.abs(alpha_eff), np.abs(polar["alpha"]), polar["Cd"],
                           left=polar["Cd"][0], right=polar["Cd"][-1])
            # Cd is symmetric (same for ±α for symmetric airfoils)
            Cm = np.interp(alpha_eff, polar["alpha"], polar["Cm"],
                           left=polar["Cm"][0], right=polar["Cm"][-1])
            # Apply 3D induced drag correction
            Cd_induced = (Cl**2) / (np.pi * aspect_ratio * self.e_oswald)
            return Cl, Cd + Cd_induced, Cm
        else:
            print(f"  [INFO] CFD polar not found for '{airfoil}' — using analytical model")
            return super().get_airfoil_polars(alpha_eff, Re, k_reduced,
                                               dalpha_dt, aspect_ratio, airfoil)


# ── Main comparison ────────────────────────────────────────────────────────────

def run_comparison():
    """
    Load available CFD polars, cross-validate, then compare BEMT thrust
    predictions: analytical model vs CFD-informed model.
    """
    print("\n" + "=" * 75)
    print("  CycloProp CFD Polar Integration & BEMT Comparison")
    print("=" * 75)

    # Try to load available polars
    available_polars = {}
    for airfoil in ["naca0009", "naca0012", "naca0015", "naca0018", "naca63012"]:
        for source in ["openfoam", "fluent", "averaged"]:
            path = os.path.join(RESULTS_DIR, f"{airfoil}_{source}_Re95k.csv")
            if os.path.exists(path):
                try:
                    available_polars[airfoil] = load_polar(path)
                    print(f"  ✅ Loaded: {os.path.basename(path)}")
                except Exception as e:
                    print(f"  ⚠️  Failed to load {path}: {e}")

    if not available_polars:
        print("\n  No CFD polar files found in cfd_study/results/")
        print("  Run OpenFOAM (Linux) or ANSYS Fluent (IIT lab) first.")
        print("  Expected file format: naca0012_openfoam_Re95k.csv")
        print("\n  CSV columns: alpha_deg, Cl, Cd, Cm")
        print("\n  Example row:   5.0, 0.547, 0.0182, -0.021")
        return

    # Cross-validate if both OpenFOAM and Fluent results exist
    for airfoil in available_polars:
        of_path  = os.path.join(RESULTS_DIR, f"{airfoil}_openfoam_Re95k.csv")
        flu_path = os.path.join(RESULTS_DIR, f"{airfoil}_fluent_Re95k.csv")
        if os.path.exists(of_path) and os.path.exists(flu_path):
            cross_validate(load_polar(of_path), load_polar(flu_path),
                           name=f"{airfoil.upper()} — OpenFOAM vs Fluent")

    # BEMT comparison: analytical vs CFD for NACA 0012
    if "naca0012" in available_polars:
        print("\n" + "=" * 75)
        print("  BEMT THRUST COMPARISON: Analytical Model vs CFD Polars (NACA 0012)")
        print("=" * 75)

        geom = CyclorotorGeometry(
            radius=0.095, span=0.220, chord=0.038,
            num_blades=4, airfoil="NACA 0012", total_module_mass=0.3014
        )

        aero_analytical = CyclorotorAeroModel()
        aero_cfd        = CFDPolarAeroModel(polars={"naca0012": available_polars["naca0012"]})

        print(f"\n  {'RPM':>6} | {'Thrust_Analytical (N)':>22} | "
              f"{'Thrust_CFD (N)':>15} | {'Diff%':>6}")
        print(f"  {'-'*60}")
        for rpm in [2000, 2200, 2400, 2640, 2800, 3000]:
            r_an  = aero_analytical.solve_hover_state(geom, rpm, 35.0)
            r_cfd = aero_cfd.solve_hover_state(geom, rpm, 35.0)
            diff  = (r_cfd["thrust_N"] - r_an["thrust_N"]) / r_an["thrust_N"] * 100
            print(f"  {rpm:>6} | {r_an['thrust_N']:>22.3f} | "
                  f"{r_cfd['thrust_N']:>15.3f} | {diff:>+6.1f}%")


if __name__ == "__main__":
    run_comparison()
