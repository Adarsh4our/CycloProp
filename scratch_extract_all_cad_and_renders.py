import os
import sys
import json
import time
import hashlib
import math
from pathlib import Path
from collections import Counter, defaultdict
import win32com.client
import pythoncom
from PIL import Image

BASE_DIR = Path(r"C:\Users\Adarsh Singh\CycloProp")
sys.path.insert(0, str(BASE_DIR / "CAD" / "Design_Completion" / "automation"))
import cad
from cad import c, app, NULL, iref

BP_DIR = BASE_DIR / "CAD" / "Design_Completion" / "Bench_Prototype"
REVB_DIR = BASE_DIR / "CAD" / "Design_Completion" / "RevB_Isolated"
D1_DIR = BP_DIR / "Deliverable_D1_Manufacturing"

STEP_DIR = D1_DIR / "STEP_AP214"
RENDER_DIR = D1_DIR / "CAD_Renders"
PART_RENDER_DIR = D1_DIR / "part_renders"
DWG_DIR = D1_DIR / "Engineering_Drawings"
DXF_DIR = DWG_DIR / "DXF_Flat_Patterns"
BOM_DIR = D1_DIR / "BOM_and_Mass_Reconciliation"

for d in [D1_DIR, STEP_DIR, RENDER_DIR, PART_RENDER_DIR, DWG_DIR, DXF_DIR, BOM_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def extract_part_geometry_with_cad(doc, rel_path: str) -> dict:
    db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    mat = c(doc, "GetMaterialPropertyName2", "Default", db) or ""
    mp = c(doc.Extension, "CreateMassProperty2")
    override_mass = bool(c(mp, "GetOverrideOptions").OverrideMass)
    mass_g = float(mp.Mass) * 1000.0
    vol_mm3 = float(mp.Volume) * 1e9
    com = list(mp.CenterOfMass) if mp.CenterOfMass else [0.0, 0.0, 0.0]
    com_mm = [round(v * 1000.0, 4) for v in com]

    bodies = list(c(doc, "GetBodies2", 0, False) or [])
    bbox_mm = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9]
    cylinders = []
    planes = []
    toruses = []
    planar_faces = []

    for b in bodies:
        bx = list(c(b, "GetBodyBox"))
        for i in range(3):
            bbox_mm[i] = min(bbox_mm[i], bx[i] * 1000.0)
            bbox_mm[i + 3] = max(bbox_mm[i + 3], bx[i + 3] * 1000.0)
        for f in (c(b, "GetFaces") or []):
            s = c(f, "GetSurface")
            if not s:
                continue
            fbox = [round(v * 1000.0, 4) for v in list(c(f, "GetBox"))]
            area_mm2 = round(float(c(f, "GetArea")) * 1e6, 3)
            if c(s, "IsCylinder"):
                cp = list(s.CylinderParams)
                ox, oy, oz, ax, ay, az, r = cp
                cylinders.append({
                    "origin_mm": [round(ox * 1000.0, 4), round(oy * 1000.0, 4), round(oz * 1000.0, 4)],
                    "axis": [round(ax, 4), round(ay, 4), round(az, 4)],
                    "radius_mm": round(r * 1000.0, 4),
                    "diameter_mm": round(r * 2000.0, 4),
                    "box_mm": fbox,
                    "area_mm2": area_mm2,
                })
            elif c(s, "IsTorus"):
                tp = list(s.TorusParams)
                toruses.append({
                    "center_mm": [round(tp[0] * 1000.0, 4), round(tp[1] * 1000.0, 4), round(tp[2] * 1000.0, 4)],
                    "axis": [round(tp[3], 4), round(tp[4], 4), round(tp[5], 4)],
                    "major_r_mm": round(tp[6] * 1000.0, 4),
                    "minor_r_mm": round(tp[7] * 1000.0, 4),
                    "box_mm": fbox,
                })
            elif c(s, "IsPlane"):
                pp = list(s.PlaneParams)
                nx, ny, nz, rx, ry, rz = pp
                planes.append({
                    "normal": [round(nx, 4), round(ny, 4), round(nz, 4)],
                    "root_mm": [round(rx * 1000.0, 4), round(ry * 1000.0, 4), round(rz * 1000.0, 4)],
                    "box_mm": fbox,
                    "area_mm2": area_mm2,
                })
                if abs(nz) > 0.99 or abs(ny) > 0.99 or abs(nx) > 0.99:
                    loops_out = []
                    for lp in (c(f, "GetLoops") or []):
                        is_outer = bool(c(lp, "IsOuter"))
                        edges_out = []
                        for ed in (c(lp, "GetEdges") or []):
                            crv = c(ed, "GetCurve")
                            ep = list(c(ed, "GetCurveParams2"))
                            sx, sy, sz = ep[0] * 1000.0, ep[1] * 1000.0, ep[2] * 1000.0
                            ex, ey, ez = ep[3] * 1000.0, ep[4] * 1000.0, ep[5] * 1000.0
                            if c(crv, "IsCircle"):
                                cir = list(crv.CircleParams)
                                cx, cy, cz, cax, cay, caz, cr = cir
                                dist_se = math.hypot(ex - sx, ey - sy) + abs(ez - sz)
                                is_full = dist_se < 1e-4
                                edges_out.append({
                                    "type": "circle" if is_full else "arc",
                                    "center_mm": [round(cx * 1000.0, 4), round(cy * 1000.0, 4), round(cz * 1000.0, 4)],
                                    "axis": [round(cax, 4), round(cay, 4), round(caz, 4)],
                                    "radius_mm": round(cr * 1000.0, 4),
                                    "start_mm": [round(sx, 4), round(sy, 4), round(sz, 4)],
                                    "end_mm": [round(ex, 4), round(ey, 4), round(ez, 4)],
                                })
                            elif c(crv, "IsLine"):
                                edges_out.append({
                                    "type": "line",
                                    "start_mm": [round(sx, 4), round(sy, 4), round(sz, 4)],
                                    "end_mm": [round(ex, 4), round(ey, 4), round(ez, 4)],
                                })
                            else:
                                edges_out.append({
                                    "type": "spline",
                                    "start_mm": [round(sx, 4), round(sy, 4), round(sz, 4)],
                                    "end_mm": [round(ex, 4), round(ey, 4), round(ez, 4)],
                                })
                        loops_out.append({
                            "is_outer": is_outer,
                            "edges": edges_out,
                        })
                    planar_faces.append({
                        "normal": [round(nx, 4), round(ny, 4), round(nz, 4)],
                        "root_mm": [round(rx * 1000.0, 4), round(ry * 1000.0, 4), round(rz * 1000.0, 4)],
                        "box_mm": fbox,
                        "area_mm2": area_mm2,
                        "loops": loops_out,
                    })

    return {
        "rel_path": rel_path,
        "material": mat,
        "material_db": db.value,
        "override_mass": override_mass,
        "body_count": len(bodies),
        "mass_g": round(mass_g, 6),
        "volume_mm3": round(vol_mm3, 4),
        "density_kg_m3": round(mass_g / vol_mm3 * 1e6, 2) if vol_mm3 > 0 else 0.0,
        "com_mm": com_mm,
        "bbox_mm": [round(x, 4) for x in bbox_mm],
        "cylinders": cylinders,
        "planes": planes,
        "toruses": toruses,
        "planar_faces": planar_faces,
    }

