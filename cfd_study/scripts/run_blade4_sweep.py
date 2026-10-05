#!/usr/bin/env python3
"""
CycloProp — Blade 4 (NACA 63-012A) Full Polar Sweep (-40° to +40°, step 5°)
============================================================================
Automates the full angle of attack sweep for NACA 63-012A:
- Generates structured C-grid for each angle (-40° to +40° in 5° steps)
- Solves RANS simpleFoam with k-omega SST at Re=95,000, c=38mm
- Logs every single iteration data point to results/iteration_logs/
- Updates master_cfd_results.csv
- Exports final polar to results/naca63012_openfoam_Re95k.csv
- Generates 4-panel aerodynamic polar dashboard plot
- Generates comparative plot: NACA 0012 (Conventional) vs NACA 63-012A (Laminar)
"""

import os
import sys
import shutil
import subprocess
import csv
import re
import matplotlib.pyplot as plt

# Paths
REPO_DIR = "/home/tinkererslab/CycloProp"
BASE_DIR = os.path.join(REPO_DIR, "cfd_study", "openfoam", "blade4_naca63012")
COORDS_FILE = os.path.join(REPO_DIR, "cfd_study", "airfoil_coords", "naca63012_normalized.dat")
TEMPLATE_DIR = os.path.join(REPO_DIR, "cfd_study", "openfoam", "blade1_naca0012", "alpha_0")
RESULTS_DIR = os.path.join(REPO_DIR, "cfd_study", "results")
LOGS_DIR = os.path.join(RESULTS_DIR, "iteration_logs")

# Import mesh generator and logger
sys.path.insert(0, os.path.join(REPO_DIR, "cfd_study", "scripts"))
from generate_mesh import generate_mesh
from log_iteration_data import log_case_data

ANGLES = list(range(-40, 41, 5))  # -40 to +40 in 5° steps (17 angles)

