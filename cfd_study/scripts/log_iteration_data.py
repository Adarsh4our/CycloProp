#!/usr/bin/env python3
"""
CycloProp — Iteration Data Logger & Master CFD Database
======================================================
Extracts full iteration-by-iteration convergence histories (forces + residuals)
for every blade and angle tested, saving detailed CSV logs and updating the master database.
"""

import os
import sys
import re
import csv
import numpy as np

def parse_log_residuals(log_file):
    """Extract residuals for each iteration from log.simpleFoam."""
    res_data = {}  # iter -> dict of residuals
    if not os.path.exists(log_file):
        return res_data
        
    current_iter = None
    with open(log_file) as f:
        for line in f:
            if line.startswith("Time = "):
                try:
                    current_iter = int(line.split("=")[-1].strip())
                    if current_iter not in res_data:
                        res_data[current_iter] = {}
                except ValueError:
                    pass
            elif current_iter is not None:
                if "Solving for Ux" in line:
                    m = re.search(r'Initial residual = ([0-9.eE+-]+)', line)
                    if m: res_data[current_iter]["res_Ux"] = float(m.group(1))
                elif "Solving for Uz" in line:
                    m = re.search(r'Initial residual = ([0-9.eE+-]+)', line)
                    if m: res_data[current_iter]["res_Uz"] = float(m.group(1))
                elif "Solving for p," in line:
                    m = re.search(r'Initial residual = ([0-9.eE+-]+)', line)
                    if m: res_data[current_iter]["res_p"] = float(m.group(1))
                elif "Solving for k," in line:
                    m = re.search(r'Initial residual = ([0-9.eE+-]+)', line)
                    if m: res_data[current_iter]["res_k"] = float(m.group(1))
                elif "Solving for omega," in line:
                    m = re.search(r'Initial residual = ([0-9.eE+-]+)', line)
                    if m: res_data[current_iter]["res_omega"] = float(m.group(1))
                elif "time step continuity errors" in line:
                    m = re.search(r'sum local = ([0-9.eE+-]+)', line)
                    if m: res_data[current_iter]["continuity_error"] = float(m.group(1))
                    
    return res_data

def log_case_data(case_dir, blade_name, alpha_deg, results_dir="/home/tinkererslab/CycloProp/cfd_study/results"):
    """
    Combines force coefficients and residuals for every iteration into a clean CSV file.
    Also records the final converged data point in master_cfd_results.csv.
    """
    coeff_file = os.path.join(case_dir, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
    log_file = os.path.join(case_dir, "log.simpleFoam")
    
    if not os.path.exists(coeff_file):
        print(f"Warning: {coeff_file} not found")
        return None
        
    res_data = parse_log_residuals(log_file)
    
    # Read coefficients
    iter_rows = []
    with open(coeff_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 8:
                try:
                    it = int(parts[0])
                    cd = float(parts[1])
                    cd_front = float(parts[2])
                    cd_rear  = float(parts[3])
                    cl = float(parts[4])
                    cl_front = float(parts[5])
                    cl_rear  = float(parts[6])
                    cm = float(parts[7])
                    
                    r = res_data.get(it, {})
                    iter_rows.append({
                        "iteration": it,
                        "Cd": cd,
                        "Cd_front": cd_front,
                        "Cd_rear": cd_rear,
                        "Cl": cl,
                        "Cl_front": cl_front,
                        "Cl_rear": cl_rear,
                        "Cm": cm,
                        "res_Ux": r.get("res_Ux", ""),
                        "res_Uz": r.get("res_Uz", ""),
                        "res_p": r.get("res_p", ""),
                        "res_k": r.get("res_k", ""),
                        "res_omega": r.get("res_omega", ""),
                        "continuity_error": r.get("continuity_error", "")
                    })
                except ValueError:
                    pass

    # Save detailed iteration log
    logs_dir = os.path.join(results_dir, "iteration_logs")
    os.makedirs(logs_dir, exist_ok=True)
    out_csv = os.path.join(logs_dir, f"{blade_name}_alpha_{alpha_deg:+d}_iterations.csv")
    
    fieldnames = [
        "iteration", "Cd", "Cd_front", "Cd_rear", "Cl", "Cl_front", "Cl_rear", "Cm",
        "res_Ux", "res_Uz", "res_p", "res_k", "res_omega", "continuity_error"
    ]
    
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(iter_rows)
        
    print(f"  ✓ Saved full iteration history ({len(iter_rows)} points) to:")
    print(f"    {out_csv}")
    
    # Update master summary CSV
    master_csv = os.path.join(results_dir, "master_cfd_results.csv")
    file_exists = os.path.exists(master_csv)
    
    final = iter_rows[-1] if iter_rows else {}
    master_fields = ["blade", "alpha_deg", "converged_iter", "Cl", "Cd", "Cm", "res_p", "res_Ux", "detail_log"]
    
    # Check if record already exists, update or append
    existing_rows = []
    if file_exists:
        with open(master_csv, "r") as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            
    updated = False
    for r in existing_rows:
        if r["blade"] == blade_name and float(r["alpha_deg"]) == float(alpha_deg):
            r["converged_iter"] = final.get("iteration", "")
            r["Cl"] = final.get("Cl", "")
            r["Cd"] = final.get("Cd", "")
            r["Cm"] = final.get("Cm", "")
            r["res_p"] = final.get("res_p", "")
            r["res_Ux"] = final.get("res_Ux", "")
            r["detail_log"] = os.path.relpath(out_csv, results_dir)
            updated = True
            break
            
    if not updated and final:
        existing_rows.append({
            "blade": blade_name,
            "alpha_deg": alpha_deg,
            "converged_iter": final.get("iteration", ""),
            "Cl": final.get("Cl", ""),
            "Cd": final.get("Cd", ""),
            "Cm": final.get("Cm", ""),
            "res_p": final.get("res_p", ""),
            "res_Ux": final.get("res_Ux", ""),
            "detail_log": os.path.relpath(out_csv, results_dir)
        })
        
    with open(master_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=master_fields)
        writer.writeheader()
        writer.writerows(existing_rows)
        
    print(f"  ✓ Updated Master Database: {master_csv}")
    return out_csv

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: log_iteration_data.py <case_dir> <blade_name> <alpha_deg>")
        sys.exit(1)
    log_case_data(sys.argv[1], sys.argv[2], int(sys.argv[3]))