def capture_view_png(doc, out_png: Path, view_name="*Isometric", view_id=7, rot_xy=None, pan_xy=None, scale_mult=1.0, width=2400, height=1800):
    cad.activate(doc)
    try:
        c(doc, "SetUserPreferenceToggle", 196, False)  # origins
        c(doc, "SetUserPreferenceToggle", 195, False)  # planes
        c(doc, "SetUserPreferenceToggle", 197, False)  # axes
    except Exception:
        pass
    c(doc, "ClearSelection2", True)
    c(doc, "ShowNamedView2", view_name, view_id)
    c(doc, "ViewZoomtofit2")
    vw = doc.ActiveView
    if rot_xy:
        rx, ry = rot_xy
        if rx != 0:
            c(vw, "RotateAboutCenter", float(rx), 0.0)
        if ry != 0:
            c(vw, "RotateAboutCenter", 0.0, float(ry))
        c(doc, "ViewZoomtofit2")
    if pan_xy:
        px, py = pan_xy
        c(vw, "TranslateBy", float(px), float(py))
    if scale_mult != 1.0:
        vw.Scale2 = float(vw.Scale2) * float(scale_mult)
    c(doc, "GraphicsRedraw2")
    time.sleep(0.25)

    bmp_tmp = out_png.with_suffix(".bmp")
    if bmp_tmp.exists():
        bmp_tmp.unlink()
    ok = c(doc, "SaveBMP", str(bmp_tmp), int(width), int(height))
    if not ok or not bmp_tmp.exists() or bmp_tmp.stat().st_size == 0:
        c(doc, "SaveBMP", str(bmp_tmp), 0, 0)
    with Image.open(bmp_tmp) as im:
        im.save(out_png, "PNG", optimize=True)
        w, h = im.size
    bmp_tmp.unlink()
    return w, h, out_png.stat().st_size, sha256_file(out_png)

