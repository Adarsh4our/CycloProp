import json
import math
import hashlib
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Adarsh Singh\CycloProp")
BP_DIR = BASE_DIR / "CAD" / "Design_Completion" / "Bench_Prototype"
D1_DIR = BP_DIR / "Deliverable_D1_Manufacturing"
DXF_DIR = D1_DIR / "Engineering_Drawings" / "DXF_Flat_Patterns"
DXF_DIR.mkdir(parents=True, exist_ok=True)

def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class DXFWriterR12:
    """
    Pure-Python AutoCAD R12 / R2000 compatible ASCII DXF writer for 1:1 CNC/Waterjet flat patterns
    with standard CAD layers: OUTER_PROFILE (White/7), HOLES_THROUGH (Cyan/4),
    COUNTERBORES_POCKETS (Yellow/2), CENTERLINES (Red/1), ANNOTATIONS (Green/3).
    """
    def __init__(self, units_mm=True):
        self.entities = []

    def add_line(self, x1, y1, x2, y2, layer="OUTER_PROFILE", color=7):
        if math.hypot(x2 - x1, y2 - y1) < 1e-5:
            return
        self.entities.append(
            f"  0\nLINE\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{x1:.6f}\n 20\n{y1:.6f}\n 30\n0.0\n"
            f" 11\n{x2:.6f}\n 21\n{y2:.6f}\n 31\n0.0\n"
        )

    def add_circle(self, cx, cy, r, layer="HOLES_THROUGH", color=4):
        self.entities.append(
            f"  0\nCIRCLE\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{cx:.6f}\n 20\n{cy:.6f}\n 30\n0.0\n"
            f" 40\n{r:.6f}\n"
        )

    def add_arc(self, cx, cy, r, start_deg, end_deg, layer="OUTER_PROFILE", color=7):
        self.entities.append(
            f"  0\nARC\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{cx:.6f}\n 20\n{cy:.6f}\n 30\n0.0\n"
            f" 40\n{r:.6f}\n 50\n{start_deg:.6f}\n 51\n{end_deg:.6f}\n"
        )

    def add_crosshair(self, cx, cy, r, layer="CENTERLINES", color=1):
        ext = max(r * 1.25, r + 1.0)
        self.add_line(cx - ext, cy, cx + ext, cy, layer=layer, color=color)
        self.add_line(cx, cy - ext, cx, cy + ext, layer=layer, color=color)

    def add_text(self, x, y, text, height=2.0, layer="ANNOTATIONS", color=3):
        self.entities.append(
            f"  0\nTEXT\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{x:.6f}\n 20\n{y:.6f}\n 30\n0.0\n"
            f" 40\n{height:.4f}\n  1\n{text}\n"
        )

    def save(self, path: Path):
        header = (
            "  0\nSECTION\n  2\nHEADER\n"
            "  9\n$ACADVER\n  1\nAC1009\n"
            "  9\n$INSUNITS\n 70\n4\n"
            "  9\n$MEASUREMENT\n 70\n1\n"
            "  0\nENDSEC\n"
            "  0\nSECTION\n  2\nTABLES\n"
            "  0\nTABLE\n  2\nLAYER\n 70\n5\n"
            "  0\nLAYER\n  2\nOUTER_PROFILE\n 70\n0\n 62\n7\n  6\nCONTINUOUS\n"
            "  0\nLAYER\n  2\nHOLES_THROUGH\n 70\n0\n 62\n4\n  6\nCONTINUOUS\n"
            "  0\nLAYER\n  2\nCOUNTERBORES_POCKETS\n 70\n0\n 62\n2\n  6\nCONTINUOUS\n"
            "  0\nLAYER\n  2\nCENTERLINES\n 70\n0\n 62\n1\n  6\nCENTER\n"
            "  0\nLAYER\n  2\nANNOTATIONS\n 70\n0\n 62\n3\n  6\nCONTINUOUS\n"
            "  0\nENDTAB\n  0\nENDSEC\n"
            "  0\nSECTION\n  2\nENTITIES\n"
        )
        footer = "  0\nENDSEC\n  0\nEOF\n"
        path.write_text(header + "".join(self.entities) + footer, encoding="ascii")

