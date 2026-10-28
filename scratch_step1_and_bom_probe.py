import os
import sys
import json
import time
import hashlib
import math
import win32com.client
import pythoncom

BASE_DIR = r"C:\Users\Adarsh Singh\CycloProp"
BP_DIR = os.path.join(BASE_DIR, "CAD", "Design_Completion", "Bench_Prototype")
REVB_DIR = os.path.join(BASE_DIR, "CAD", "Design_Completion", "RevB_Isolated")
D1_DIR = os.path.join(BP_DIR, "Deliverable_D1_Manufacturing")

STEP_DIR = os.path.join(D1_DIR, "STEP_AP214")
RENDER_DIR = os.path.join(D1_DIR, "CAD_Renders")
DWG_DIR = os.path.join(D1_DIR, "Engineering_Drawings")
DXF_DIR = os.path.join(DWG_DIR, "DXF_Flat_Patterns")
BOM_DIR = os.path.join(D1_DIR, "BOM_and_Mass_Reconciliation")

for d in [D1_DIR, STEP_DIR, RENDER_DIR, DWG_DIR, DXF_DIR, BOM_DIR]:
    os.makedirs(d, exist_ok=True)

def v(x):
    return x() if callable(x) else x

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def get_byref_long(val=0):
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, val)

def open_doc(sw, path, doc_type=1, read_only=True):
    errs = get_byref_long(0)
    warns = get_byref_long(0)
    opts = 1 | (2 if read_only else 0)
    doc = sw.OpenDoc6(path, doc_type, opts, "", errs, warns)
    return doc

def save_as_step(sw, doc, step_path):
    if os.path.exists(step_path) and os.path.getsize(step_path) > 0:
        return True
    try:
        sw.SetUserPreferenceIntegerValue(22, 214)
    except Exception as e:
        print("Warning setting swStepAP:", e)
    try:
        res = doc.SaveAs3(step_path, 0, 3)
    except Exception:
        res = doc.SaveAs(step_path)
    if not os.path.exists(step_path) or os.path.getsize(step_path) == 0:
        errs = get_byref_long(0)
        warns = get_byref_long(0)
        null_disp = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
        doc.Extension.SaveAs3(step_path, 0, 3, null_disp, errs, warns)
    return os.path.exists(step_path) and os.path.getsize(step_path) > 0

