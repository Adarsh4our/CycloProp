#!/usr/bin/env python3
"""
CycloProp — Automated C-Grid blockMeshDict Generator for 2D Airfoils
=====================================================================
Generates a high-quality, structured C-grid mesh in OpenFOAM format
from normalized 2D airfoil coordinates (.dat).

Compatible with OpenFOAM v2412 / v2012 / v1912 / OpenFOAM-9/10/11.
"""

import os
import sys
import numpy as np

def load_airfoil_coords(dat_path):
    """
    Load normalized coordinates from .dat file.
    Expects upper surface LE->TE (indices 0..N-1) then lower surface TE->LE (indices N..2N-1).
    """
    coords = []
    with open(dat_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            coords.append([float(parts[0]), float(parts[1])])
    
    coords = np.array(coords)
    n_pts = len(coords)
    half = n_pts // 2
    
    upper = coords[:half]         # x from 0 to 1, y >= 0
    lower = coords[half:]         # x from 1 to 0, y <= 0
    
    # Sort lower so it goes from LE (0) to TE (1)
    lower_le_to_te = lower[::-1]
    
    return upper, lower_le_to_te

def generate_blockmeshdict(dat_path, out_file, chord=0.038, H_chord=12.0, D_chord=20.0,
                           N_le=50, N_te=75, N_wake=60, N_radial=50,
                           exp_radial=150.0, exp_wake=30.0):
    """
    Generate OpenFOAM blockMeshDict with C-grid topology.
    chord: blade chord in meters (scale factor)
    H_chord: far-field radius and half-height in chords
    D_chord: downstream outlet length in chords
    """
    upper, lower = load_airfoil_coords(dat_path)
    
    # Find max thickness on upper surface
    idx_upper_mt = np.argmax(upper[:, 1])
    x_mt = upper[idx_upper_mt, 0]
    y_mt_upper = upper[idx_upper_mt, 1]
    
    # Find corresponding point on lower surface closest to x_mt
    idx_lower_mt = np.argmin(np.abs(lower[:, 0] - x_mt))
    y_mt_lower = lower[idx_lower_mt, 1]
    
    # Domain dimensions (in normalized units, scaled by scale factor = chord)
    H = H_chord
    D = D_chord
    W = 0.05   # 2D spanwise thickness
    
    # Spline points along airfoil surfaces
    # Segment 1: Upper LE -> MT
    pts_upper_le_mt = upper[1:idx_upper_mt]
    # Segment 2: Upper MT -> TE
    pts_upper_mt_te = upper[idx_upper_mt+1:-1]
    # Segment 3: Lower LE -> MT
    pts_lower_le_mt = lower[1:idx_lower_mt]
    # Segment 4: Lower MT -> TE
    pts_lower_mt_te = lower[idx_lower_mt+1:-1]
    
    # 2D Vertices in (x, y)
    # 0: LE (0, 0)
    # 1: Upper MT (x_mt, y_mt_upper)
    # 2: TE (1, 0)
    # 3: Lower MT (x_mt, y_mt_lower)
    # 4: Inlet nose (x_mt - H, 0)
    # 5: Inlet top (x_mt, H)
    # 6: Inlet bottom (x_mt, -H)
    # 7: Top mid (1, H)
    # 8: Top outlet (D, H)
    # 9: Bottom mid (1, -H)
    # 10: Bottom outlet (D, -H)
    # 11: Outlet mid (D, 0)
    
    v2d = [
        [0.0, 0.0],              # 0: LE
        [x_mt, y_mt_upper],       # 1: Upper MT
        [1.0, 0.0],              # 2: TE
        [x_mt, y_mt_lower],       # 3: Lower MT
        [x_mt - H, 0.0],         # 4: Inlet nose
        [x_mt, H],               # 5: Inlet top
        [x_mt, -H],              # 6: Inlet bottom
        [1.0, H],                # 7: Top mid
        [D, H],                  # 8: Top outlet
        [1.0, -H],               # 9: Bottom mid
        [D, -H],                 # 10: Bottom outlet
        [D, 0.0],                # 11: Outlet mid
    ]
    
    # 3D vertices: 0..11 at z = -W, 12..23 at z = +W
    vertices = []
    for x, y in v2d:
        vertices.append([x, y, -W])
    for x, y in v2d:
        vertices.append([x, y, +W])
        
    # Inlet arc midpoint calculation
    # Top arc from 4 to 5: center is (x_mt, 0), angle from 180° to 90°, mid at 135°
    arc_top_mid = [x_mt - H * np.cos(np.pi / 4), H * np.sin(np.pi / 4)]
    # Bottom arc from 4 to 6: center is (x_mt, 0), angle from 180° to 270°, mid at 225°
    arc_bot_mid = [x_mt - H * np.cos(np.pi / 4), -H * np.sin(np.pi / 4)]

    # Format output
    lines = []
    lines.append("/*--------------------------------*- C++ -*----------------------------------*\\")
    lines.append("| =========                 |                                                 |")
    lines.append("| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |")
    lines.append("|  \\\\    /   O peration     | Version:  v2412                                 |")
    lines.append("|   \\\\  /    A nd           | Website:  www.openfoam.com                      |")
    lines.append("|    \\\\/     M anipulation  |                                                 |")
    lines.append("\\*---------------------------------------------------------------------------*/")
    lines.append("FoamFile")
    lines.append("{")
    lines.append("    version     2.0;")
    lines.append("    format      ascii;")
    lines.append("    class       dictionary;")
    lines.append("    object      blockMeshDict;")
    lines.append("}")
    lines.append("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //")
    lines.append("")
    lines.append(f"scale   {chord:.6f};")
    lines.append("")
    lines.append("vertices")
    lines.append("(")
    for i, (x, y, z) in enumerate(vertices):
        lines.append(f"    ({x:14.8f} {y:14.8f} {z:14.8f}) // {i}")
    lines.append(");")
    lines.append("")
    lines.append("blocks")
    lines.append("(")
    
    # Block 0: Upper LE (0 1 5 4 12 13 17 16)
    # x1: 0->1 (N_le), x2: 1->5 (N_radial), x3: z (1)
    # Grading: radial clustered towards airfoil wall (start of radial is airfoil)
    lines.append(f"    hex (0 1 5 4 12 13 17 16) ({N_le} {N_radial} 1) simpleGrading (1 {exp_radial:.1f} 1) // Block 0: Upper LE")
    
    # Block 1: Upper airfoil (1 2 7 5 13 14 19 17)
    # x1: 1->2 (N_te), x2: 2->7 (N_radial), x3: z (1)
    lines.append(f"    hex (1 2 7 5 13 14 19 17) ({N_te} {N_radial} 1) simpleGrading (1 {exp_radial:.1f} 1) // Block 1: Upper Airfoil")
    
    # Block 2: Upper wake (2 11 8 7 14 23 20 19)
    # x1: 2->11 (N_wake), x2: 11->8 (N_radial), x3: z (1)
    lines.append(f"    hex (2 11 8 7 14 23 20 19) ({N_wake} {N_radial} 1) simpleGrading ({exp_wake:.1f} {exp_radial:.1f} 1) // Block 2: Upper Wake")
    
    # Block 3: Lower LE (4 6 3 0 16 18 15 12)
    # In Block 3: x1: 4->6 (N_le), x2: 6->3 (N_radial), x3: z (1)
    # Here, direction 2 goes from 6 (inlet bottom) to 3 (airfoil lower MT) -> inwards towards wall!
    # So grading in radial direction must be 1 / exp_radial to cluster near wall!
    inv_exp = 1.0 / exp_radial
    lines.append(f"    hex (4 6 3 0 16 18 15 12) ({N_le} {N_radial} 1) simpleGrading (1 {inv_exp:.6f} 1) // Block 3: Lower LE")
    
    # Block 4: Lower airfoil (6 9 2 3 18 21 14 15)
    # x1: 6->9 (N_te), x2: 9->2 (N_radial), x3: z (1)
    # Direction 2 goes from 9 (bottom mid) to 2 (TE) -> inwards towards airfoil!
    lines.append(f"    hex (6 9 2 3 18 21 14 15) ({N_te} {N_radial} 1) simpleGrading (1 {inv_exp:.6f} 1) // Block 4: Lower Airfoil")
    
    # Block 5: Lower wake (9 10 11 2 21 22 23 14)
    # x1: 9->10 (N_wake), x2: 10->11 (N_radial), x3: z (1)
    # Direction 2 goes from 10 to 11 -> inwards towards wake center!
    lines.append(f"    hex (9 10 11 2 21 22 23 14) ({N_wake} {N_radial} 1) simpleGrading ({exp_wake:.1f} {inv_exp:.6f} 1) // Block 5: Lower Wake")
    
    lines.append(");")
    lines.append("")
    lines.append("edges")
    lines.append("(")
    
    # Arcs for inlet
    lines.append(f"    arc 4 5 ({arc_top_mid[0]:.6f} {arc_top_mid[1]:.6f} {-W:.6f})")
    lines.append(f"    arc 16 17 ({arc_top_mid[0]:.6f} {arc_top_mid[1]:.6f} {W:.6f})")
    lines.append(f"    arc 4 6 ({arc_bot_mid[0]:.6f} {arc_bot_mid[1]:.6f} {-W:.6f})")
    lines.append(f"    arc 16 18 ({arc_bot_mid[0]:.6f} {arc_bot_mid[1]:.6f} {W:.6f})")
    
    # Splines for upper surface
    lines.append("    spline 0 1")
    lines.append("    (")
    for x, y in pts_upper_le_mt:
        lines.append(f"        ({x:.8f} {y:.8f} {-W:.6f})")
    lines.append("    )")
    lines.append("    spline 12 13")
    lines.append("    (")
    for x, y in pts_upper_le_mt:
        lines.append(f"        ({x:.8f} {y:.8f} {W:.6f})")
    lines.append("    )")
    
    lines.append("    spline 1 2")
    lines.append("    (")
    for x, y in pts_upper_mt_te:
        lines.append(f"        ({x:.8f} {y:.8f} {-W:.6f})")
    lines.append("    )")
    lines.append("    spline 13 14")
    lines.append("    (")
    for x, y in pts_upper_mt_te:
        lines.append(f"        ({x:.8f} {y:.8f} {W:.6f})")
    lines.append("    )")
    
    # Splines for lower surface
    # Note: Edge 0->3 in Block 3 goes from LE (0) to Lower MT (3)
    lines.append("    spline 0 3")
    lines.append("    (")
    for x, y in pts_lower_le_mt:
        lines.append(f"        ({x:.8f} {y:.8f} {-W:.6f})")
    lines.append("    )")
    lines.append("    spline 12 15")
    lines.append("    (")
    for x, y in pts_lower_le_mt:
        lines.append(f"        ({x:.8f} {y:.8f} {W:.6f})")
    lines.append("    )")
    
    # Edge 3->2 in Block 4 goes from Lower MT (3) to TE (2)
    lines.append("    spline 3 2")
    lines.append("    (")
    for x, y in pts_lower_mt_te:
        lines.append(f"        ({x:.8f} {y:.8f} {-W:.6f})")
    lines.append("    )")
    lines.append("    spline 15 14")
    lines.append("    (")
    for x, y in pts_lower_mt_te:
        lines.append(f"        ({x:.8f} {y:.8f} {W:.6f})")
    lines.append("    )")
    
    lines.append(");")
    lines.append("")
    lines.append("boundary")
    lines.append("(")
    
    # Airfoil wall patch
    lines.append("    airfoil")
    lines.append("    {")
    lines.append("        type wall;")
    lines.append("        faces")
    lines.append("        (")
    lines.append("            (0 12 13 1)   // Upper LE->MT")
    lines.append("            (1 13 14 2)   // Upper MT->TE")
    lines.append("            (0 3 15 12)   // Lower LE->MT")
    lines.append("            (3 2 14 15)   // Lower MT->TE")
    lines.append("        );")
    lines.append("    }")
    lines.append("")
    
    # Inlet patch (arc)
    lines.append("    inlet")
    lines.append("    {")
    lines.append("        type patch;")
    lines.append("        faces")
    lines.append("        (")
    lines.append("            (4 5 17 16)   // Upper inlet arc")
    lines.append("            (4 16 18 6)   // Lower inlet arc")
    lines.append("        );")
    lines.append("    }")
    lines.append("")
    
    # Top and bottom far-field patches
    lines.append("    topAndBottom")
    lines.append("    {")
    lines.append("        type patch;")
    lines.append("        faces")
    lines.append("        (")
    lines.append("            (5 7 19 17)   // Top mid")
    lines.append("            (7 8 20 19)   // Top outlet")
    lines.append("            (6 18 21 9)   // Bottom mid")
    lines.append("            (9 21 22 10)  // Bottom outlet")
    lines.append("        );")
    lines.append("    }")
    lines.append("")
    
    # Outlet patch
    lines.append("    outlet")
    lines.append("    {")
    lines.append("        type patch;")
    lines.append("        faces")
    lines.append("        (")
    lines.append("            (8 11 23 20)  // Upper outlet")
    lines.append("            (11 10 22 23) // Lower outlet")
    lines.append("        );")
    lines.append("    }")
    lines.append("")
    
    # 2D front and back empty patches
    lines.append("    frontAndBack")
    lines.append("    {")
    lines.append("        type empty;")
    lines.append("        faces")
    lines.append("        (")
    # Back faces (z = -W)
    lines.append("            (0 1 5 4)     // Block 0 back")
    lines.append("            (1 2 7 5)     // Block 1 back")
    lines.append("            (2 11 8 7)    // Block 2 back")
    lines.append("            (4 6 3 0)     // Block 3 back")
    lines.append("            (6 9 2 3)     // Block 4 back")
    lines.append("            (9 10 11 2)   // Block 5 back")
    # Front faces (z = +W)
    lines.append("            (12 16 17 13) // Block 0 front")
    lines.append("            (13 17 19 14) // Block 1 front")
    lines.append("            (14 19 20 23) // Block 2 front")
    lines.append("            (16 12 15 18) // Block 3 front")
    lines.append("            (18 15 14 21) // Block 4 front")
    lines.append("            (21 14 23 22) // Block 5 front")
    lines.append("        );")
    lines.append("    }")
    lines.append(");")
    lines.append("")
    lines.append("// ************************************************************************* //")
    
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    with open(out_file, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  ✓ Generated: {out_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_cgrid.py <airfoil.dat> <output_blockMeshDict>")
        sys.exit(1)
    generate_blockmeshdict(sys.argv[1], sys.argv[2])