def project_pt(pt3, normal_axis):
    # If plate is in XY plane (normal=Z), 2D coords are (X, Y)
    # If plate is in XZ plane (normal=Y, e.g., BD_RB_4-Inner_Carriage_Plate), 2D coords are (X, Z)
    if normal_axis == "Z":
        return pt3[0], pt3[1]
    elif normal_axis == "Y":
        return pt3[0], pt3[2]
    else:
        return pt3[1], pt3[2]

def export_plate_dxf(geom: dict, dxf_name: str, normal_axis: str, thickness_mm: float, mat_spec: str) -> dict:
    dxf = DXFWriterR12(units_mm=True)
    bbox = geom["bbox_mm"]
    if normal_axis == "Z":
        w_mm = round(bbox[3] - bbox[0], 3)
        h_mm = round(bbox[4] - bbox[1], 3)
        x_min, y_min = bbox[0], bbox[1]
    else:
        w_mm = round(bbox[3] - bbox[0], 3)
        h_mm = round(bbox[5] - bbox[2], 3)
        x_min, y_min = bbox[0], bbox[2]

    # Collect unique 2D lines, arcs, and circles from planar faces aligned with normal_axis
    seen_lines = set()
    seen_circles = set()
    seen_arcs = set()

    for pf in geom["planar_faces"]:
        nx, ny, nz = pf["normal"]
        if (normal_axis == "Z" and abs(nz) < 0.99) or (normal_axis == "Y" and abs(ny) < 0.99):
            continue
        for lp in pf["loops"]:
            is_outer = lp["is_outer"]
            layer = "OUTER_PROFILE" if is_outer else "COUNTERBORES_POCKETS"
            color = 7 if is_outer else 2
            for ed in lp["edges"]:
                etype = ed["type"]
                if etype == "line":
                    x1, y1 = project_pt(ed["start_mm"], normal_axis)
                    x2, y2 = project_pt(ed["end_mm"], normal_axis)
                    key = tuple(sorted([(round(x1, 3), round(y1, 3)), (round(x2, 3), round(y2, 3))]))
                    if key not in seen_lines:
                        seen_lines.add(key)
                        dxf.add_line(x1, y1, x2, y2, layer=layer, color=color)
                elif etype == "circle":
                    cx, cy = project_pt(ed["center_mm"], normal_axis)
                    r = ed["radius_mm"]
                    key = (round(cx, 3), round(cy, 3), round(r, 3))
                    if key not in seen_circles:
                        seen_circles.add(key)
                        dxf.add_circle(cx, cy, r, layer="HOLES_THROUGH", color=4)
                        dxf.add_crosshair(cx, cy, r)
                elif etype == "arc":
                    cx, cy = project_pt(ed["center_mm"], normal_axis)
                    sx, sy = project_pt(ed["start_mm"], normal_axis)
                    ex, ey = project_pt(ed["end_mm"], normal_axis)
                    r = ed["radius_mm"]
                    ang1 = math.degrees(math.atan2(sy - cy, sx - cx)) % 360.0
                    ang2 = math.degrees(math.atan2(ey - cy, ex - cx)) % 360.0
                    # Check arc orientation via axis
                    ax_val = ed["axis"][2] if normal_axis == "Z" else ed["axis"][1]
                    if ax_val < 0:
                        ang1, ang2 = ang2, ang1
                    key = (round(cx, 3), round(cy, 3), round(r, 3), round(ang1, 1), round(ang2, 1))
                    if key not in seen_arcs:
                        seen_arcs.add(key)
                        dxf.add_arc(cx, cy, r, ang1, ang2, layer=layer, color=color)

    # Also ensure all cylindrical holes along normal_axis are included on HOLES_THROUGH / COUNTERBORES_POCKETS
    hole_list = []
    for cyl in geom["cylinders"]:
        ax = cyl["axis"]
        if (normal_axis == "Z" and abs(ax[2]) > 0.99) or (normal_axis == "Y" and abs(ax[1]) > 0.99):
            cx, cy = project_pt(cyl["origin_mm"], normal_axis)
            r = cyl["radius_mm"]
            d = cyl["diameter_mm"]
            cbox = cyl["box_mm"]
            depth = round((cbox[5] - cbox[2]) if normal_axis == "Z" else (cbox[4] - cbox[1]), 3)
            key = (round(cx, 3), round(cy, 3), round(r, 3))
            is_thru = abs(depth - thickness_mm) < 0.25
            if key not in seen_circles:
                seen_circles.add(key)
                lyr = "HOLES_THROUGH" if is_thru else "COUNTERBORES_POCKETS"
                clr = 4 if is_thru else 2
                dxf.add_circle(cx, cy, r, layer=lyr, color=clr)
                dxf.add_crosshair(cx, cy, r)
            hole_list.append({
                "x_mm": round(cx, 3),
                "y_mm": round(cy, 3),
                "diameter_mm": round(d, 3),
                "depth_mm": depth,
                "is_through": is_thru,
            })

    # Deduplicate hole_list by (x_mm, y_mm, diameter_mm)
    unique_holes = {}
    for h in hole_list:
        uk = (h["x_mm"], h["y_mm"], h["diameter_mm"])
        if uk not in unique_holes or h["depth_mm"] > unique_holes[uk]["depth_mm"]:
            unique_holes[uk] = h
    sorted_holes = sorted(unique_holes.values(), key=lambda item: (item["diameter_mm"], item["x_mm"], item["y_mm"]))

    # Add a clean 1:1 title annotation below the lower-left edge
    txt_h = max(1.8, min(8.0, w_mm * 0.025))
    dxf.add_text(x_min, y_min - txt_h * 2.2, f"PART: {dxf_name.replace('.dxf','')} | SCALE 1:1 (UNITS: MM) | ENVELOPE: {w_mm} x {h_mm} x {thickness_mm} MM", height=txt_h)
    dxf.add_text(x_min, y_min - txt_h * 3.8, f"MATERIAL: {mat_spec} | CAD MASS: {geom['mass_g']:.2f} g | UNIQUE HOLES/BORES: {len(sorted_holes)}", height=txt_h * 0.85)

    out_path = DXF_DIR / dxf_name
    dxf.save(out_path)
    return {
        "dxf_filename": dxf_name,
        "dxf_path": str(out_path),
        "size_bytes": out_path.stat().st_size,
        "sha256": sha256_file(out_path),
        "envelope_mm": [w_mm, h_mm, thickness_mm],
        "material": mat_spec,
        "cad_mass_g": geom["mass_g"],
        "entity_count": len(dxf.entities),
        "unique_hole_count": len(sorted_holes),
        "holes": sorted_holes,
    }

