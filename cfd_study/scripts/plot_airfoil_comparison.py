#!/usr/bin/env python3
"""
CycloProp — Blade Profile Visual Comparison (NACA 0012 vs NACA 0015)
===================================================================
Visualizes the geometry, thickness distribution, and structural cross-section
comparing our chosen design (NACA 0012) against original baseline (NACA 0015).
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

def load_coords(path):
    pts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            pts.append([float(x) for x in line.split()])
    return np.array(pts)

def plot_airfoil_comparison(out_png="/home/tinkererslab/CycloProp/cfd_study/openfoam/blade2_naca0015/airfoil_comparison_0012_vs_0015.png"):
    c_mm = 38.0
    file_0012 = "/home/tinkererslab/CycloProp/cfd_study/airfoil_coords/naca0012_normalized.dat"
    file_0015 = "/home/tinkererslab/CycloProp/cfd_study/airfoil_coords/naca0015_normalized.dat"
    
    pts_0012 = load_coords(file_0012) * c_mm
    pts_0015 = load_coords(file_0015) * c_mm
    
    half_12 = len(pts_0012) // 2
    half_15 = len(pts_0015) // 2
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [1.4, 1.0]}, facecolor='white')
    
    # 1. Overlay Plot (1:1 Aspect Ratio)
    ax1.plot(pts_0015[:, 0], pts_0015[:, 1], color='#e63946', lw=2.2, label='Blade 2: NACA 0015 (t/c = 15%, Max t = 5.70 mm) [Original Baseline]')
    ax1.plot(pts_0012[:, 0], pts_0012[:, 1], color='#1d3557', lw=2.2, label='Blade 1: NACA 0012 (t/c = 12%, Max t = 4.56 mm) [Chosen Design ★]')
    ax1.fill_between(pts_0015[:half_15, 0], pts_0015[:half_15, 1], pts_0015[half_15:][::-1, 1], color='#e63946', alpha=0.12)
    ax1.fill_between(pts_0012[:half_12, 0], pts_0012[:half_12, 1], pts_0012[half_12:][::-1, 1], color='#1d3557', alpha=0.20)
    
    ax1.set_xlim(-2, 40)
    ax1.set_ylim(-6, 6)
    ax1.set_aspect('equal')
    ax1.set_title("Geometric Profile Overlay (True 1:1 Scale — Blade Chord c = 38 mm)", fontsize=13, fontweight='bold', pad=10)
    ax1.set_xlabel("Chord Position x (mm)", fontsize=10)
    ax1.set_ylabel("Thickness z (mm)", fontsize=10)
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Annotate max thickness
    ax1.annotate("NACA 0015: 5.70 mm (+25% thicker)", xy=(11.4, 2.85), xytext=(15, 4.5),
                 arrowprops=dict(facecolor='#e63946', shrink=0.05, width=1.5, headwidth=7),
                 fontsize=10, fontweight='bold', color='#e63946')
    ax1.annotate("NACA 0012: 4.56 mm (Lower Drag)", xy=(11.4, 2.28), xytext=(18, -4.5),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.5, headwidth=7),
                 fontsize=10, fontweight='bold', color='#1d3557')
                 
    # 2. Thickness Distribution along Chord
    x_eval = np.linspace(0, c_mm, 200)
    t_12 = 2 * np.interp(x_eval, pts_0012[:half_12, 0], pts_0012[:half_12, 1])
    t_15 = 2 * np.interp(x_eval, pts_0015[:half_15, 0], pts_0015[:half_15, 1])
    
    ax2.plot(x_eval, t_15, color='#e63946', lw=2.0, label='NACA 0015 Total Thickness')
    ax2.plot(x_eval, t_12, color='#1d3557', lw=2.0, label='NACA 0012 Total Thickness')
    ax2.fill_between(x_eval, t_12, t_15, color='#f1faee', alpha=0.8, hatch='///', edgecolor='#e63946', label='Excess Profile Drag Thickness (20% Drag Penalty)')
    
    ax2.set_xlim(0, 38)
    ax2.set_ylim(0, 6.5)
    ax2.set_title("Cross-Sectional Blade Thickness Comparison", fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel("Chord Position x (mm)", fontsize=10)
    ax2.set_ylabel("Total Thickness (mm)", fontsize=10)
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=10)
    
    plt.suptitle("CycloProp Aerodynamic Trade-off: NACA 0012 vs NACA 0015 (Re = 95,000)", fontsize=15, fontweight='bold', y=0.98)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved comparison plot: {out_png}")

if __name__ == "__main__":
    plot_airfoil_comparison()
