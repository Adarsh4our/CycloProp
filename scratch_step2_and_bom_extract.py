import os
import sys
import json
import time
import hashlib
import math
import win32com.client
import pythoncom
from PIL import Image

BASE_DIR = r"C:\Users\Adarsh Singh\CycloProp"
BP_DIR = os.path.join(BASE_DIR, "CAD", "Design_Completion", "Bench_Prototype")
D1_DIR = os.path.join(BP_DIR, "Deliverable_D1_Manufacturing")
RENDER_DIR = os.path.join(D1_DIR, "CAD_Renders")
BOM_DIR = os.path.join(D1_DIR, "BOM_and_Mass_Reconciliation")

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

def capture_viewport_png(sw, doc, png_path, std_view_id=None, zoom_box=None, custom_rot=None):
    try:
        doc.SetUserPreferenceToggle(196, False) # swDisplayOrigins
        doc.SetUserPreferenceToggle(195, False) # swDisplayPlanes
        doc.SetUserPreferenceToggle(197, False) # swDisplayAxes
    except Exception:
        pass
    doc.ClearSelection2(True)
    if std_view_id is not None:
        doc.ShowNamedView2("", std_view_id)
    v(doc.ViewZoomtofit2)
    view = doc.ActiveView
    if custom_rot:
        rx, ry, rz = custom_rot
        if rx:
            view.RotateAboutCenter(rx, 0)
        if ry:
            view.RotateAboutCenter(0, ry)
        if rz:
            view.RollBy(rz)
        v(doc.ViewZoomtofit2)
    if zoom_box:
        dx, dy, scale = zoom_box
        try:
            if dx != 0 or dy != 0:
                view.TranslateBy(dx, dy)
            if scale != 1.0:
                view.Scale2 = view.Scale2 * scale
        except Exception as e:
            print("Zoom adjust warning:", e)
    v(doc.GraphicsRedraw2)
    time.sleep(0.3)

    bmp_tmp = png_path.replace(".png", "_tmp.bmp")
    if os.path.exists(bmp_tmp):
        os.remove(bmp_tmp)
    ok = sw.SaveBMP(bmp_tmp, 2400, 1800)
    if not ok or not os.path.exists(bmp_tmp) or os.path.getsize(bmp_tmp) == 0:
        ok = sw.SaveBMP(bmp_tmp, 0, 0)
    if os.path.exists(bmp_tmp) and os.path.getsize(bmp_tmp) > 0:
        img = Image.open(bmp_tmp)
        img.save(png_path, "PNG", optimize=True)
        os.remove(bmp_tmp)
        return True
    return False