def main():
    geom_dump = json.loads((D1_DIR / "d1_cad_geometry_dump.json").read_text())
    plates = [
        ("Bench_Rotor/BD_RB_Intermediate_X_Slider.SLDPRT", "BD_RB_Intermediate_X_Slider.dxf", "Z", 3.0, "6061-T6 Aluminum Plate (t = 3.00 mm)"),
        ("Bench_Rotor/BD_RB_4-Inner_Carriage_Plate.SLDPRT", "BD_RB_4-Inner_Carriage_Plate.dxf", "Y", 10.0, "7075-T6 Aluminum Machined Plate (t = 10.00 mm)"),
        ("Bench_Rotor/BD_RB_XY_Fixed_Base.SLDPRT", "BD_RB_XY_Fixed_Base.dxf", "Z", 3.0, "6061-T6 Aluminum Plate (t = 3.00 mm)"),
        ("Hardware_Models/BD_Motor_Adapter_Plate.SLDPRT", "BD_Motor_Adapter_Plate.dxf", "Z", 8.0, "6061-T6 Aluminum Plate (t = 8.00 mm)"),
        ("Actuation_Models/BA_Bench_Plate_650_12.SLDPRT", "BA_Bench_Plate_650_12.dxf", "Z", 12.0, "6061-T6 Aluminum Tooling Plate (650 x 650 x 12.00 mm)"),
    ]
    dxf_manifest = {}
    for rel_p, dxf_name, n_axis, thk, mspec in plates:
        info = export_plate_dxf(geom_dump[rel_p], dxf_name, n_axis, thk, mspec)
        dxf_manifest[dxf_name] = info
        print(f"Exported 1:1 DXF {dxf_name}: {info['size_bytes']} B, {info['entity_count']} entities, {info['unique_hole_count']} holes, sha256={info['sha256'][:12]}...")

    (D1_DIR / "dxf_manifest_raw.json").write_text(json.dumps(dxf_manifest, indent=2))

if __name__ == "__main__":
    main()
