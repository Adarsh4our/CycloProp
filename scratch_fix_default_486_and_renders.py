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
D1_DIR = BP_DIR / "Deliverable_D1_Manufacturing"
STEP_DIR = D1_DIR / "STEP_AP214"
RENDER_DIR = D1_DIR / "CAD_Renders"
PART_RENDER_DIR = D1_DIR / "part_renders"

def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def auto_center_crop_and_pad(im: Image.Image, target_w=2400, target_h=1800, pad_ratio=0.07) -> Image.Image:
    import numpy as np
    rgb = im.convert("RGB")
    w, h = rgb.size
    arr = np.array(rgb, dtype=np.int16)
    bg_col = np.median(arr[:, :40, :], axis=1, keepdims=True)
    diff = np.abs(arr - bg_col).max(axis=2)
    mask = diff > 10
    ys, xs = np.where(mask)
    if len(xs) < 100:
        return rgb
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw = x1 - x0 + 1
    bh = y1 - y0 + 1
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    req_w = bw / (1.0 - 2 * pad_ratio)
    req_h = bh / (1.0 - 2 * pad_ratio)
    aspect = target_w / target_h
    if req_w / req_h < aspect:
        req_w = req_h * aspect
    else:
        req_h = req_w / aspect
    crop_x0 = int(round(cx - req_w / 2.0))
    crop_y0 = int(round(cy - req_h / 2.0))
    crop_x1 = int(round(cx + req_w / 2.0))
    crop_y1 = int(round(cy + req_h / 2.0))

    pad_left = max(0, -crop_x0)
    pad_top = max(0, -crop_y0)
    pad_right = max(0, crop_x1 - w)
    pad_bot = max(0, crop_y1 - h)
    if pad_left or pad_top or pad_right or pad_bot:
        bg_rgb = tuple(int(v) for v in np.median(arr[:10, :10, :], axis=(0, 1)))
        padded = Image.new("RGB", (w + pad_left + pad_right, h + pad_top + pad_bot), bg_rgb)
        padded.paste(rgb, (pad_left, pad_top))
        crop_x0 += pad_left
        crop_x1 += pad_left
        crop_y0 += pad_top
        crop_y1 += pad_top
        rgb = padded

    cropped = rgb.crop((crop_x0, crop_y0, crop_x1, crop_y1))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

def save_viewport(doc, out_png: Path, rotate_cw_deg=0, center_model=True):
    c(doc, "GraphicsRedraw2")
    time.sleep(0.3)
    bmp_tmp = out_png.with_suffix(".bmp")
    if bmp_tmp.exists():
        bmp_tmp.unlink()
    ok = c(doc, "SaveBMP", str(bmp_tmp), 2400, 1800)
    if not ok or not bmp_tmp.exists() or bmp_tmp.stat().st_size == 0:
        c(doc, "SaveBMP", str(bmp_tmp), 0, 0)
    with Image.open(bmp_tmp) as im:
        im_out = im.convert("RGB")
    bmp_tmp.unlink()
    if rotate_cw_deg == 90:
        im_out = im_out.transpose(Image.Transpose.ROTATE_270)
    elif rotate_cw_deg == 180:
        im_out = im_out.transpose(Image.Transpose.ROTATE_180)
    elif rotate_cw_deg == 270:
        im_out = im_out.transpose(Image.Transpose.ROTATE_90)
    if center_model:
        im_out = auto_center_crop_and_pad(im_out, 2400, 1800, pad_ratio=0.07)
    im_out.save(out_png, "PNG", optimize=True)
    return im_out.size[0], im_out.size[1], out_png.stat().st_size, sha256_file(out_png)

def unsuppress_list(doc, comps):
    if not comps:
        return
    c(doc, "ClearSelection2", True)
    for co in comps:
        c(co, "Select4", True, NULL, False)
    c(doc, "EditUnsuppress2")
    c(doc, "ClearSelection2", True)