def main():
    sw = win32com.client.Dispatch("SldWorks.Application")
    sw.Visible = True
    try:
        sw.FrameState = 1
    except Exception:
        pass

    ba_asm_path = os.path.join(BP_DIR, "BA_Bench_Actuation_Layout.SLDASM")
    errs = get_byref_long(0)
    warns = get_byref_long(0)
    ba_doc = sw.OpenDoc6(ba_asm_path, 2, 1, "", errs, warns)
    sw.ActivateDoc3(v(ba_doc.GetTitle), False, 2, errs)
    ba_doc.ShowConfiguration2("Default")
    v(ba_doc.EditRebuild3)

    # 1. Extract all active leaf components in BA_Bench_Actuation_Layout.SLDASM ("Default" config)
    print("--- Extracting 486 active leaf components & mass properties ---")
    comps = ba_doc.GetComponents(False)
    active_leaves = []
    part_cache = {}

    for c in comps:
        supp = v(c.GetSuppression2)
        if supp == 0:
            continue
        children = v(c.GetChildren)
        if children and len(children) > 0:
            continue
        name = c.Name2
        path = v(c.GetPathName)
        md = v(c.GetModelDoc2)
        if path not in part_cache:
            mass_g = 0.0
            vol_mm3 = 0.0
            dens_kgm3 = 0.0
            mat_name = ""
            body_cnt = 1
            if md:
                try:
                    mat_name = md.GetMaterialPropertyName2("Default", "")
                except Exception:
                    pass
                try:
                    bodies = md.GetBodies2(0, False)
                    if bodies:
                        body_cnt = len(bodies)
                except Exception:
                    pass
                try:
                    mp = v(md.Extension.CreateMassProperty)
                    if mp:
                        mass_g = float(v(mp.Mass)) * 1000.0
                        vol_mm3 = float(v(mp.Volume)) * 1e9
                        dens_kgm3 = float(v(mp.Density))
                except Exception as e:
                    print("MP err:", path, e)
            part_cache[path] = {
                "path": path,
                "basename": os.path.basename(path),
                "material": mat_name,
                "body_count": body_cnt,
                "unit_mass_g": mass_g,
                "unit_volume_mm3": vol_mm3,
                "density_kg_m3": dens_kgm3
            }
        active_leaves.append({
            "instance_name": name,
            "path": path,
            "basename": os.path.basename(path)
        })

    mp_asm = v(ba_doc.Extension.CreateMassProperty)
    total_asm_mass_g = float(v(mp_asm.Mass)) * 1000.0
    print(f"Active leaf components count: {len(active_leaves)}")
    print(f"Unique leaf parts count: {len(part_cache)}")
    print(f"Total assembly mass (SW CreateMassProperty): {total_asm_mass_g:.6f} g")

    sum_leaf_mass_g = sum(part_cache[item["path"]]["unit_mass_g"] for item in active_leaves)
    print(f"Sum of 486 leaf part masses: {sum_leaf_mass_g:.6f} g")

    with open(os.path.join(D1_DIR, "d1_bom_raw_dump.json"), "w") as f:
        json.dump({
            "total_asm_mass_g": total_asm_mass_g,
            "sum_leaf_mass_g": sum_leaf_mass_g,
            "active_leaf_count": len(active_leaves),
            "unique_part_count": len(part_cache),
            "part_cache": part_cache,
            "active_leaves": active_leaves
        }, f, indent=2)

    # 2. Capture the 6 High-Res SolidWorks Viewport Renders
    print("--- Capturing 6 High-Res SolidWorks Viewport Renders ---")
    renders = [
        ("Fig_D1_Bench_Assembly_Isometric.png", 7, None, None),
        ("Fig_D1_Bench_Assembly_Front_Elevation.png", 1, None, None),
        ("Fig_D1_Bench_Assembly_Right_Side.png", 4, None, None),
        ("Fig_D1_Bench_Assembly_Top_Plan.png", 5, None, None),
    ]
    render_manifest = {}
    for fname, vid, zbox, crot in renders:
        out_p = os.path.join(RENDER_DIR, fname)
        ok = capture_viewport_png(sw, ba_doc, out_p, std_view_id=vid, zoom_box=zbox, custom_rot=crot)
        sz = os.path.getsize(out_p) if os.path.exists(out_p) else 0
        h = sha256_file(out_p) if sz > 0 else ""
        with Image.open(out_p) as im:
            w, ht = im.size
        render_manifest[fname] = {
            "path": out_p,
            "width_px": w,
            "height_px": ht,
            "size_bytes": sz,
            "sha256": h
        }
        print(f"Captured {fname}: {w}x{ht} px, {sz} bytes")

    # Close-up 5: Fig_D1_Rotor_Eccentric_Mechanism_CloseUp.png
    bd_asm_path = os.path.join(BP_DIR, "Bench_Rotor", "BD_Bench_Development_Source.SLDASM")
    bd_doc = sw.OpenDoc6(bd_asm_path, 2, 1, "", errs, warns)
    sw.ActivateDoc3(v(bd_doc.GetTitle), False, 2, errs)
    bd_doc.ShowConfiguration2("Default")
    v(bd_doc.EditRebuild3)

    fname5 = "Fig_D1_Rotor_Eccentric_Mechanism_CloseUp.png"
    out_p5 = os.path.join(RENDER_DIR, fname5)
    capture_viewport_png(sw, bd_doc, out_p5, std_view_id=7, zoom_box=(0.0, 0.14, 2.55), custom_rot=(0.18, -0.35, 0.0))
    sz5 = os.path.getsize(out_p5)
    with Image.open(out_p5) as im:
        w5, ht5 = im.size
    render_manifest[fname5] = {
        "path": out_p5,
        "width_px": w5,
        "height_px": ht5,
        "size_bytes": sz5,
        "sha256": sha256_file(out_p5)
    }
    print(f"Captured {fname5}: {w5}x{ht5} px, {sz5} bytes")

    # Close-up 6: Fig_D1_UnderBench_Zaber_Actuation_CloseUp.png
    sw.ActivateDoc3(v(ba_doc.GetTitle), False, 2, errs)
    fname6 = "Fig_D1_UnderBench_Zaber_Actuation_CloseUp.png"
    out_p6 = os.path.join(RENDER_DIR, fname6)
    capture_viewport_png(sw, ba_doc, out_p6, std_view_id=7, zoom_box=(0.02, 0.16, 3.2), custom_rot=(-0.55, 0.45, 0.0))
    sz6 = os.path.getsize(out_p6)
    with Image.open(out_p6) as im:
        w6, ht6 = im.size
    render_manifest[fname6] = {
        "path": out_p6,
        "width_px": w6,
        "height_px": ht6,
        "size_bytes": sz6,
        "sha256": sha256_file(out_p6)
    }
    print(f"Captured {fname6}: {w6}x{ht6} px, {sz6} bytes")

    with open(os.path.join(D1_DIR, "render_manifest_raw.json"), "w") as f:
        json.dump(render_manifest, f, indent=2)

if __name__ == "__main__":
    main()