def extract_part_geometry(doc, rel_path):
    info = {
        "rel_path": rel_path,
        "title": v(doc.GetTitle),
        "material": "",
        "body_count": 0,
        "mass_g": 0.0,
        "volume_mm3": 0.0,
        "density_kg_m3": 0.0,
        "com_mm": [0.0, 0.0, 0.0],
        "bbox_mm": [],
        "cylinders": [],
        "planes": [],
        "toruses": [],
        "z_planar_loops": []
    }
    try:
        info["material"] = doc.GetMaterialPropertyName2("Default", "")
    except Exception:
        pass
    try:
        ext = doc.Extension
        mp = v(ext.CreateMassProperty)
        if mp:
            info["mass_g"] = float(v(mp.Mass)) * 1000.0
            info["volume_mm3"] = float(v(mp.Volume)) * 1e9
            info["density_kg_m3"] = float(v(mp.Density))
            com = v(mp.CenterOfMass)
            if com:
                info["com_mm"] = [round(c * 1000.0, 4) for c in com]
    except Exception as e:
        print("MassProp error on", rel_path, e)

    try:
        bodies = doc.GetBodies2(0, False)
        if bodies:
            info["body_count"] = len(bodies)
            xmin, ymin, zmin = 1e9, 1e9, 1e9
            xmax, ymax, zmax = -1e9, -1e9, -1e9
            for b in bodies:
                bx = v(b.GetBodyBox)
                if bx:
                    xmin = min(xmin, bx[0]*1000.0)
                    ymin = min(ymin, bx[1]*1000.0)
                    zmin = min(zmin, bx[2]*1000.0)
                    xmax = max(xmax, bx[3]*1000.0)
                    ymax = max(ymax, bx[4]*1000.0)
                    zmax = max(zmax, bx[5]*1000.0)
                faces = v(b.GetFaces)
                if not faces:
                    continue
                for f in faces:
                    surf = v(f.GetSurface)
                    if not surf:
                        continue
                    fbox = v(f.GetBox)
                    fbox_mm = [round(val*1000.0, 4) for val in fbox] if fbox else []
                    if v(surf.IsCylinder):
                        cp = v(surf.CylinderParams)
                        if cp:
                            ox, oy, oz, ax, ay, az, r = cp
                            info["cylinders"].append({
                                "origin_mm": [round(ox*1000.0, 4), round(oy*1000.0, 4), round(oz*1000.0, 4)],
                                "axis": [round(ax, 4), round(ay, 4), round(az, 4)],
                                "radius_mm": round(r*1000.0, 4),
                                "diameter_mm": round(r*2000.0, 4),
                                "box_mm": fbox_mm
                            })
                    elif v(surf.IsPlane):
                        pp = v(surf.PlaneParams)
                        if pp:
                            nx, ny, nz, rx, ry, rz = pp
                            info["planes"].append({
                                "normal": [round(nx, 4), round(ny, 4), round(nz, 4)],
                                "root_mm": [round(rx*1000.0, 4), round(ry*1000.0, 4), round(rz*1000.0, 4)],
                                "box_mm": fbox_mm
                            })
                            if abs(nz) > 0.99 or abs(ny) > 0.99 or abs(nx) > 0.99:
                                loops_data = []
                                loops = v(f.GetLoops)
                                if loops:
                                    for lp in loops:
                                        is_outer = bool(v(lp.IsOuter))
                                        edges_data = []
                                        edges = v(lp.GetEdges)
                                        if edges:
                                            for ed in edges:
                                                crv = v(ed.GetCurve)
                                                ep = v(ed.GetCurveParams2)
                                                if not crv or not ep:
                                                    continue
                                                sx, sy, sz = ep[0]*1000.0, ep[1]*1000.0, ep[2]*1000.0
                                                ex, ey, ez = ep[3]*1000.0, ep[4]*1000.0, ep[5]*1000.0
                                                if v(crv.IsCircle):
                                                    cir = v(crv.CircleParams)
                                                    cx, cy, cz, cax, cay, caz, cr = cir
                                                    dist_se = math.hypot(ex-sx, ey-sy) + abs(ez-sz)
                                                    is_full = dist_se < 1e-4
                                                    edges_data.append({
                                                        "type": "circle" if is_full else "arc",
                                                        "center_mm": [round(cx*1000.0, 4), round(cy*1000.0, 4), round(cz*1000.0, 4)],
                                                        "axis": [round(cax, 4), round(cay, 4), round(caz, 4)],
                                                        "radius_mm": round(cr*1000.0, 4),
                                                        "start_mm": [round(sx, 4), round(sy, 4), round(sz, 4)],
                                                        "end_mm": [round(ex, 4), round(ey, 4), round(ez, 4)]
                                                    })
                                                elif v(crv.IsLine):
                                                    edges_data.append({
                                                        "type": "line",
                                                        "start_mm": [round(sx, 4), round(sy, 4), round(sz, 4)],
                                                        "end_mm": [round(ex, 4), round(ey, 4), round(ez, 4)]
                                                    })
                                                else:
                                                    edges_data.append({
                                                        "type": "spline",
                                                        "start_mm": [round(sx, 4), round(sy, 4), round(sz, 4)],
                                                        "end_mm": [round(ex, 4), round(ey, 4), round(ez, 4)]
                                                    })
                                        loops_data.append({
                                            "is_outer": is_outer,
                                            "edges": edges_data
                                        })
                                info["z_planar_loops"].append({
                                    "normal": [round(nx, 4), round(ny, 4), round(nz, 4)],
                                    "root_mm": [round(rx*1000.0, 4), round(ry*1000.0, 4), round(rz*1000.0, 4)],
                                    "box_mm": fbox_mm,
                                    "loops": loops_data
                                })
                    elif v(surf.IsTorus):
                        tp = v(surf.TorusParams)
                        if tp:
                            info["toruses"].append({
                                "center_mm": [round(tp[0]*1000.0, 4), round(tp[1]*1000.0, 4), round(tp[2]*1000.0, 4)],
                                "axis": [round(tp[3], 4), round(tp[4], 4), round(tp[5], 4)],
                                "major_r_mm": round(tp[6]*1000.0, 4),
                                "minor_r_mm": round(tp[7]*1000.0, 4),
                                "box_mm": fbox_mm
                            })
            info["bbox_mm"] = [round(xmin, 4), round(ymin, 4), round(zmin, 4), round(xmax, 4), round(ymax, 4), round(zmax, 4)]
    except Exception as e:
        print("Geometry error on", rel_path, e)
    return info