def run_cmd(cmd, cwd=None):
    res = subprocess.run(f"bash -c 'source /usr/lib/openfoam/openfoam2412/etc/bashrc && {cmd}'",
                         shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr

def setup_case(case_dir, alpha):
    """Setup OpenFOAM case directory for a specific angle."""
    # Clean any previous partial run
    if os.path.exists(case_dir):
        for item in os.listdir(case_dir):
            p = os.path.join(case_dir, item)
            if item.isdigit() and int(item) > 0 and os.path.isdir(p):
                shutil.rmtree(p)
        post_dir = os.path.join(case_dir, "postProcessing")
        if os.path.exists(post_dir):
            shutil.rmtree(post_dir)
            
    os.makedirs(os.path.join(case_dir, "0"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "constant"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
    
    # 1. Generate mesh
    generate_mesh(COORDS_FILE, case_dir, float(alpha))
    
    # 2. Copy base templates from blade 1
    for f in ["transportProperties", "turbulenceProperties"]:
        shutil.copy(os.path.join(TEMPLATE_DIR, "constant", f), os.path.join(case_dir, "constant", f))
        
    for f in ["U", "p", "k", "omega", "nut"]:
        src = os.path.join(TEMPLATE_DIR, "0", f)
        dst = os.path.join(case_dir, "0", f)
        with open(src) as fp:
            text = fp.read()
        # Ensure symmetry patch type in 0 files
        text = re.sub(r'type\s+(symmetryPlane|empty)\s*;', 'type symmetry;', text)
        with open(dst, "w") as fp:
            fp.write(text)

    if abs(alpha) >= 25:
        # Use stabilized relaxation factors and bounded upwind schemes for deep stall
        fv_sol = """FoamFile
{
    version 2.0; format ascii; class dictionary; object fvSolution;
}
solvers
{
    p { solver GAMG; smoother GaussSeidel; tolerance 1e-6; relTol 0.05; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-6; relTol 0.1; }
}
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl { p 1e-4; U 1e-4; "(k|omega)" 1e-4; }
}
relaxationFactors
{
    fields { p 0.2; }
    equations { U 0.4; "(k|omega)" 0.4; }
}
"""
        fv_sch = """FoamFile
{
    version 2.0; format ascii; class dictionary; object fvSchemes;
}
ddtSchemes { default steadyState; }
gradSchemes
{
    default Gauss linear;
    grad(p) Gauss linear;
    grad(U) cellLimited Gauss linear 1;
    grad(k) cellLimited Gauss linear 1;
    grad(omega) cellLimited Gauss linear 1;
}
divSchemes
{
    default none;
    div(phi,U) bounded Gauss upwind;
    div(phi,k) bounded Gauss upwind;
    div(phi,omega) bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
"""
        with open(os.path.join(case_dir, "system", "fvSolution"), "w") as f:
            f.write(fv_sol)
        with open(os.path.join(case_dir, "system", "fvSchemes"), "w") as f:
            f.write(fv_sch)
    else:
        for f in ["fvSchemes", "fvSolution"]:
            shutil.copy(os.path.join(TEMPLATE_DIR, "system", f), os.path.join(case_dir, "system", f))
        
    # 3. Create controlDict with 450 iterations
    ctrl = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}}
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         450;
deltaT          1;
writeControl    timeStep;
writeInterval   100;
purgeWrite      2;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;

functions
{{
    forceCoeffs
    {{
        type            forceCoeffs;
        libs            ("libforces.so");
        writeControl    timeStep;
        writeInterval   10;
        patches         (airfoil);
        rho             rhoInf;
        rhoInf          1.225;
        magUInf         36.8;
        lRef            0.038;
        Aref            0.038;
        liftDir         (0 0 1);
        dragDir         (1 0 0);
        pitchAxis       (0 1 0);
        CofR            (0 0 0);
    }}
}}
"""
    with open(os.path.join(case_dir, "system", "controlDict"), "w") as f:
        f.write(ctrl)

def is_case_completed(case_dir):
    coeff_file = os.path.join(case_dir, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
    if not os.path.exists(coeff_file):
        return False
    with open(coeff_file) as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    return len(lines) >= 30

def extract_final_coeffs(case_dir):
    coeff_file = os.path.join(case_dir, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
    if not os.path.exists(coeff_file):
        return None, None, None
    last_line = None
    with open(coeff_file) as f:
        for l in f:
            if not l.startswith("#") and l.strip():
                last_line = l
    if not last_line:
        return None, None, None
    cols = last_line.split()
    return float(cols[4]), float(cols[1]), float(cols[7])  # Cl, Cd, Cm

def plot_master_polar(results, out_png):
    alphas = [r["alpha"] for r in results]
    cls = [r["Cl"] for r in results]
    cds = [r["Cd"] for r in results]
    cl_cds = [cl / cd if cd != 0 else 0 for cl, cd in zip(cls, cds)]
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), facecolor='white')
    
    # 1. Lift Curve
    axs[0, 0].plot(alphas, cls, 'o-', color='#0077b6', lw=2.2, ms=6, label='NACA 63-012A (k-ω SST, Re=95k)')
    axs[0, 0].axhline(0, color='gray', lw=0.8, ls=':')
    axs[0, 0].axvline(0, color='gray', lw=0.8, ls=':')
    axs[0, 0].set_title("1. Lift Curve (Cl vs Angle of Attack)", fontsize=12, fontweight='bold')
    axs[0, 0].set_xlabel("Angle of Attack α (°)", fontsize=10)
    axs[0, 0].set_ylabel("Lift Coefficient Cl", fontsize=10)
    axs[0, 0].grid(True, ls=':', alpha=0.5)
    axs[0, 0].legend(loc='upper left', fontsize=9)
    
    # 2. Drag Polar
    axs[0, 1].plot(alphas, cds, 's-', color='#e63946', lw=2.2, ms=6, label='NACA 63-012A Drag')
    axs[0, 1].axvline(0, color='gray', lw=0.8, ls=':')
    axs[0, 1].set_title("2. Drag Curve (Cd vs Angle of Attack)", fontsize=12, fontweight='bold')
    axs[0, 1].set_xlabel("Angle of Attack α (°)", fontsize=10)
    axs[0, 1].set_ylabel("Drag Coefficient Cd", fontsize=10)
    axs[0, 1].grid(True, ls=':', alpha=0.5)
    axs[0, 1].legend(loc='upper center', fontsize=9)
    
    # 3. Aerodynamic Efficiency
    axs[1, 0].plot(alphas, cl_cds, '^-', color='#2a9d8f', lw=2.2, ms=6, label='NACA 63-012A L/D')
    axs[1, 0].axhline(0, color='gray', lw=0.8, ls=':')
    axs[1, 0].axvline(0, color='gray', lw=0.8, ls=':')
    axs[1, 0].set_title("3. Aerodynamic Efficiency (Cl / Cd vs α)", fontsize=12, fontweight='bold')
    axs[1, 0].set_xlabel("Angle of Attack α (°)", fontsize=10)
    axs[1, 0].set_ylabel("Cl / Cd Ratio", fontsize=10)
    axs[1, 0].grid(True, ls=':', alpha=0.5)
    axs[1, 0].legend(loc='upper left', fontsize=9)
    
    # 4. Drag Polar (Cl vs Cd)
    axs[1, 1].plot(cds, cls, 'd-', color='#1d3557', lw=2.2, ms=6, label='NACA 63-012A Polar')
    axs[1, 1].axhline(0, color='gray', lw=0.8, ls=':')
    axs[1, 1].set_title("4. Drag Polar Curve (Cl vs Cd)", fontsize=12, fontweight='bold')
    axs[1, 1].set_xlabel("Drag Coefficient Cd", fontsize=10)
    axs[1, 1].set_ylabel("Lift Coefficient Cl", fontsize=10)
    axs[1, 1].grid(True, ls=':', alpha=0.5)
    axs[1, 1].legend(loc='lower right', fontsize=9)
    
    plt.suptitle("CycloProp Blade 4 — NACA 63-012A Full Aerodynamic Polar Sweep (-40° to +40°)",
                 fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n  ✓ Master Polar Dashboard saved: {out_png}")

def plot_airfoil_comparison_6series(naca12_csv, naca63_results, out_png):
    """Generate comparative plot: NACA 0012 (Conventional) vs NACA 63-012A (Laminar)."""
    n12_data = {}
    if os.path.exists(naca12_csv):
        with open(naca12_csv) as f:
            for r in csv.DictReader(f):
                n12_data[int(r["alpha_deg"])] = {
                    "Cl": float(r["Cl"]), "Cd": float(r["Cd"]), "Cm": float(r["Cm"])
                }
    if not n12_data:
        return

    common_alphas = sorted(list(set(n12_data.keys()).intersection(set([r["alpha"] for r in naca63_results]))))
    if not common_alphas:
        return

    n12_cl = [n12_data[a]["Cl"] for a in common_alphas]
    n12_cd = [n12_data[a]["Cd"] for a in common_alphas]
    
    n63_dict = {r["alpha"]: r for r in naca63_results}
    n63_cl = [n63_dict[a]["Cl"] for a in common_alphas]
    n63_cd = [n63_dict[a]["Cd"] for a in common_alphas]
    
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.5), facecolor='white')
    
    # Lift Comparison
    axs[0].plot(common_alphas, n12_cl, 'o-', color='#1d3557', lw=2.2, label='NACA 0012 (4-Digit Conventional)')
    axs[0].plot(common_alphas, n63_cl, 's--', color='#0077b6', lw=2.2, label='NACA 63-012A (6-Series Laminar)')
    axs[0].axhline(0, color='gray', lw=0.8, ls=':')
    axs[0].axvline(0, color='gray', lw=0.8, ls=':')
    axs[0].set_title("Lift Coefficient Comparison (Cl vs α)", fontsize=12, fontweight='bold')
    axs[0].set_xlabel("Angle of Attack α (°)", fontsize=10)
    axs[0].set_ylabel("Lift Coefficient Cl", fontsize=10)
    axs[0].grid(True, ls=':', alpha=0.5)
    axs[0].legend(fontsize=10)
    
    # Drag Comparison
    axs[1].plot(common_alphas, n12_cd, 'o-', color='#1d3557', lw=2.2, label='NACA 0012 (4-Digit Conventional)')
    axs[1].plot(common_alphas, n63_cd, 's--', color='#0077b6', lw=2.2, label='NACA 63-012A (6-Series Laminar)')
    axs[1].axvline(0, color='gray', lw=0.8, ls=':')
    axs[1].set_title("Drag Coefficient Comparison (Cd vs α)", fontsize=12, fontweight='bold')
    axs[1].set_xlabel("Angle of Attack α (°)", fontsize=10)
    axs[1].set_ylabel("Drag Coefficient Cd", fontsize=10)
    axs[1].grid(True, ls=':', alpha=0.5)
    axs[1].legend(fontsize=10)
    
    plt.suptitle("CycloProp Aerodynamic Comparison: NACA 0012 (Chosen) vs NACA 63-012A (Laminar)",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_png, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Comparative Plot saved: {out_png}")

def run_single_angle(alpha):
    """Run one single angle for Blade 4."""
    tag = f"alpha_{alpha:+d}" if alpha != 0 else "alpha_0"
    case_dir = os.path.join(BASE_DIR, tag)
    print(f"\n>>> Setting up Blade 4 (NACA 63-012A) at α = {alpha:+d}° in {case_dir}")
    setup_case(case_dir, alpha)
    
    print(">>> Meshing with blockMesh...")
    rc, out, err = run_cmd("blockMesh", cwd=case_dir)
    if rc != 0:
        print(f"Error in blockMesh: {err}")
        return None
        
    print(">>> Solving simpleFoam...")
    rc, out, err = run_cmd("simpleFoam > log.simpleFoam 2>&1", cwd=case_dir)
    if rc != 0:
        print(f"Error in simpleFoam: {err}")
        return None
        
    # Log iteration data
    log_case_data(case_dir, "blade4_naca63012", alpha, RESULTS_DIR)
    cl, cd, cm = extract_final_coeffs(case_dir)
    print(f"\n[Result α={alpha:+d}°] -> Cl = {cl:+.4f}, Cd = {cd:.5f}, Cm = {cm:+.4f}")
    return {"alpha": alpha, "Cl": cl, "Cd": cd, "Cm": cm}

def main():
    print("=" * 75)
    print("  CycloProp — Blade 4 (NACA 63-012A) Full Polar Sweep")
    print("  Range: -40° to +40° in 5° steps (17 angles)")
    print("  Condition: Re = 95,000 | Chord c = 38 mm | V = 36.8 m/s")
    print("=" * 75)
    
    sweep_results = []
    
    for alpha in ANGLES:
        tag = f"alpha_{alpha:+d}" if alpha != 0 else "alpha_0"
        case_dir = os.path.join(BASE_DIR, tag)
        
        print(f"\n[{ANGLES.index(alpha)+1}/{len(ANGLES)}] Angle α = {alpha:+3d}°: ", end="", flush=True)
        
        if is_case_completed(case_dir):
            print("Already solved! Logging...", end="", flush=True)
        else:
            print("Meshing...", end="", flush=True)
            setup_case(case_dir, alpha)
            rc, out, err = run_cmd("blockMesh", cwd=case_dir)
            if rc != 0:
                print(" [ERROR: blockMesh failed]")
                continue
                
            print(" Solving...", end="", flush=True)
            rc, out, err = run_cmd("simpleFoam > log.simpleFoam 2>&1", cwd=case_dir)
            if rc != 0:
                print(" [ERROR: simpleFoam failed]")
                continue
                
        # Log iteration history
        log_case_data(case_dir, "blade4_naca63012", alpha, RESULTS_DIR)
        
        # Read final coefficients
        cl, cd, cm = extract_final_coeffs(case_dir)
        if cl is not None:
            cl_cd = cl / cd if cd != 0 else 0
            print(f" -> Cl = {cl:+7.4f} | Cd = {cd:7.5f} | Cl/Cd = {cl_cd:6.1f} | Cm = {cm:+7.4f}")
            sweep_results.append({"alpha": alpha, "Cl": cl, "Cd": cd, "Cm": cm})
        else:
            print(" [ERROR: Could not read coefficients]")
            
    # Export final polar CSV
    polar_csv = os.path.join(RESULTS_DIR, "naca63012_openfoam_Re95k.csv")
    with open(polar_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alpha_deg", "Cl", "Cd", "Cm"])
        writer.writeheader()
        for r in sweep_results:
            writer.writerow({"alpha_deg": r["alpha"], "Cl": f"{r['Cl']:.6f}",
                             "Cd": f"{r['Cd']:.6f}", "Cm": f"{r['Cm']:.6f}"})
    print(f"\n{'='*75}")
    print(f"  ✓ Exported Final Polar CSV: {polar_csv}")
    
    # Plot Master Polar
    dashboard_png = os.path.join(BASE_DIR, "naca63012_polar_dashboard.png")
    plot_master_polar(sweep_results, dashboard_png)
    
    # Plot Comparison with NACA 0012
    comp_png = os.path.join(RESULTS_DIR, "airfoil_comparison_naca0012_vs_naca63012.png")
    naca12_csv = os.path.join(RESULTS_DIR, "naca0012_openfoam_Re95k.csv")
    plot_airfoil_comparison_6series(naca12_csv, sweep_results, comp_png)
    print("=" * 75)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        alpha = int(sys.argv[2])
        run_single_angle(alpha)
    else:
        main()
