#!/usr/bin/env python3
"""
CycloProp — OpenFOAM 2D Mesh Visualizer
=======================================
Reads constant/polyMesh and generates high-resolution visual plots
of the C-grid mesh and boundary layer refinement around the airfoil.
"""

import os
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def plot_mesh(case_dir, out_png=None):
    if out_png is None:
        out_png = os.path.join(case_dir, "mesh_visualization.png")
        
    poly_dir = os.path.join(case_dir, "constant", "polyMesh")
    points_file = os.path.join(poly_dir, "points")
    faces_file = os.path.join(poly_dir, "faces")
    boundary_file = os.path.join(poly_dir, "boundary")
    
    if not os.path.exists(points_file):
        print(f"Error: {points_file} not found")
        return
        
    # Read points
    with open(points_file) as f:
        text = f.read()
    pts_raw = re.findall(r'\(([-+0-9.eE\s]+)\)', text[text.find('\n(')+2 : text.rfind(')\n;')])
    pts = np.array([[float(x) for x in p.split()] for p in pts_raw])
    
    # Read faces
    with open(faces_file) as f:
        text = f.read()
    faces_raw = re.findall(r'\(([-+0-9.eE\s]+)\)', text[text.find('\n(')+2 : text.rfind(')\n;')])
    faces = [[int(x) for x in p.split()] for p in faces_raw]
    
    # Read boundary to find symFront
    with open(boundary_file) as f:
        b_text = f.read()
        
    m_sym = re.search(r'symFront\s*\{[^}]*nFaces\s+(\d+);\s*startFace\s+(\d+);', b_text)
    if not m_sym:
        # Fallback to frontAndBack
        m_sym = re.search(r'frontAndBack\s*\{[^}]*nFaces\s+(\d+);\s*startFace\s+(\d+);', b_text)
        
    if m_sym:
        n_faces = int(m_sym.group(1))
        start_face = int(m_sym.group(2))
        front_faces = faces[start_face : start_face + n_faces]
    else:
        # Take all 4-node faces on min y
        y_min = pts[:, 1].min()
        front_faces = [f for f in faces if len(f) == 4 and np.allclose(pts[f, 1], y_min)]
        
    # Extract line segments in (x, z)
    segments = []
    for f in front_faces:
        p0 = pts[f[0], [0, 2]]
        p1 = pts[f[1], [0, 2]]
        p2 = pts[f[2], [0, 2]]
        p3 = pts[f[3], [0, 2]]
        segments.extend([[p0, p1], [p1, p2], [p2, p3], [p3, p0]])
        
    # Create 3-panel figure
    fig = plt.figure(figsize=(16, 10), facecolor='white')
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2], hspace=0.25, wspace=0.2)
    
    ax_full  = fig.add_subplot(gs[0, :])
    ax_foil  = fig.add_subplot(gs[1, 0])
    ax_nose  = fig.add_subplot(gs[1, 1])
    
    # 1. Full Domain
    lc_full = LineCollection(segments, colors='#4a7c59', linewidths=0.3, alpha=0.6)
    ax_full.add_collection(lc_full)
    ax_full.set_xlim(-0.35, 0.65)
    ax_full.set_ylim(-0.35, 0.35)
    ax_full.set_aspect('equal')
    ax_full.set_title("Overview: Full C-Grid Domain (Inlet Arc, Far-Field & Wake)", fontsize=13, fontweight='bold', pad=10)
    ax_full.set_xlabel("x (m) [Flow Direction →]", fontsize=10)
    ax_full.set_ylabel("z (m) [Lift Direction ↑]", fontsize=10)
    ax_full.grid(True, linestyle=':', alpha=0.4)
    
    # 2. Zoomed Airfoil
    lc_foil = LineCollection(segments, colors='#1b4965', linewidths=0.4, alpha=0.7)
    ax_foil.add_collection(lc_foil)
    ax_foil.set_xlim(-0.02, 0.04)
    ax_foil.set_ylim(-0.015, 0.015)
    ax_foil.set_aspect('equal')
    # Determine blade title
    folder_name = os.path.basename(os.path.dirname(os.path.abspath(case_dir)))
    if not folder_name or folder_name.startswith("alpha"):
        folder_name = os.path.basename(os.path.abspath(case_dir))
    blade_title = folder_name.replace("_", " ").upper()

    ax_foil.set_title(f"{blade_title} Blade: Boundary Layer Grid Clustering", fontsize=13, fontweight='bold', pad=10)
    ax_foil.set_xlabel("x (m)", fontsize=10)
    ax_foil.set_ylabel("z (m)", fontsize=10)
    ax_foil.grid(True, linestyle=':', alpha=0.4)
    
    # 3. Leading Edge Close-up
    lc_nose = LineCollection(segments, colors='#003049', linewidths=0.5, alpha=0.85)
    ax_nose.add_collection(lc_nose)
    ax_nose.set_xlim(-0.012, -0.004)
    ax_nose.set_ylim(-0.004, 0.004)
    ax_nose.set_aspect('equal')
    ax_nose.set_title("Leading Edge Detail: High-Resolution Wall Normal Cells", fontsize=13, fontweight='bold', pad=10)
    ax_nose.set_xlabel("x (m)", fontsize=10)
    ax_nose.set_ylabel("z (m)", fontsize=10)
    ax_nose.grid(True, linestyle=':', alpha=0.4)
    
    plt.suptitle(f"CycloProp {blade_title} — Structured C-Grid (Re=95k, c=38mm)", fontsize=15, fontweight='bold', y=0.98)
    
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Mesh visualization saved: {out_png}")

if __name__ == "__main__":
    c_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    o_png = sys.argv[2] if len(sys.argv) > 2 else None
    plot_mesh(c_dir, o_png)
