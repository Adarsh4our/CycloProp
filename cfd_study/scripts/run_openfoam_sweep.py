"""
CycloProp — OpenFOAM Polar Sweep Automation
=============================================
Runs simpleFoam for all 5 airfoils × all AoA angles.
Run this script ON LINUX after installing OpenFOAM.

Usage:
  python3 run_openfoam_sweep.py

Requirements:
  - OpenFOAM v2412 installed and sourced in ~/.bashrc
  - Base template case at ~/CycloProp_CFD/base_template/
  - Run gen_airfoil_coords.py first to generate airfoil .dat files
"""

import os
import subprocess
import numpy as np
import csv
import shutil
import math

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_TEMPLATE = os.path.expanduser("~/CycloProp_CFD/base_template")
WORK_DIR      = os.path.expanduser("~/CycloProp_CFD/runs")
RESULTS_DIR   = os.path.expanduser("~/CycloProp_CFD/results")
COORDS_DIR    = os.path.expanduser("~/CycloProp/cfd_study/airfoil_coords")

V_INLET = 36.8   # m/s — Re=95000, c=38mm, rho=1.225, mu=1.81e-5
ALPHAS  = list(range(-35, 36, 5))   # -35° to +35° in 5° steps

AIRFOILS = [
    "naca0009",
    "naca0012",
    "naca0015",
    "naca0018",
    "naca63012",
]

os.makedirs(WORK_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# ── Helper: run a shell command and stream output ──────────────────────────────
def run(cmd: str, cwd: str, logfile: str = None):
    """Run shell command, write stdout+stderr to logfile, return exit code."""
    with open(logfile or "/dev/null", "w") as log:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            stdout=log, stderr=subprocess.STDOUT, text=True
        )
    return result.returncode


# ── Helper: extract last Cl, Cd from forceCoeffs.dat ──────────────────────────
def extract_coeffs(case_dir: str, alpha_deg: float):
    """
    Parse OpenFOAM forceCoeffs.dat and convert to true aerodynamic axes.
    OpenFOAM reports forces in global (x, y) — we rotate to wind axes.
    """
    coeff_file = os.path.join(
        case_dir, "postProcessing", "forceCoeffs", "0", "forceCoeffs.dat"
    )
    if not os.path.exists(coeff_file):
        return None, None, None

    # Read last non-comment line
    last_line = None
    with open(coeff_file) as f:
        for line in f:
            if not line.strip().startswith("#") and line.strip():
                last_line = line
    if last_line is None:
        return None, None, None

    cols = last_line.split()
    # Typical OpenFOAM forceCoeffs columns: Time Cm Cd Cl Cl(f) Cl(r)
    try:
        Cm     = float(cols[1])
        Cd_raw = float(cols[2])   # force in X direction (global)
        Cl_raw = float(cols[3])   # force in Y direction (global)
    except (IndexError, ValueError):
        return None, None, None

    # Rotate from global (x,y) to wind (drag/lift) axes
    a = math.radians(alpha_deg)
    Cl_true =  Cl_raw * math.cos(a) + Cd_raw * math.sin(a)
    Cd_true = -Cl_raw * math.sin(a) + Cd_raw * math.cos(a)

    return float(Cl_true), float(Cd_true), float(Cm)


# ── Helper: update velocity in 0/U ────────────────────────────────────────────
def set_velocity(case_dir: str, Vx: float, Vy: float):
    """Replace internalField and inlet velocity in 0/U."""
    u_file = os.path.join(case_dir, "0", "U")
    with open(u_file) as f:
        content = f.read()

    vel_str = f"({Vx:.5f} {Vy:.5f} 0)"

    # Replace internalField
    import re
    content = re.sub(
        r"internalField\s+uniform\s+\([^)]+\)",
        f"internalField   uniform {vel_str}",
        content
    )
    # Replace inlet value
    content = re.sub(
        r"(inlet\b.*?value\s+uniform\s+)\([^)]+\)",
        rf"\g<1>{vel_str}",
        content, flags=re.DOTALL
    )

    with open(u_file, "w") as f:
        f.write(content)


# ── Main sweep ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  CycloProp OpenFOAM Polar Sweep")
    print(f"  Airfoils : {', '.join(AIRFOILS)}")
    print(f"  AoA range: {ALPHAS[0]}° to {ALPHAS[-1]}° in 5° steps")
    print(f"  V_inlet  : {V_INLET} m/s  (Re = 95,000, c = 38 mm)")
    print("=" * 70)

    if not os.path.isdir(BASE_TEMPLATE):
        print(f"\n⚠️  Base template not found: {BASE_TEMPLATE}")
        print("   Run: cp -r $(find /usr/lib/openfoam -name airFoil2D) ~/CycloProp_CFD/base_template")
        return

    for foil in AIRFOILS:
        result_path = os.path.join(RESULTS_DIR, f"{foil}_openfoam_Re95k.csv")

        print(f"\n{'─'*70}")
        print(f"  AIRFOIL: {foil.upper()}")
        print(f"{'─'*70}")

        rows = []
        for alpha in ALPHAS:
            Vx = V_INLET * math.cos(math.radians(alpha))
            Vy = V_INLET * math.sin(math.radians(alpha))

            case_dir = os.path.join(WORK_DIR, foil, f"alpha_{alpha:+d}")
            shutil.copytree(BASE_TEMPLATE, case_dir, dirs_exist_ok=True)

            # Set velocity
            set_velocity(case_dir, Vx, Vy)

            print(f"  α={alpha:+4d}°  Vx={Vx:7.3f}  Vy={Vy:7.3f}  → ", end="", flush=True)

            # Mesh
            rc_mesh = run("blockMesh", cwd=case_dir, logfile=os.path.join(case_dir, "log.blockMesh"))
            if rc_mesh != 0:
                print("MESH FAILED — see log.blockMesh")
                rows.append({"alpha_deg": alpha, "Cl": "ERR", "Cd": "ERR", "Cm": "ERR"})
                continue

            # Solve
            rc_solve = run("simpleFoam", cwd=case_dir, logfile=os.path.join(case_dir, "log.simpleFoam"))
            if rc_solve != 0:
                print("SOLVE FAILED — see log.simpleFoam")
                rows.append({"alpha_deg": alpha, "Cl": "ERR", "Cd": "ERR", "Cm": "ERR"})
                continue

            # Extract
            Cl, Cd, Cm = extract_coeffs(case_dir, alpha)
            if Cl is None:
                print("NO RESULT — check postProcessing folder")
                rows.append({"alpha_deg": alpha, "Cl": "ERR", "Cd": "ERR", "Cm": "ERR"})
            else:
                ClCd = f"{Cl/Cd:.1f}" if Cd and Cd != 0 else "∞"
                print(f"Cl={Cl:+.4f}  Cd={Cd:.5f}  Cl/Cd={ClCd}")
                rows.append({"alpha_deg": alpha, "Cl": f"{Cl:.6f}",
                             "Cd": f"{Cd:.6f}", "Cm": f"{Cm:.6f}"})

        # Write CSV
        with open(result_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["alpha_deg", "Cl", "Cd", "Cm"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n  ✓ Saved: {result_path}")

    print("\n" + "=" * 70)
    print("  All sweeps complete.")
    print(f"  Results in: {RESULTS_DIR}")
    print("  Next: copy CSVs to Windows → run integrate_cfd_polars.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