def main():
    app.Visible = True
    try:
        app.FrameState = 1  # Maximize
    except Exception:
        pass

    # 1. Query 3D geometry + capture isometric part snapshots for the 15 critical parts + 4 extra parts + RevB 260mm shaft
    parts_to_query = [
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
        ("Hardware_Models/BD_Motor_Adapter_Plate.SLDPRT", None),
        ("Actuation_Models/BA_Bench_Plate_650_12.SLDPRT", None),
        ("Bench_Rotor/BD_RB_Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE.SLDPRT", None),
        ("Bench_Rotor/BD_RB_Socket_Eye_D7_Sphere5p05_PROTOTYPE.SLDPRT", None),
    ]

    geom_dump = {}
    print("=== Step 1A: Querying 3D geometry & capturing isometric thumbnails of critical parts ===", flush=True)
    for rel_p, step_name in parts_to_query:
        p_path = BP_DIR / rel_p
        doc = cad.getdoc(p_path, 1, readonly=True)
        title = c(doc, "GetTitle")
        geom = extract_part_geometry_with_cad(doc, rel_p)
        geom_dump[rel_p] = geom
        # Also capture a clean isometric render of this part for our engineering drawing sheets!
        part_stem = p_path.stem
        thumb_path = PART_RENDER_DIR / f"{part_stem}_iso.png"
        if not thumb_path.exists():
            capture_view_png(doc, thumb_path, "*Isometric", 7, width=1200, height=900)
        print(f"  [Part] {rel_p}: mass={geom['mass_g']:.3f} g, cyls={len(geom['cylinders'])}, bbox={geom['bbox_mm']}", flush=True)
        c(app, "CloseDoc", title)

    # Also query RevB 260mm shaft
    revb_shaft = REVB_DIR / "RB_3-Drive_Shaft.SLDPRT"
    if revb_shaft.exists():
        doc = cad.getdoc(revb_shaft, 1, readonly=True)
        title = c(doc, "GetTitle")
        geom = extract_part_geometry_with_cad(doc, "RevB_Isolated/RB_3-Drive_Shaft.SLDPRT")
        geom_dump["RevB_Isolated/RB_3-Drive_Shaft.SLDPRT"] = geom
        print(f"  [RevB 260mm Shaft] mass={geom['mass_g']:.4f} g, vol={geom['volume_mm3']:.2f} mm3, bbox={geom['bbox_mm']}", flush=True)
        c(app, "CloseDoc", title)

    (D1_DIR / "d1_cad_geometry_dump.json").write_text(json.dumps(geom_dump, indent=2))

    # 2. Open BA_Bench_Actuation_Layout.SLDASM and BD_Bench_Development_Source.SLDASM, activate "Default" configuration
    print("=== Step 1B & Step 4: Activating 'Default' configuration (486 active leaf parts) ===", flush=True)
    top_asm_path = BP_DIR / "BA_Bench_Actuation_Layout.SLDASM"
    sub_asm_path = BP_DIR / "Bench_Rotor" / "BD_Bench_Development_Source.SLDASM"

    asm = cad.getdoc(top_asm_path, 2)
    cad.activate(asm)
    top_comps = c(asm, "GetComponents", True)
    sub_comp = next(co for co in top_comps if "BD_Bench_Development_Source" in co.Name2)
    sub_doc = c(sub_comp, "GetModelDoc2")

    # Switch both sub_doc and asm to "Default" configuration and ensure sub_comp references "Default"
    c(sub_doc, "ShowConfiguration2", "Default")
    c(asm, "ShowConfiguration2", "Default")
    if sub_comp.ReferencedConfiguration != "Default":
        sub_comp.ReferencedConfiguration = "Default"
        sub_comp.Solving = 1
        c(asm, "CompConfigProperties5", 2, 0, True, True, "Default", False, False)

    # Ensure rotor angle setup mate is active in Default config so home pose is exact
    f_ang = c(sub_doc, "FeatureByName", "RevB_SETUP_Rotor_Angle")
    if f_ang is not None:
        c(f_ang, "SetSuppression2", 1, 2, None)

    c(sub_doc, "EditRebuild3")
    c(asm, "EditRebuild3")

    # Verify active leaf count in "Default" configuration
    all_comps = c(asm, "GetComponents", False)
    counts = Counter()
    comp_instances = defaultdict(list)
    part_docs = {}
    active_leaf_count = 0

    for co in all_comps:
        if c(co, "GetSuppression") == 0:
            continue
        pdoc = c(co, "GetModelDoc2")
        if pdoc is None:
            continue
        if c(pdoc, "GetType") != 1:  # 1 = swDocPART
            continue
        active_leaf_count += 1
        path_str = c(co, "GetPathName")
        cfg_name = co.ReferencedConfiguration
        key = (path_str, cfg_name)
        counts[key] += 1
        comp_instances[key].append(co.Name2)
        part_docs[key] = pdoc

    print(f"  [Default Config] Verified active leaf components = {active_leaf_count}, unique parts = {len(counts)}", flush=True)

    # Re-export BD_Bench_Development_Source.STEP and BA_Bench_Actuation_Layout.STEP in verified Default config (486 parts)
    try:
        c(app, "SetUserPreferenceIntegerValue", 22, 214)
    except Exception:
        pass
    bd_step_path = STEP_DIR / "BD_Bench_Development_Source.STEP"
    ba_step_path = STEP_DIR / "BA_Bench_Actuation_Layout.STEP"
    if bd_step_path.exists():
        bd_step_path.unlink()
    if ba_step_path.exists():
        ba_step_path.unlink()

    c(sub_doc.Extension, "SaveAs", str(bd_step_path), 0, 3, NULL, iref(), iref())
    c(asm.Extension, "SaveAs", str(ba_step_path), 0, 3, NULL, iref(), iref())
    print(f"  [STEP Export] BD_Bench_Development_Source.STEP: {bd_step_path.stat().st_size} bytes", flush=True)
    print(f"  [STEP Export] BA_Bench_Actuation_Layout.STEP: {ba_step_path.stat().st_size} bytes", flush=True)

    # Build complete step_manifest
    step_manifest = {}
    for p_step in sorted(STEP_DIR.glob("*.STEP")):
        step_manifest[p_step.name] = {
            "step_path": str(p_step),
            "size_bytes": p_step.stat().st_size,
            "sha256": sha256_file(p_step),
        }
    (D1_DIR / "step_manifest_raw.json").write_text(json.dumps(step_manifest, indent=2))

    # Extract full 73-unique-part / 486-instance BOM
    bom_rows = []
    for (path_str, cfg_name), qty in sorted(counts.items(), key=lambda x: Path(x[0][0]).name):
        pdoc = part_docs[(path_str, cfg_name)]
        prev_cfg = pdoc.ConfigurationManager.ActiveConfiguration.Name
        if prev_cfg != cfg_name:
            c(pdoc, "ShowConfiguration2", cfg_name)
        db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
        mat = c(pdoc, "GetMaterialPropertyName2", cfg_name, db) or ""
        mp = c(pdoc.Extension, "CreateMassProperty2")
        override = bool(c(mp, "GetOverrideOptions").OverrideMass)
        vol_mm3 = float(mp.Volume) * 1e9
        mass_each_g = float(mp.Mass) * 1000.0
        dens = mass_each_g / vol_mm3 * 1e6 if vol_mm3 > 0 else 0.0
        bodies = list(c(pdoc, "GetBodies2", 0, False) or [])
        if prev_cfg != cfg_name:
            c(pdoc, "ShowConfiguration2", prev_cfg)

        bom_rows.append({
            "part_filename": Path(path_str).name,
            "full_path": path_str,
            "configuration": cfg_name,
            "quantity": qty,
            "material": mat if mat else ("Multi-Body Override (7075-T6 + CFRP + Rohacell)" if override else "Assigned Solid Material"),
            "material_db": db.value,
            "body_count": len(bodies),
            "mass_override": override,
            "unit_volume_mm3": round(vol_mm3, 4),
            "effective_density_kg_m3": round(dens, 2),
            "unit_mass_g": round(mass_each_g, 6),
            "total_mass_g": round(qty * mass_each_g, 6),
            "instances": comp_instances[(path_str, cfg_name)],
        })

    mp_top = c(asm.Extension, "CreateMassProperty2")
    mp_sub = c(sub_doc.Extension, "CreateMassProperty2")
    top_mass_g = float(mp_top.Mass) * 1000.0
    sub_mass_g = float(mp_sub.Mass) * 1000.0
    sum_bom_g = sum(r["total_mass_g"] for r in bom_rows)
    print(f"  [BOM] 73 unique parts ({len(bom_rows)}), 486 instances ({sum(r['quantity'] for r in bom_rows)}), sum_bom={sum_bom_g:.4f} g, top_asm={top_mass_g:.4f} g, sub_asm={sub_mass_g:.4f} g", flush=True)

    (D1_DIR / "d1_bom_raw_dump.json").write_text(json.dumps({
        "unique_part_count": len(bom_rows),
        "active_leaf_instance_count": sum(r["quantity"] for r in bom_rows),
        "top_assembly_mass_g": top_mass_g,
        "rotor_subassembly_mass_g": sub_mass_g,
        "sum_leaf_masses_g": sum_bom_g,
        "rows": bom_rows,
    }, indent=2))

    # 3. Capture the 6 High-Res SolidWorks Viewport Renders (CAD_Renders/)
    print("=== Step 2: Capturing 6 High-Res SolidWorks Viewport Renders ===", flush=True)
    render_manifest = {}
    render_specs = [
        ("Fig_D1_Bench_Assembly_Isometric.png", asm, "*Isometric", 7, None, None, 1.0),
        ("Fig_D1_Bench_Assembly_Front_Elevation.png", asm, "*Front", 1, None, None, 1.0),
        ("Fig_D1_Bench_Assembly_Right_Side.png", asm, "*Right", 4, None, None, 1.0),
        ("Fig_D1_Bench_Assembly_Top_Plan.png", asm, "*Top", 5, None, None, 1.0),
    ]
    for fname, doc_ref, vname, vid, rxy, pxy, sc in render_specs:
        out_p = RENDER_DIR / fname
        w, h, sz, sha = capture_view_png(doc_ref, out_p, vname, vid, rxy, pxy, sc)
        render_manifest[fname] = {
            "path": str(out_p),
            "width_px": w,
            "height_px": h,
            "size_bytes": sz,
            "sha256": sha,
        }
        print(f"  [Render] {fname}: {w}x{h} px, {sz} bytes", flush=True)

    # Render 5: Fig_D1_Rotor_Eccentric_Mechanism_CloseUp.png (using sub_doc opened in its own window temporarily or zoomed in asm)
    sub_open = cad.getdoc(sub_asm_path, 2)
    cad.activate(sub_open)
    c(sub_open, "ShowConfiguration2", "Default")
    c(sub_open, "EditRebuild3")
    # Also capture full rotor ortho/iso renders for Sheet 02!
    capture_view_png(sub_open, PART_RENDER_DIR / "BD_Rotor_Iso.png", "*Isometric", 7, width=1600, height=1200)
    capture_view_png(sub_open, PART_RENDER_DIR / "BD_Rotor_Front.png", "*Front", 1, width=1600, height=1200)
    capture_view_png(sub_open, PART_RENDER_DIR / "BD_Rotor_Top.png", "*Top", 5, width=1600, height=1200)

    fname5 = "Fig_D1_Rotor_Eccentric_Mechanism_CloseUp.png"
    out_p5 = RENDER_DIR / fname5
    w5, h5, sz5, sha5 = capture_view_png(sub_open, out_p5, "*Isometric", 7, rot_xy=(0.15, -0.35), pan_xy=(0.0, 0.13), scale_mult=2.4)
    render_manifest[fname5] = {
        "path": str(out_p5),
        "width_px": w5,
        "height_px": h5,
        "size_bytes": sz5,
        "sha256": sha5,
    }
    print(f"  [Render] {fname5}: {w5}x{h5} px, {sz5} bytes", flush=True)

    # Render 6: Fig_D1_UnderBench_Zaber_Actuation_CloseUp.png
    cad.activate(asm)
    fname6 = "Fig_D1_UnderBench_Zaber_Actuation_CloseUp.png"
    out_p6 = RENDER_DIR / fname6
    w6, h6, sz6, sha6 = capture_view_png(asm, out_p6, "*Isometric", 7, rot_xy=(-0.48, 0.42), pan_xy=(0.01, 0.15), scale_mult=2.8)
    render_manifest[fname6] = {
        "path": str(out_p6),
        "width_px": w6,
        "height_px": h6,
        "size_bytes": sz6,
        "sha256": sha6,
    }
    print(f"  [Render] {fname6}: {w6}x{h6} px, {sz6} bytes", flush=True)

    (D1_DIR / "render_manifest_raw.json").write_text(json.dumps(render_manifest, indent=2))

    # 4. Switch BA_Bench_Actuation_Layout.SLDASM back to "Motion_Fast_Playback" (clean, 0 mate errors) per Guardrail #3
    print("=== Guardrail #3: Switching BA_Bench_Actuation_Layout.SLDASM back to 'Motion_Fast_Playback' ===", flush=True)
    c(sub_doc, "ShowConfiguration2", "Motion_Fast_Playback")
    c(asm, "ShowConfiguration2", "Motion_Fast_Playback")
    sub_comp.ReferencedConfiguration = "Motion_Fast_Playback"
    sub_comp.Solving = 1
    c(asm, "CompConfigProperties5", 2, 0, True, True, "Motion_Fast_Playback", False, False)
    f_ang = c(sub_doc, "FeatureByName", "RevB_SETUP_Rotor_Angle")
    if f_ang is not None:
        c(f_ang, "SetSuppression2", 0, 2, None)
    c(sub_doc, "EditRebuild3")
    c(asm, "EditRebuild3")
    c(asm, "ShowNamedView2", "*Isometric", 7)
    c(asm, "ViewZoomtofit2")
    print("  [Guardrail #3] Restored 'Motion_Fast_Playback' configuration cleanly.", flush=True)

if __name__ == "__main__":
    main()