def main():
    sw = win32com.client.Dispatch("SldWorks.Application")
    sw.Visible = True
    sw.UserControl = True

    step_parts = [
        ("Bench_Rotor/BD_RB_Part1.SLDPRT", "BD_RB_Part1.STEP"),
        ("Bench_Rotor/BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT", "BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.STEP"),
        ("Bench_Rotor/BD_RB_3-Drive_Shaft.SLDPRT", "BD_RB_3-Drive_Shaft.STEP"),
        ("Bench_Rotor/BD_RB_4-Outer_Control_Ring.SLDPRT", "BD_RB_4-Outer_Control_Ring.STEP"),
        ("Bench_Rotor/BD_RB_4-Inner_Carriage_Plate.SLDPRT", "BD_RB_4-Inner_Carriage_Plate.STEP"),
        ("Bench_Rotor/BD_RB_Intermediate_X_Slider.SLDPRT", "BD_RB_Intermediate_X_Slider.STEP"),
        ("Bench_Rotor/BD_RB_XY_Fixed_Base.SLDPRT", "BD_RB_XY_Fixed_Base.STEP"),
        ("Bench_Rotor/BD_RB_Oldham_Input_PROTOTYPE.SLDPRT", "BD_RB_Oldham_Input_PROTOTYPE.STEP"),
        ("Bench_Rotor/BD_RB_Oldham_Floating_Disk_PROTOTYPE.SLDPRT", "BD_RB_Oldham_Floating_Disk_PROTOTYPE.STEP"),
        ("Bench_Rotor/BD_RB_Oldham_Output_PROTOTYPE.SLDPRT", "BD_RB_Oldham_Output_PROTOTYPE.STEP"),
        ("Bench_Rotor/BD_RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE.SLDPRT", "BD_RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE.STEP"),
        ("Actuation_Models/BA_X_Actuator_Drop_Link.SLDPRT", "BA_X_Actuator_Drop_Link.STEP"),
        ("Actuation_Models/BA_Y_Cross_Slot_Drop_Link.SLDPRT", "BA_Y_Cross_Slot_Drop_Link.STEP"),
        ("Actuation_Models/BA_Y_Guided_Crosshead.SLDPRT", "BA_Y_Guided_Crosshead.STEP"),
        ("Actuation_Models/BA_Y_Bronze_Sliding_Shoe.SLDPRT", "BA_Y_Bronze_Sliding_Shoe.STEP"),
    ]

    extra_query_parts = [
        "Hardware_Models/BD_Motor_Adapter_Plate.SLDPRT",
        "Actuation_Models/BA_Bench_Plate_650_12.SLDPRT",
        "Bench_Rotor/BD_RB_Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE.SLDPRT",
        "Bench_Rotor/BD_RB_Socket_Eye_D7_Sphere5p05_PROTOTYPE.SLDPRT",
    ]

    step_manifest = {}
    geom_dump = {}

    print("--- Verifying/Exporting 15 Critical Part STEP files & querying 3D geometry ---")
    for rel_path, step_name in step_parts:
        full_path = os.path.join(BP_DIR, rel_path.replace("/", "\\"))
        doc = open_doc(sw, full_path, 1, read_only=True)
        if not doc:
            print("ERROR opening", full_path)
            continue
        title = v(doc.GetTitle)
        step_out = os.path.join(STEP_DIR, step_name)
        ok = save_as_step(sw, doc, step_out)
        sz = os.path.getsize(step_out) if os.path.exists(step_out) else 0
        h = sha256_file(step_out) if sz > 0 else ""
        step_manifest[step_name] = {
            "source_file": rel_path,
            "step_path": step_out,
            "size_bytes": sz,
            "sha256": h,
            "category": "Critical Custom Part"
        }
        geom_dump[rel_path] = extract_part_geometry(doc, rel_path)
        print(f"Part {step_name}: {sz}B, mass={geom_dump[rel_path]['mass_g']:.3f}g, cyls={len(geom_dump[rel_path]['cylinders'])}, bbox={geom_dump[rel_path]['bbox_mm']}")
        sw.CloseDoc(title)

    for rel_path in extra_query_parts:
        full_path = os.path.join(BP_DIR, rel_path.replace("/", "\\"))
        doc = open_doc(sw, full_path, 1, read_only=True)
        if not doc:
            print("ERROR opening extra part", full_path)
            continue
        title = v(doc.GetTitle)
        geom_dump[rel_path] = extract_part_geometry(doc, rel_path)
        print(f"Extra {rel_path}: mass={geom_dump[rel_path]['mass_g']:.3f}g, cyls={len(geom_dump[rel_path]['cylinders'])}, bbox={geom_dump[rel_path]['bbox_mm']}")
        sw.CloseDoc(title)

    revb_shaft_path = os.path.join(REVB_DIR, "RB_3-Drive_Shaft.SLDPRT")
    if os.path.exists(revb_shaft_path):
        doc = open_doc(sw, revb_shaft_path, 1, read_only=True)
        if doc:
            title = v(doc.GetTitle)
            geom_dump["RevB_Isolated/RB_3-Drive_Shaft.SLDPRT"] = extract_part_geometry(doc, "RevB_Isolated/RB_3-Drive_Shaft.SLDPRT")
            print("Queried RevB 260mm shaft:", geom_dump["RevB_Isolated/RB_3-Drive_Shaft.SLDPRT"]["mass_g"], "g, vol=", geom_dump["RevB_Isolated/RB_3-Drive_Shaft.SLDPRT"]["volume_mm3"], "mm3")
            sw.CloseDoc(title)

    # Top-Level Assembly 3: RevB_Bench_Development_Source.STEP
    revb_asm_path = os.path.join(REVB_DIR, "RB_Assem20_Design_RevB.SLDASM")
    step_name = "RevB_Bench_Development_Source.STEP"
    step_out = os.path.join(STEP_DIR, step_name)
    if not os.path.exists(step_out) or os.path.getsize(step_out) == 0:
        doc = open_doc(sw, revb_asm_path, 2, read_only=True)
        if doc:
            title = v(doc.GetTitle)
            save_as_step(sw, doc, step_out)
            sw.CloseDoc(title)
    sz = os.path.getsize(step_out) if os.path.exists(step_out) else 0
    h = sha256_file(step_out) if sz > 0 else ""
    step_manifest[step_name] = {
        "source_file": "CAD/Design_Completion/RevB_Isolated/RB_Assem20_Design_RevB.SLDASM",
        "step_path": step_out,
        "size_bytes": sz,
        "sha256": h,
        "category": "Top-Level Assembly (Isolated Flight-Scale Rotor)"
    }
    print(f"Verified {step_name}: {sz} bytes, sha256={h[:12]}...")

    # Open BD_Bench_Development_Source.SLDASM and BA_Bench_Actuation_Layout.SLDASM
    bd_asm_path = os.path.join(BP_DIR, "Bench_Rotor", "BD_Bench_Development_Source.SLDASM")
    ba_asm_path = os.path.join(BP_DIR, "BA_Bench_Actuation_Layout.SLDASM")

    print("--- Opening BD_Bench_Development_Source.SLDASM ---")
    bd_doc = open_doc(sw, bd_asm_path, 2, read_only=False)
    bd_doc.ShowConfiguration2("Default")
    v(bd_doc.EditRebuild3)
    step_name = "BD_Bench_Development_Source.STEP"
    step_out = os.path.join(STEP_DIR, step_name)
    save_as_step(sw, bd_doc, step_out)
    sz = os.path.getsize(step_out) if os.path.exists(step_out) else 0
    h = sha256_file(step_out) if sz > 0 else ""
    step_manifest[step_name] = {
        "source_file": "CAD/Design_Completion/Bench_Prototype/Bench_Rotor/BD_Bench_Development_Source.SLDASM",
        "step_path": step_out,
        "size_bytes": sz,
        "sha256": h,
        "category": "Top-Level Assembly (Bench Rotor + 400W Main Drive Subassembly)"
    }
    print(f"Exported {step_name}: {sz} bytes, sha256={h[:12]}...")

    print("--- Opening BA_Bench_Actuation_Layout.SLDASM ---")
    ba_doc = open_doc(sw, ba_asm_path, 2, read_only=False)
    errs = get_byref_long(0)
    sw.ActivateDoc3(v(ba_doc.GetTitle), False, 2, errs)
    ba_doc.ShowConfiguration2("Default")
    v(ba_doc.EditRebuild3)

    step_name = "BA_Bench_Actuation_Layout.STEP"
    step_out = os.path.join(STEP_DIR, step_name)
    save_as_step(sw, ba_doc, step_out)
    sz = os.path.getsize(step_out) if os.path.exists(step_out) else 0
    h = sha256_file(step_out) if sz > 0 else ""
    step_manifest[step_name] = {
        "source_file": "CAD/Design_Completion/Bench_Prototype/BA_Bench_Actuation_Layout.SLDASM",
        "step_path": step_out,
        "size_bytes": sz,
        "sha256": h,
        "category": "Top-Level Assembly (Full Bench Prototype Rig - Default Config, 486 Leaf Parts)"
    }
    print(f"Exported {step_name}: {sz} bytes, sha256={h[:12]}...")

    with open(os.path.join(D1_DIR, "step_manifest_raw.json"), "w") as f:
        json.dump(step_manifest, f, indent=2)
    with open(os.path.join(D1_DIR, "d1_cad_geometry_dump.json"), "w") as f:
        json.dump(geom_dump, f, indent=2)

    print("Step 1 & Geometry Dump Complete!")

if __name__ == "__main__":
    main()
