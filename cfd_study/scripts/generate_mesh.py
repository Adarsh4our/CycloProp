#!/usr/bin/env python3
"""
CycloProp Universal Airfoil Mesh Generator
=========================================
Generates structured C-grid blockMeshDict from any normalized airfoil .dat file.
Supports NACA 0009, 0012, 0015, 0018, and NACA 63-012A at any angle of attack alpha.
"""

import os
import sys
import numpy as np

def generate_mesh(dat_file, case_dir, alpha_deg=0.0, chord=0.038,
                  Nx=160, ND=80, NT=60, ExpT=250.0, ExpD=50.0, ExpArc=30.0):
    """
    Generate blockMeshDict in case_dir/system/blockMeshDict.
    """
    alpha = np.radians(alpha_deg)
    
    # Load coordinates from dat file
    coords = []
    with open(dat_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            coords.append([float(parts[0]), float(parts[1])])
    
    coords = np.array(coords)
    half = len(coords) // 2
    upper_raw = coords[:half]         # 0 to 1
    lower_raw = coords[half:][::-1]   # 0 to 1
    
    # Cosine spacing for interpolation
    Ni = 400
    beta = np.linspace(0, np.pi, Ni)
    x = 0.5 * (1.0 - np.cos(beta))
    
    # Interpolate upper and lower surfaces
    Zu_raw = np.interp(x, upper_raw[:, 0], upper_raw[:, 1])
    Zl_raw = np.interp(x, lower_raw[:, 0], lower_raw[:, 1])
    
    # Enforce sharp closed trailing edge (prevents grid folding at high angles)
    z_te = 0.5 * (Zu_raw[-1] + Zl_raw[-1])
    Zu_raw[-1] = z_te
    Zl_raw[-1] = z_te
    
    # Shift to quarter-chord
    Xu_raw = x - 0.25
    Xl_raw = x - 0.25
    
    # Rotate by alpha
    rot = np.array([[np.cos(alpha), np.sin(alpha)],
                    [-np.sin(alpha), np.cos(alpha)]])
    
    upper_rot = rot @ np.vstack((Xu_raw, Zu_raw))
    lower_rot = rot @ np.vstack((Xl_raw, Zl_raw))
    
    Xu = upper_rot[0]
    Zu = upper_rot[1]
    Xl = lower_rot[0]
    Zl = lower_rot[1]
    
    # Domain dimensions (in non-dimensional units, scaled by chord)
    H = 8.0     # Half-height (8 chords)
    D = 16.0    # Downstream length (16 chords)
    # Spanwise thickness: set W such that 2 * W * chord = 1.0 m (unit span)
    W = 0.5 / chord
    scale = chord
    
    # Find max thickness location on raw profile
    thick = Zu_raw - Zl_raw
    C_max_idx = np.argmax(thick)
    
    # Nose point of mesh
    NoseX = (-H + Xu[C_max_idx]) * np.cos(alpha)
    NoseZ = -(-H + Xu[C_max_idx]) * np.sin(alpha)
    
    # 12 Vertices at +W (plane 1)
    vertices1 = np.zeros((12, 3))
    vertices1[0]  = [NoseX, W, NoseZ]
    vertices1[1]  = [Xu[C_max_idx], W, H]
    vertices1[2]  = [Xu[-1], W, H]
    vertices1[3]  = [D, W, H]
    vertices1[4]  = [Xu[0], W, Zu[0]]
    vertices1[5]  = [Xu[C_max_idx], W, Zu[C_max_idx]]
    vertices1[6]  = [Xl[C_max_idx], W, Zl[C_max_idx]]
    vertices1[7]  = [Xu[-1], W, Zu[-1]]
    vertices1[8]  = [D, W, Zu[-1]]
    vertices1[9]  = [Xl[C_max_idx], W, -H]
    vertices1[10] = [Xu[-1], W, -H]
    vertices1[11] = [D, W, -H]
    
    # 12 Vertices at -W (plane 2)
    vertices2 = vertices1.copy()
    vertices2[:, 1] = -W
    
    vertices = np.vstack((vertices1, vertices2))
    
    # Spline edge points
    pts1 = np.column_stack([Xu[1:C_max_idx], W * np.ones(C_max_idx - 1), Zu[1:C_max_idx]])
    pts5 = np.column_stack([pts1[:, 0], -W * np.ones(len(pts1)), pts1[:, 2]])
    
    pts2 = np.column_stack([Xu[C_max_idx+1:-1], W * np.ones(Ni - 2 - C_max_idx), Zu[C_max_idx+1:-1]])
    pts6 = np.column_stack([pts2[:, 0], -W * np.ones(len(pts2)), pts2[:, 2]])
    
    pts3 = np.column_stack([Xl[1:C_max_idx], W * np.ones(C_max_idx - 1), Zl[1:C_max_idx]])
    pts7 = np.column_stack([pts3[:, 0], -W * np.ones(len(pts3)), pts3[:, 2]])
    
    pts4 = np.column_stack([Xl[C_max_idx+1:-1], W * np.ones(Ni - 2 - C_max_idx), Zl[C_max_idx+1:-1]])
    pts8 = np.column_stack([pts4[:, 0], -W * np.ones(len(pts4)), pts4[:, 2]])
    
    # Arcs for inlet
    pts9  = np.array([-H * np.cos(np.pi / 4) + Xu[C_max_idx], W, H * np.sin(np.pi / 4)])
    pts11 = np.array([pts9[0], -W, pts9[2]])
    
    pts10 = np.array([-H * np.cos(np.pi / 4) + Xu[C_max_idx], W, -H * np.sin(np.pi / 4)])
    pts12 = np.array([pts10[0], -W, pts10[2]])
    
    Nleading = int((x[C_max_idx]) * Nx)
    Ntrailing = Nx - Nleading
    NW = 1
    
    txt = "/*--------------------------------*- C++ -*----------------------------------*\\\n"
    txt += "| =========                 |                                                 |\n"
    txt += "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n"
    txt += "|  \\\\    /   O peration     | Version:  v2412                                 |\n"
    txt += "|   \\\\  /    A nd           | Web:      www.openfoam.com                      |\n"
    txt += "|    \\\\/     M anipulation  |                                                 |\n"
    txt += "\\*---------------------------------------------------------------------------*/\n"
    txt += "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object blockMeshDict;\n}\n"
    txt += "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n"
    txt += f"scale {scale:.8f};\n\n"
    txt += "vertices\n(\n"
    for v in vertices:
        txt += f"    ({v[0]:14.8f} {v[1]:14.8f} {v[2]:14.8f})\n"
    txt += ");\n\n"
    
    txt += "blocks\n(\n"
    txt += f"    hex (4 5 1 0 16 17 13 12)     ({Nleading} {NT} {NW}) edgeGrading (1 {1/ExpArc:.6f} {1/ExpArc:.6f} 1 {ExpT:.1f} {ExpT:.1f} {ExpT:.1f} {ExpT:.1f} 1 1 1 1)\n"
    txt += f"    hex (5 7 2 1 17 19 14 13)     ({Ntrailing} {NT} {NW}) simpleGrading (1 {ExpT:.1f} 1)\n"
    txt += f"    hex (7 8 3 2 19 20 15 14)     ({ND} {NT} {NW}) simpleGrading ({ExpD:.1f} {ExpT:.1f} 1)\n"
    txt += f"    hex (16 18 21 12 4 6 9 0)     ({Nleading} {NT} {NW}) edgeGrading (1 {1/ExpArc:.6f} {1/ExpArc:.6f} 1 {ExpT:.1f} {ExpT:.1f} {ExpT:.1f} {ExpT:.1f} 1 1 1 1)\n"
    txt += f"    hex (18 19 22 21 6 7 10 9)    ({Ntrailing} {NT} {NW}) simpleGrading (1 {ExpT:.1f} 1)\n"
    txt += f"    hex (19 20 23 22 7 8 11 10)   ({ND} {NT} {NW}) simpleGrading ({ExpD:.1f} {ExpT:.1f} 1)\n"
    txt += ");\n\n"
    
    txt += "edges\n(\n"
    txt += "    spline 4 5\n    (\n"
    for pt in pts1:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    txt += "    spline 5 7\n    (\n"
    for pt in pts2:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    txt += "    spline 4 6\n    (\n"
    for pt in pts3:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    txt += "    spline 6 7\n    (\n"
    for pt in pts4:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    
    txt += "    spline 16 17\n    (\n"
    for pt in pts5:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    txt += "    spline 17 19\n    (\n"
    for pt in pts6:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    txt += "    spline 16 18\n    (\n"
    for pt in pts7:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    txt += "    spline 18 19\n    (\n"
    for pt in pts8:
        txt += f"        ({pt[0]:.8f} {pt[1]:.8f} {pt[2]:.8f})\n"
    txt += "    )\n"
    
    txt += f"    arc 0 1 ({pts9[0]:.8f} {pts9[1]:.8f} {pts9[2]:.8f})\n"
    txt += f"    arc 0 9 ({pts10[0]:.8f} {pts10[1]:.8f} {pts10[2]:.8f})\n"
    txt += f"    arc 12 13 ({pts11[0]:.8f} {pts11[1]:.8f} {pts11[2]:.8f})\n"
    txt += f"    arc 12 21 ({pts12[0]:.8f} {pts12[1]:.8f} {pts12[2]:.8f})\n"
    txt += ");\n\n"
    
    txt += """boundary
(
    inlet
    {
        type patch;
        faces
        (
            (1 0 12 13)
            (0 9 21 12)
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (11 8 20 23)
            (8 3 15 20)
        );
    }

    symFront
    {
        type symmetry;
        faces
        (
            (0 1 5 4)
            (1 2 7 5)
            (7 2 3 8)
            (8 11 10 7)
            (10 9 6 7)
            (6 9 0 4)
        );
    }

    symBack
    {
        type symmetry;
        faces
        (
            (17 13 12 16)
            (19 14 13 17)
            (20 15 14 19)
            (23 20 19 22)
            (22 19 18 21)
            (21 18 16 12)
        );
    }

    topAndBottom
    {
        type patch;
        faces
        (
            (3 2 14 15)
            (2 1 13 14)
            (9 10 22 21)
            (10 11 23 22)
        );
    }

    airfoil
    {
        type wall;
        faces
        (
            (4 5 17 16)
            (5 7 19 17)
            (7 6 18 19)
            (6 4 16 18)
        );
    }
);

// ************************************************************************* //
"""
    target = os.path.join(case_dir, "system", "blockMeshDict")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w") as f:
        f.write(txt)
    print(f"Generated {target} for {os.path.basename(dat_file)} at alpha={alpha_deg}°")

if __name__ == "__main__":
    dat = sys.argv[1]
    case = sys.argv[2]
    alpha = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    generate_mesh(dat, case, alpha)