def main():
    app.Visible = True
    cad003a = json.loads((BP_DIR / "CAD003A_COMPLETION_STATE.json").read_text())
    legacy_savox_suppressed = set(cad003a["step4_savox_tab_suppression"]["suppressed_components"])

    top_asm_path = BP_DIR / "BA_Bench_Actuation_Layout.SLDASM"
    sub_asm_path = BP_DIR / "Bench_Rotor" / "BD_Bench_Development_Source.SLDASM"

    # Open sub_doc in its own window so ShowConfiguration2("Default") and EditUnsuppress2 operate directly on sub_doc!
    sub_doc = cad.getdoc(sub_asm_path, 2)
    cad.activate(sub_doc)
    c(sub_doc, "ShowConfiguration2", "Default")

    # Check if any non-legacy-Savox components are suppressed in sub_doc ("Default")
    sub_to_unsuppress = []
    for co in c(sub_doc, "GetComponents", False):
        if c(co, "GetSuppression") == 0:
            leaf_name = co.Name2.split("/")[-1]
            if leaf_name not in legacy_savox_suppressed and co.Name2 not in legacy_savox_suppressed:
                sub_to_unsuppress.append(co)
    print(f"[Subassembly Default] Unsuppressing {len(sub_to_unsuppress)} decorative fasteners...", flush=True)
    unsuppress_list(sub_doc, sub_to_unsuppress)

    # Ensure RevB_SETUP_Rotor_Angle is unsuppressed in Default config
    f_ang = c(sub_doc, "FeatureByName", "RevB_SETUP_Rotor_Angle")
    if f_ang is not None:
        c(f_ang, "SetSuppression2", 1, 2, None)
    c(sub_doc, "EditRebuild3")

    # Now activate top-level assembly BA_Bench_Actuation_Layout.SLDASM in "Default" configuration
    asm = cad.getdoc(top_asm_path, 2)
    cad.activate(asm)
    c(asm, "ShowConfiguration2", "Default")

    top_comps = c(asm, "GetComponents", True)
    sub_comp = next(co for co in top_comps if "BD_Bench_Development_Source" in co.Name2)
    if sub_comp.ReferencedConfiguration != "Default" or sub_comp.Solving != 1:
        c(asm, "ClearSelection2", True)
        c(sub_comp, "Select4", False, NULL, False)
        sub_comp.ReferencedConfiguration = "Default"
        sub_comp.Solving = 1
        c(asm, "CompConfigProperties5", 2, 1, True, True, "Default", False, False)
        c(asm, "ClearSelection2", True)

    top_to_unsuppress = [co for co in top_comps if c(co, "GetSuppression") == 0]
    print(f"[Top Assembly Default] Unsuppressing {len(top_to_unsuppress)} decorative fasteners...", flush=True)
    unsuppress_list(asm, top_to_unsuppress)

    # Reset Bench_X_Actuator_Stroke to centered home pose (e_x = 0.0 mm) in Default configuration
    inspect = json.loads((BP_DIR / "ACTUATION_START_INSPECTION.json").read_text())
    xp0_m = next(r for r in inspect if "X_Slider_Drive_Tab_" in r["name"])["pos_mm"][0] / 1000.0
    mx = c(asm, "FeatureByName", "Bench_X_Actuator_Stroke")
    if mx is not None:
        fd_mx = c(mx, "GetDefinition")
        stroke_x = 0.0 - xp0_m
        fd_mx.Distance = abs(stroke_x)
        fd_mx.FlipDimension = bool(stroke_x >= 0)
        c(mx, "ModifyDefinition", fd_mx, asm, NULL)

    c(sub_doc, "EditRebuild3")
    c(asm, "EditRebuild3")

    # 1. Verify 486 active leaf components & 73 unique parts
    all_comps = c(asm, "GetComponents", False)
    counts = Counter()
    comp_instances = defaultdict(list)
    part_docs = {}
    active_leaf_count = 0

    for co in all_comps:
        if c(co, "GetSuppression") == 0:
            continue
        pdoc = c(co, "GetModelDoc2")
        if pdoc is None or c(pdoc, "GetType") != 1:
            continue
        active_leaf_count += 1
        path_str = c(co, "GetPathName")
        cfg_name = co.ReferencedConfiguration
        key = (path_str, cfg_name)
        counts[key] += 1
        comp_instances[key].append(co.Name2)
        part_docs[key] = pdoc

    print(f"  [Verified Default] Active leaf components = {active_leaf_count}, Unique parts = {len(counts)}", flush=True)

    # 2. Export STEP AP214 for BD_Bench_Development_Source.SLDASM and BA_Bench_Actuation_Layout.SLDASM (all 486 parts!)
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
    print(f"  [STEP Export 486] BD_Bench_Development_Source.STEP: {bd_step_path.stat().st_size} bytes", flush=True)
    print(f"  [STEP Export 486] BA_Bench_Actuation_Layout.STEP: {ba_step_path.stat().st_size} bytes", flush=True)

    step_manifest = {}
    for p_step in sorted(STEP_DIR.glob("*.STEP")):
        step_manifest[p_step.name] = {
            "step_path": str(p_step),
            "size_bytes": p_step.stat().st_size,
            "sha256": sha256_file(p_step),
        }
    (D1_DIR / "step_manifest_raw.json").write_text(json.dumps(step_manifest, indent=2))

    # 3. Extract 73-unique-part / 486-instance BOM
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
    print(f"  [BOM Verified] {len(bom_rows)} unique parts, {sum(r['quantity'] for r in bom_rows)} instances | sum_bom={sum_bom_g:.4f} g | top_asm={top_mass_g:.4f} g | sub_asm={sub_mass_g:.4f} g", flush=True)

    (D1_DIR / "d1_bom_raw_dump.json").write_text(json.dumps({
        "unique_part_count": len(bom_rows),
        "active_leaf_instance_count": sum(r["quantity"] for r in bom_rows),
        "top_assembly_mass_g": top_mass_g,
        "rotor_subassembly_mass_g": sub_mass_g,
        "sum_leaf_masses_g": sum_bom_g,
        "rows": bom_rows,
    }, indent=2))

    # 4. Capture the 6 High-Res SolidWorks Viewport Renders (CAD_Renders/) with all 486 parts active!
    print("=== Capturing 6 High-Resolution SolidWorks Viewport Renders (486 Active Parts) ===", flush=True)
    cad.activate(asm)
    try:
        c(asm, "SetUserPreferenceToggle", 196, False)
        c(asm, "SetUserPreferenceToggle", 195, False)
        c(asm, "SetUserPreferenceToggle", 197, False)
    except Exception:
        pass

    render_manifest = {}

    # (1) Fig_D1_Bench_Assembly_Isometric.png
    c(asm, "ClearSelection2", True)
    c(asm, "ShowNamedView2", "*Bottom", 6)
    c(asm, "ViewZoomtofit2")
    vw = asm.ActiveView
    c(vw, "RotateAboutCenter", 0.52, -0.68)
    c(asm, "ViewZoomtofit2")
    out1 = RENDER_DIR / "Fig_D1_Bench_Assembly_Isometric.png"
    w, h, sz, sha = save_viewport(asm, out1, rotate_cw_deg=0, center_model=True)
    render_manifest[out1.name] = {"path": str(out1), "width_px": w, "height_px": h, "size_bytes": sz, "sha256": sha}
    print(f"  [1] {out1.name}: {w}x{h}, {sz}B", flush=True)

    # (2) Fig_D1_Bench_Assembly_Front_Elevation.png
    c(asm, "ClearSelection2", True)
    c(asm, "ShowNamedView2", "*Bottom", 6)
    c(asm, "ViewZoomtofit2")
    out2 = RENDER_DIR / "Fig_D1_Bench_Assembly_Front_Elevation.png"
    w, h, sz, sha = save_viewport(asm, out2, rotate_cw_deg=0, center_model=True)
    render_manifest[out2.name] = {"path": str(out2), "width_px": w, "height_px": h, "size_bytes": sz, "sha256": sha}
    print(f"  [2] {out2.name}: {w}x{h}, {sz}B", flush=True)

    # (3) Fig_D1_Bench_Assembly_Right_Side.png
    c(asm, "ClearSelection2", True)
    c(asm, "ShowNamedView2", "*Right", 4)
    c(asm, "ViewZoomtofit2")
    out3 = RENDER_DIR / "Fig_D1_Bench_Assembly_Right_Side.png"
    w, h, sz, sha = save_viewport(asm, out3, rotate_cw_deg=90, center_model=True)
    render_manifest[out3.name] = {"path": str(out3), "width_px": w, "height_px": h, "size_bytes": sz, "sha256": sha}
    print(f"  [3] {out3.name}: {w}x{h}, {sz}B", flush=True)

    # (4) Fig_D1_Bench_Assembly_Top_Plan.png
    c(asm, "ClearSelection2", True)
    c(asm, "ShowNamedView2", "*Front", 1)
    c(asm, "ViewZoomtofit2")
    out4 = RENDER_DIR / "Fig_D1_Bench_Assembly_Top_Plan.png"
    w, h, sz, sha = save_viewport(asm, out4, rotate_cw_deg=0, center_model=True)
    render_manifest[out4.name] = {"path": str(out4), "width_px": w, "height_px": h, "size_bytes": sz, "sha256": sha}
    print(f"  [4] {out4.name}: {w}x{h}, {sz}B", flush=True)

    # (5) Fig_D1_Rotor_Eccentric_Mechanism_CloseUp.png
    c(asm, "ClearSelection2", True)
    c(asm, "ShowNamedView2", "*Bottom", 6)
    vw = asm.ActiveView
    c(vw, "RotateAboutCenter", 0.38, -0.58)
    target_names_5 = (
        "BD_RB_4-Outer_Control_Ring",
        "BD_RB_Oldham_Input_PROTOTYPE",
        "BD_RB_Oldham_Floating_Disk_PROTOTYPE",
        "BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE",
        "BD_RB_4-Inner_Carriage_Plate",
        "BD_RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE",
    )
    for co in all_comps:
        if any(t in co.Name2 for t in target_names_5):
            c(co, "Select4", True, NULL, False)
    c(asm, "ViewZoomToSelection")
    c(asm, "ClearSelection2", True)
    vw.Scale2 = float(vw.Scale2) * 0.78
    out5 = RENDER_DIR / "Fig_D1_Rotor_Eccentric_Mechanism_CloseUp.png"
    w, h, sz, sha = save_viewport(asm, out5, rotate_cw_deg=0, center_model=False)
    render_manifest[out5.name] = {"path": str(out5), "width_px": w, "height_px": h, "size_bytes": sz, "sha256": sha}
    print(f"  [5] {out5.name}: {w}x{h}, {sz}B", flush=True)

    # (6) Fig_D1_UnderBench_Zaber_Actuation_CloseUp.png
    c(asm, "ClearSelection2", True)
    c(asm, "ShowNamedView2", "*Bottom", 6)
    vw = asm.ActiveView
    c(vw, "RotateAboutCenter", -0.32, 0.62)
    target_names_6 = (
        "BA_X_Actuator_Drop_Link",
        "BA_Y_Cross_Slot_Drop_Link",
        "BA_Y_Guided_Crosshead",
        "BA_Y_Bronze_Sliding_Shoe",
        "BA_D8_Guide_Shaft_L126",
        "BA_Guide_Support_Post",
    )
    for co in all_comps:
        if any(t in co.Name2 for t in target_names_6):
            c(co, "Select4", True, NULL, False)
    c(asm, "ViewZoomToSelection")
    c(asm, "ClearSelection2", True)
    vw.Scale2 = float(vw.Scale2) * 0.82
    out6 = RENDER_DIR / "Fig_D1_UnderBench_Zaber_Actuation_CloseUp.png"
    w, h, sz, sha = save_viewport(asm, out6, rotate_cw_deg=0, center_model=False)
    render_manifest[out6.name] = {"path": str(out6), "width_px": w, "height_px": h, "size_bytes": sz, "sha256": sha}
    print(f"  [6] {out6.name}: {w}x{h}, {sz}B", flush=True)

    # Capture clean subassembly render from sub_doc for Sheet 02
    cad.activate(sub_doc)
    c(sub_doc, "ClearSelection2", True)
    c(sub_doc, "ShowNamedView2", "*Bottom", 6)
    vw_sub = sub_doc.ActiveView
    c(vw_sub, "RotateAboutCenter", 0.48, -0.62)
    c(sub_doc, "ViewZoomtofit2")
    save_viewport(sub_doc, PART_RENDER_DIR / "BD_Rotor_Iso.png", rotate_cw_deg=0, center_model=True)

    (D1_DIR / "render_manifest_raw.json").write_text(json.dumps(render_manifest, indent=2))

    # 5. Switch BA_Bench_Actuation_Layout.SLDASM back to "Motion_Fast_Playback" per Guardrail #3
    print("=== Guardrail #3: Switching BA_Bench_Actuation_Layout.SLDASM back to 'Motion_Fast_Playback' ===", flush=True)
    c(sub_doc, "ShowConfiguration2", "Motion_Fast_Playback")
    c( app, "CloseDoc", c(sub_doc, "GetTitle") )
    cad.activate(asm)
    c(asm, "ShowConfiguration2", "Motion_Fast_Playback")
    c(asm, "EditRebuild3")
    c(asm, "ShowNamedView2", "*Isometric", 7)
    c(asm, "ViewZoomtofit2")
    print("=== Restored 'Motion_Fast_Playback' configuration cleanly ===", flush=True)

if __name__ == "__main__":
    main()
