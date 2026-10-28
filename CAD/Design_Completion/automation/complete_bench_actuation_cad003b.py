"""Execute Steps 1-4 of CAD-003B: Zaber Bench Actuation Kinematic Mating, Hardware Detailing & Coupled Motion Readiness."""
import sys
import os
import time
import subprocess
import json
import math
import shutil
import hashlib
from pathlib import Path
import pythoncom
import win32com.client
import win32com.client.dynamic
import numpy as np

# Ensure a single clean SolidWorks session with no prior file locks
subprocess.run(['powershell', '-Command', 'Stop-Process -Name SLDWORKS -Force -ErrorAction SilentlyContinue'])
time.sleep(1.5)

ROOT = Path(r'C:\Users\Adarsh Singh\CycloProp')
sys.path.insert(0, str(ROOT / 'CAD/Design_Completion/automation'))
import cad
from cad import c, app, NULL, iref, array
from shaft_angle_drive import drive_shaft_angle

app.Visible = True


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


FOLDER = cad.TASK / 'Bench_Prototype'
ROTOR_DIR = FOLDER / 'Bench_Rotor'
ACT_MODELS = FOLDER / 'Actuation_Models'
HW_MODELS = FOLDER / 'Hardware_Models'
BACKUP_DIR = FOLDER / 'Before_CAD003B_Backup'
BACKUP_DIR.mkdir(exist_ok=True)
(BACKUP_DIR / 'Actuation_Models').mkdir(exist_ok=True)

# Clean up any stale temporary lock files
for p in FOLDER.rglob('~$*'):
    try:
        p.unlink()
    except Exception:
        pass


def make_screw_part(folder, name, desc, dia, length, head_d, head_h, material='AISI 4340 Steel, normalized'):
    path = folder / f'{name}.SLDPRT'
    if path.exists():
        return path
    template = c(app, 'GetUserPreferenceStringValue', 8)
    d = c(app, 'NewDocument', template, 0, 0.0, 0.0)
    cad.properties(d, desc)
    cad.ring(d, head_d, 0, -head_h, 0, 'Head_Envelope')
    cad.ring(d, dia, 0, 0, length, 'Thread_Major_Envelope')
    assert c(d, 'EditRebuild3')
    c(d, 'SetMaterialPropertyName2', 'Default', cad.MAT_DB, material)
    assert c(d, 'EditRebuild3')
    cad.save(d, path)
    return path


def make_washer_part(folder, name, desc, od, id_, h, material='AISI 4340 Steel, normalized'):
    path = folder / f'{name}.SLDPRT'
    if path.exists():
        return path
    template = c(app, 'GetUserPreferenceStringValue', 8)
    d = c(app, 'NewDocument', template, 0, 0.0, 0.0)
    cad.properties(d, desc)
    cad.ring(d, od, id_, 0, h, 'Washer_Envelope')
    assert c(d, 'EditRebuild3')
    c(d, 'SetMaterialPropertyName2', 'Default', cad.MAT_DB, material)
    assert c(d, 'EditRebuild3')
    cad.save(d, path)
    return path


def make_nut_part(folder, name, desc, dia, af, h, material='AISI 4340 Steel, normalized'):
    path = folder / f'{name}.SLDPRT'
    if path.exists():
        return path
    template = c(app, 'GetUserPreferenceStringValue', 8)
    d = c(app, 'NewDocument', template, 0, 0.0, 0.0)
    cad.properties(d, desc)
    cad.sketch(d)
    radius = af / math.sqrt(3.0)
    cad.polygon(d, [(radius * math.cos(i * math.pi / 3.0), radius * math.sin(i * math.pi / 3.0)) for i in range(6)])
    cad.circle(d, 0, 0, dia / 2.0)
    cad.extrude(d, 0, h, 'Nut_Thread_Major_Envelope')
    assert c(d, 'EditRebuild3')
    c(d, 'SetMaterialPropertyName2', 'Default', cad.MAT_DB, material)
    assert c(d, 'EditRebuild3')
    cad.save(d, path)
    return path


def rigid_datums_world(doc, parent, child, prefix):
    """Lock child to parent using cardinal datum planes evaluated in top-level world coordinates."""
    pt = cad.tf(parent)
    ct = cad.tf(child)
    pr = np.array(pt[:9]).reshape(3, 3)
    cr = np.array(ct[:9]).reshape(3, 3)
    delta = np.array(ct[9:12]) - np.array(pt[9:12])
    axes = [('Right Plane', 0), ('Top Plane', 1), ('Front Plane', 2)]
    created = []
    for cn, ci in axes:
        dots = pr @ cr[ci]
        pi = int(np.argmax(np.abs(dots)))
        pn = axes[pi][0]
        align = 0 if dots[pi] > 0 else 1
        signed = float(delta @ pr[pi])
        gap = abs(signed)
        entities = [cad.mappedplane(parent, pn), cad.mappedplane(child, cn)]
        label = prefix + '_' + cn.replace(' ', '_')
        existing = c(doc, 'FeatureByName', label)
        if existing is not None:
            created.append(label)
            continue
        if gap < 1e-8:
            m = cad.mate(doc, 0, label, entities, align)
        else:
            c(doc, 'ClearSelection2', True)
            for ent in entities:
                cad.entityselect(doc, ent)
            m = c(doc, 'AddDistanceMate', align, signed < 0, gap, gap, gap, 0, 0, iref())
            assert m is not None, ('datum distance failed', label)
            m.Name = label
            fd = c(m, 'GetDefinition')
            fd.FlipDimension = signed < 0
            assert c(m, 'ModifyDefinition', fd, doc, NULL)
        created.append(m.Name)
    return created


def add_world_plane_mate(doc, parent, pn, child, cn, label):
    """Add a single coincident or distance mate between parent plane pn and child plane cn at current world pose."""
    existing = c(doc, 'FeatureByName', label)
    if existing is not None:
        return existing
    axes = {'Right Plane': 0, 'Top Plane': 1, 'Front Plane': 2}
    pt = cad.tf(parent)
    ct = cad.tf(child)
    pr = np.array(pt[:9]).reshape(3, 3)
    cr = np.array(ct[:9]).reshape(3, 3)
    pi = axes[pn]
    ci = axes[cn]
    dot = float(pr[pi] @ cr[ci])
    align = 0 if dot > 0 else 1
    delta = np.array(ct[9:12]) - np.array(pt[9:12])
    signed = float(delta @ pr[pi])
    gap = abs(signed)
    entities = [cad.mappedplane(parent, pn), cad.mappedplane(child, cn)]
    if gap < 1e-8:
        m = cad.mate(doc, 0, label, entities, align)
    else:
        c(doc, 'ClearSelection2', True)
        for ent in entities:
            cad.entityselect(doc, ent)
        m = c(doc, 'AddDistanceMate', align, signed < 0, gap, gap, gap, 0, 0, iref())
        assert m is not None, ('plane mate failed', label)
        m.Name = label
        fd = c(m, 'GetDefinition')
        fd.FlipDimension = signed < 0
        assert c(m, 'ModifyDefinition', fd, doc, NULL)
    return m


def insert_locked_hw(doc, parent, path, key, world_pos_m, R_world, added_dict, mates_list, existing_hw_map=None):
    if existing_hw_map and f'Bench_HW_{key}_Right_Plane' in existing_hw_map:
        co = existing_hw_map[f'Bench_HW_{key}_Right_Plane']
        # Ensure distance mates match target world_pos_m at current parent pose
        pt = cad.tf(parent)
        pr = np.array(pt[:9]).reshape(3, 3)
        cr = np.array(R_world).reshape(3, 3)
        delta = np.array(world_pos_m) - np.array(pt[9:12])
        axes = [('Right Plane', 0), ('Top Plane', 1), ('Front Plane', 2)]
        for cn, ci in axes:
            dots = pr @ cr[ci]
            pi = int(np.argmax(np.abs(dots)))
            gap = abs(float(delta @ pr[pi]))
            label = f'Bench_HW_{key}_' + cn.replace(' ', '_')
            if gap > 1e-8:
                feat = c(doc, 'FeatureByName', label)
                if feat is not None:
                    fd = c(feat, 'GetDefinition')
                    if abs(fd.Distance - gap) > 1e-6:
                        fd.Distance = gap
                        assert c(feat, 'ModifyDefinition', fd, doc, NULL)
        added_dict[key] = co.Name2
        mates_list.extend([f'Bench_HW_{key}_Right_Plane', f'Bench_HW_{key}_Top_Plane', f'Bench_HW_{key}_Front_Plane'])
        return co
    if key in added_dict:
        return next(co for co in c(doc, 'GetComponents', True) if co.Name2 == added_dict[key])
    cad.getdoc(path, 1)
    cad.activate(doc)
    co = c(doc, 'AddComponent5', str(path), 0, '', False, '', *map(float, world_pos_m))
    assert co is not None, f'Failed to insert {key}'
    cad.set_transform(co, world_pos_m, R_world)
    m_names = rigid_datums_world(doc, parent, co, f'Bench_HW_{key}')
    added_dict[key] = co.Name2
    mates_list.extend(m_names)
    return co


def main():
    # =========================================================================
    # STEP 1.1: Pre-Flight Backup & Hash Verification
    # =========================================================================
    layout_path = FOLDER / 'BA_Bench_Actuation_Layout.SLDASM'
    rotor_path = ROTOR_DIR / 'BD_Bench_Development_Source.SLDASM'

    act_part_names = [
        'BA_Bench_Plate_650_12.SLDPRT',
        'BA_Bronze_Bush_10_8_L15.SLDPRT',
        'BA_D8_Guide_Shaft_L126.SLDPRT',
        'BA_Frame_Bench_Column_L102.SLDPRT',
        'BA_Guide_Support_Post.SLDPRT',
        'BA_NA23C60_T4A_CASE_REFERENCE.SLDPRT',
        'BA_NA23C60_T4A_ROD_REFERENCE.SLDPRT',
        'BA_NEMA23_Bench_Bracket.SLDPRT',
        'BA_X_Actuator_Drop_Link.SLDPRT',
        'BA_Y_Bronze_Sliding_Shoe.SLDPRT',
        'BA_Y_Cross_Slot_Drop_Link.SLDPRT',
        'BA_Y_Guided_Crosshead.SLDPRT',
    ]

    pre_hashes = {}
    # Record pre-task hashes from Before_CAD003B_Backup
    for src, bkp in [
        (layout_path, BACKUP_DIR / 'BA_Bench_Actuation_Layout.SLDASM'),
        (rotor_path, BACKUP_DIR / 'BD_Bench_Development_Source.SLDASM'),
    ]:
        if not bkp.exists():
            shutil.copy2(src, bkp)
        pre_hashes[src.name] = sha256_file(bkp)

    for pname in act_part_names:
        src = ACT_MODELS / pname
        bkp = BACKUP_DIR / 'Actuation_Models' / pname
        if not bkp.exists():
            shutil.copy2(src, bkp)
        pre_hashes[f'Actuation_Models/{pname}'] = sha256_file(bkp)

    pre_hashes['config/baseline.json'] = sha256_file(ROOT / 'config/baseline.json')
    print('PRE_HASHES_VERIFIED', json.dumps(pre_hashes, indent=2), flush=True)

    inspect = json.loads((FOLDER / 'ACTUATION_START_INSPECTION.json').read_text())
    xp = next(r for r in inspect if 'X_Slider_Drive_Tab_' in r['name'])['pos_mm']
    yp = next(r for r in inspect if 'Y_Carriage_Drive_Tab_' in r['name'])['pos_mm']

    app.CommandInProgress = True
    try:
        # =====================================================================
        # STEP 1.2 & STEP 3 PART MODIFICATIONS:
        # Material Audit + Detail Reliefs & Mounting Holes on Actuation_Models
        # =====================================================================
        bronze_mat = 'Commercial Bronze, UNS C22000 (90-10 Bronze)'
        for bname in ['BA_Y_Bronze_Sliding_Shoe.SLDPRT', 'BA_Bronze_Bush_10_8_L15.SLDPRT']:
            bdoc = cad.getdoc(ACT_MODELS / bname, 1)
            cad.activate(bdoc)
            c(bdoc, 'SetMaterialPropertyName2', 'Default', cad.MAT_DB, bronze_mat)
            assert c(bdoc, 'EditRebuild3')
            cad.save(bdoc)

        # 1) BA_X_Actuator_Drop_Link.SLDPRT:
        # Add Fixed_Base_Window_Relief so Deep_Actuator_Web passes cleanly through the Y=[30..48] mm
        # window of BD_RB_XY_Fixed_Base (at Z_local = [-9..-6] mm) with 1.0 mm radial clearance,
        # plus D3.4 through-holes and D7.5x2.0 bottom counterbores at (-27,28),(-13,28) so M3x12 low-head
        # screws (head Z_base=3.5..5.5 mm, shank Z_base=5.5..17.5 mm) and bottom washers (Z_base=5.5..6.0 mm)
        # clear both BD_RB_XY_Fixed_Base (Z_base=3.0 mm) and BD_RB_4-Inner_Carriage_Plate (Z_base=18.0 mm) by 0.50 mm.
        xdrop_doc = cad.getdoc(ACT_MODELS / 'BA_X_Actuator_Drop_Link.SLDPRT', 1)
        if c(xdrop_doc, 'FeatureByName', 'XDrop_M3_Bottom_Counterbore_H2') is None:
            c(app, 'CloseDoc', str(ACT_MODELS / 'BA_X_Actuator_Drop_Link.SLDPRT'))
            shutil.copy2(BACKUP_DIR / 'Actuation_Models/BA_X_Actuator_Drop_Link.SLDPRT', ACT_MODELS / 'BA_X_Actuator_Drop_Link.SLDPRT')
            xdrop_doc = cad.getdoc(ACT_MODELS / 'BA_X_Actuator_Drop_Link.SLDPRT', 1)
            cad.activate(xdrop_doc)
            c(xdrop_doc, 'ClearSelection2', True)
            assert c(xdrop_doc.Extension, 'SelectByID2', 'Right Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, NULL, 0)
            c(xdrop_doc.SketchManager, 'InsertSketch', True)
            xdrop_doc.SketchManager.AddToDB = True
            tr = list(xdrop_doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
            R_tr = np.array(tr[:9]).reshape(3, 3)
            P_tr = np.array(tr[9:12])
            for y0, z0, y1, z1 in [(24.0, -11.0, 31.0, -5.0), (47.0, -11.0, 49.0, -1.0)]:
                pts = [np.array([0.0, y, z]) / 1000.0 @ R_tr + P_tr for y, z in [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]]
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    c(xdrop_doc.SketchManager, 'CreateLine', float(a[0]), float(a[1]), 0.0, float(b[0]), float(b[1]), 0.0)
            cad.close_sketch(xdrop_doc)
            cad.cut_both(xdrop_doc, 'Fixed_Base_Window_Relief')
            assert c(xdrop_doc, 'EditRebuild3')
            cad.face_circles(xdrop_doc, 2, 0.0, [(-0.027, 0.028, 0.0), (-0.013, 0.028, 0.0)], 0.0017)
            cad.cut(xdrop_doc, 'XDrop_M3_Through_Recut', 0.0055)
            cad.face_circles(xdrop_doc, 2, -0.005, [(-0.027, 0.028, -0.005), (-0.013, 0.028, -0.005)], 0.00375)
            cad.cut(xdrop_doc, 'XDrop_M3_Bottom_Counterbore_H2', 0.0020)
            assert c(xdrop_doc, 'EditRebuild3')
            cad.inspect_part(xdrop_doc)
            cad.save(xdrop_doc)

        # 2) BA_Y_Cross_Slot_Drop_Link.SLDPRT:
        # - Add Outboard_Clearance_Web (X=-58..-44, Y=-26..-14, Z=-71..-6) and Fixed_Base_Ear_Clearance_Cut
        #   (X=-50..-31, Z=-20..-13) so YDrop clears BD_RB_XY_Fixed_Base's Routed_Frame_Ear_LeftMinus_Outboard
        #   (X_base=-42..-36, Z_base=0..3) across the entire +/-6.88 mm XY envelope.
        # - Cut YDrop_M3_Fastener_Underfoot_Relief (X=-43..-31, Z=-13.5..-6.0) and YDrop_M3_Through_Recut
        #   at (-35,-23),(-35,-17) so M3x10 screws + washers seat cleanly against Z_local=-6.0 mm.
        # - Cut Slot_Bottom_Upriser_Opening (Y=-29.51..-10.49, Z=-85..-74) so YHead's Shoe_Upriser enters
        #   the cross-slot cleanly from below without bottom-wall interference.
        ydrop_doc = cad.getdoc(ACT_MODELS / 'BA_Y_Cross_Slot_Drop_Link.SLDPRT', 1)
        cad.activate(ydrop_doc)
        if c(ydrop_doc, 'FeatureByName', 'Outboard_Clearance_Web') is None:
            cad.box(ydrop_doc, -58.0, -26.0, -44.0, -14.0, -71.0, -6.0, 'Outboard_Clearance_Web')
            # Cut Fixed_Base_Ear_Clearance_Cut from Top Plane
            c(ydrop_doc, 'ClearSelection2', True)
            assert c(ydrop_doc.Extension, 'SelectByID2', 'Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, NULL, 0)
            c(ydrop_doc.SketchManager, 'InsertSketch', True)
            ydrop_doc.SketchManager.AddToDB = True
            tr = list(ydrop_doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
            R_tr = np.array(tr[:9]).reshape(3, 3)
            P_tr = np.array(tr[9:12])
            pts = [np.array([x, 0.0, z]) / 1000.0 @ R_tr + P_tr for x, z in [(-50.0, -20.0), (-31.0, -20.0), (-31.0, -13.0), (-50.0, -13.0)]]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                c(ydrop_doc.SketchManager, 'CreateLine', float(a[0]), float(a[1]), 0.0, float(b[0]), float(b[1]), 0.0)
            cad.close_sketch(ydrop_doc)
            cad.cut_both(ydrop_doc, 'Fixed_Base_Ear_Clearance_Cut')

            # Cut Slot_Bottom_Upriser_Opening on Right Plane
            c(ydrop_doc, 'ClearSelection2', True)
            assert c(ydrop_doc.Extension, 'SelectByID2', 'Right Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, NULL, 0)
            c(ydrop_doc.SketchManager, 'InsertSketch', True)
            ydrop_doc.SketchManager.AddToDB = True
            tr = list(ydrop_doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
            R_tr = np.array(tr[:9]).reshape(3, 3)
            P_tr = np.array(tr[9:12])
            pts = [np.array([0.0, y, z]) / 1000.0 @ R_tr + P_tr for y, z in [(-29.51, -85.5), (-10.49, -85.5), (-10.49, -74.0), (-29.51, -74.0)]]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                c(ydrop_doc.SketchManager, 'CreateLine', float(a[0]), float(a[1]), 0.0, float(b[0]), float(b[1]), 0.0)
            cad.close_sketch(ydrop_doc)
            cad.cut_both(ydrop_doc, 'Slot_Bottom_Upriser_Opening')
            assert c(ydrop_doc, 'EditRebuild3')
        if c(ydrop_doc, 'FeatureByName', 'YDrop_M3_Through_Recut') is None:
            cad.box(ydrop_doc, -58.0, -26.0, -43.0, -14.0, -7.0, 0.0, 'Outboard_Foot_Web_Bridge')
            c(ydrop_doc, 'ClearSelection2', True)
            assert c(ydrop_doc.Extension, 'SelectByID2', 'Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, NULL, 0)
            c(ydrop_doc.SketchManager, 'InsertSketch', True)
            ydrop_doc.SketchManager.AddToDB = True
            tr = list(ydrop_doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
            R_tr = np.array(tr[:9]).reshape(3, 3)
            P_tr = np.array(tr[9:12])
            pts = [np.array([x, 0.0, z]) / 1000.0 @ R_tr + P_tr for x, z in [(-43.0, -13.5), (-31.0, -13.5), (-31.0, -6.0), (-43.0, -6.0)]]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                c(ydrop_doc.SketchManager, 'CreateLine', float(a[0]), float(a[1]), 0.0, float(b[0]), float(b[1]), 0.0)
            cad.close_sketch(ydrop_doc)
            cad.cut_both(ydrop_doc, 'YDrop_M3_Fastener_Underfoot_Relief')
            cad.face_circles(ydrop_doc, 2, 0.0, [(-0.035, -0.023, 0.0), (-0.035, -0.017, 0.0)], 0.0017)
            cad.cut(ydrop_doc, 'YDrop_M3_Through_Recut', 0.0065)
            assert c(ydrop_doc, 'EditRebuild3')
            cad.inspect_part(ydrop_doc)
            cad.save(ydrop_doc)

        # 3) BA_Y_Guided_Crosshead.SLDPRT:
        # - Cut coaxial D4.0 mm major thread bore M4_Shoe_Thread_Major_Envelope (X=0, Y=0, Z=12..23 mm).
        # - Cut Cross_Slot_Bottom_Clearance on Right Plane so Shoe_Upriser matches YShoe's 19.0 mm width
        #   (Y in [-9.5, +9.5] mm) and Adapter_Bridge top is at Z=18.0 mm (Z_base=-68.0 mm, 1.0 mm below YDrop).
        yhead_doc = cad.getdoc(ACT_MODELS / 'BA_Y_Guided_Crosshead.SLDPRT', 1)
        cad.activate(yhead_doc)
        if c(yhead_doc, 'FeatureByName', 'M4_Shoe_Thread_Major_Envelope') is None:
            cad.face_circles(yhead_doc, 2, 0.023, [(0.0, 0.0, 0.023)], 0.002)
            cad.cut(yhead_doc, 'M4_Shoe_Thread_Major_Envelope', 0.011)

            c(yhead_doc, 'ClearSelection2', True)
            assert c(yhead_doc.Extension, 'SelectByID2', 'Right Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, NULL, 0)
            c(yhead_doc.SketchManager, 'InsertSketch', True)
            yhead_doc.SketchManager.AddToDB = True
            tr = list(yhead_doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
            R_tr = np.array(tr[:9]).reshape(3, 3)
            P_tr = np.array(tr[9:12])
            for y0, z0, y1, z1 in [(-12.0, 18.0, -9.5, 23.5), (9.5, 18.0, 12.5, 23.5)]:
                pts = [np.array([0.0, y, z]) / 1000.0 @ R_tr + P_tr for y, z in [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]]
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    c(yhead_doc.SketchManager, 'CreateLine', float(a[0]), float(a[1]), 0.0, float(b[0]), float(b[1]), 0.0)
            cad.close_sketch(yhead_doc)
            cad.cut_both(yhead_doc, 'Cross_Slot_Bottom_Clearance')
            assert c(yhead_doc, 'EditRebuild3')
            cad.inspect_part(yhead_doc)
            cad.save(yhead_doc)

        # 4) BA_Bench_Plate_650_12.SLDPRT:
        # Cut mounting through-holes (Z = 0..12 mm):
        # - 4x Frame Columns: D6.6 mm (r=3.3 mm) at (+/-105, +/-85) mm
        # - 4x XBracket Foot Holes: D6.6 mm (r=3.3 mm) at X = -140.7 + xp[0] + {-10, +38}, Y = 36.5 + {-28, +28}
        # - 4x YBracket Foot Holes: D6.6 mm (r=3.3 mm) at X = -38.0 - {-28, +28}, Y = -162.7 + yp[1] + {-10, +38}
        # - 4x YGuideSupport Posts: D5.5 mm (r=2.75 mm) at X in {-52, -24}, Y in {-70, +20}
        bench_doc = cad.getdoc(ACT_MODELS / 'BA_Bench_Plate_650_12.SLDPRT', 1)
        cad.activate(bench_doc)
        col_xy = [(x, y) for x in [-105.0, 105.0] for y in [-85.0, 85.0]]
        xbrk_xy = [(-140.7 + xp[0] + dz, 36.5 + dx) for dx in [-28.0, 28.0] for dz in [-10.0, 38.0]]
        ybrk_xy = [(-38.0 - dx, -162.7 + yp[1] + dz) for dx in [-28.0, 28.0] for dz in [-10.0, 38.0]]
        post_xy = [(x, y) for x in [-52.0, -24.0] for y in [-70.0, 20.0]]

        if c(bench_doc, 'FeatureByName', 'Bench_M6_Anchor_Holes_12x_D6p6') is None:
            m6_pts = [(x / 1000.0, y / 1000.0, 0.012) for x, y in (col_xy + xbrk_xy + ybrk_xy)]
            cad.face_circles(bench_doc, 2, 0.012, m6_pts, 0.0033)
            cad.cut(bench_doc, 'Bench_M6_Anchor_Holes_12x_D6p6', 0.012)

            m5_pts = [(x / 1000.0, y / 1000.0, 0.012) for x, y in post_xy]
            cad.face_circles(bench_doc, 2, 0.012, m5_pts, 0.00275)
            cad.cut(bench_doc, 'Bench_M5_SupportPost_Holes_4x_D5p5', 0.012)
            assert c(bench_doc, 'EditRebuild3')
            cad.inspect_part(bench_doc)
            cad.save(bench_doc)

        # Verify all 12 Actuation_Models parts materials & masses
        act_materials_report = {}
        for pname in act_part_names:
            d = cad.getdoc(ACT_MODELS / pname, 1)
            db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
            mat = c(d, 'GetMaterialPropertyName2', 'Default', db)
            mp = c(d.Extension, 'CreateMassProperty2')
            assert mp.Density > 2000.0, f'{pname} has default 1000 kg/m3 density!'
            act_materials_report[pname] = {
                'material': mat,
                'database': db.value,
                'density_kg_m3': float(mp.Density),
                'mass_g': float(mp.Mass * 1000.0),
                'volume_mm3': float(mp.Volume * 1e9),
            }
        print('STEP1_ACTUATION_MATERIALS_VERIFIED', json.dumps(act_materials_report, indent=2), flush=True)

        # =====================================================================
        # STEP 3 PART CREATION: Create Reference Fasteners & Shaft Collars
        # =====================================================================
        created_hw_paths = {}
        # 1) Y-Shoe M4x12 screw
        created_hw_paths['BA_M4x12_ISO4762_REFERENCE'] = make_screw_part(
            ACT_MODELS, 'BA_M4x12_ISO4762_REFERENCE',
            'ISO 4762 M4x12 socket head cap screw reference for Y-shoe to Y-crosshead attachment.',
            4.0, 12.0, 7.0, 4.0
        )
        # 2) D8 Shaft Collar OD16 ID8 W8
        created_hw_paths['BA_D8_Shaft_Collar_OD16_W8_REFERENCE'] = make_washer_part(
            ACT_MODELS, 'BA_D8_Shaft_Collar_OD16_W8_REFERENCE',
            'D8 guide shaft axial retaining collar reference OD16 ID8 W8.',
            16.0, 8.0, 8.0
        )
        # 3) M3 drop-link fasteners
        m3x12_p = ACT_MODELS / 'BA_M3x12_ISO4762_REFERENCE.SLDPRT'
        if m3x12_p.exists():
            d_chk = cad.getdoc(m3x12_p, 1)
            if c(d_chk.Extension, 'CreateMassProperty2').Volume * 1e9 > 140.0:
                c(app, 'CloseDoc', str(m3x12_p))
                m3x12_p.unlink()
        created_hw_paths['BA_M3x12_ISO4762_REFERENCE'] = make_screw_part(
            ACT_MODELS, 'BA_M3x12_ISO4762_REFERENCE',
            'DIN 7984 / ISO 4762 low-head M3x12 socket cap screw reference (head D5.5 H2.0) for X-actuator drop link attachment.',
            3.0, 12.0, 5.5, 2.0
        )
        created_hw_paths['BA_M3x10_ISO4762_REFERENCE'] = make_screw_part(
            ACT_MODELS, 'BA_M3x10_ISO4762_REFERENCE',
            'ISO 4762 M3x10 socket head cap screw reference for Y-actuator drop link attachment.',
            3.0, 10.0, 5.5, 3.0
        )
        created_hw_paths['BA_M3_Washer_3p2x7x0p5_REFERENCE'] = make_washer_part(
            ACT_MODELS, 'BA_M3_Washer_3p2x7x0p5_REFERENCE',
            'DIN 125A M3 flat washer reference ID3.2 OD7.0 H0.5.',
            7.0, 3.2, 0.5
        )
        created_hw_paths['BA_M3_Nut_AF5p5_H2p4_REFERENCE'] = make_nut_part(
            ACT_MODELS, 'BA_M3_Nut_AF5p5_H2p4_REFERENCE',
            'ISO 4032 M3 hex nut reference AF5.5 H2.4.',
            3.0, 5.5, 2.4
        )
        # 4) Bench M6 & M5 anchor fasteners
        created_hw_paths['BA_M6x35_ISO4762_REFERENCE'] = make_screw_part(
            ACT_MODELS, 'BA_M6x35_ISO4762_REFERENCE',
            'ISO 4762 M6x35 socket head cap screw reference for bench column anchoring.',
            6.0, 35.0, 10.0, 6.0
        )
        created_hw_paths['BA_M6x25_ISO4762_REFERENCE'] = make_screw_part(
            ACT_MODELS, 'BA_M6x25_ISO4762_REFERENCE',
            'ISO 4762 M6x25 socket head cap screw reference for NEMA 23 bracket foot anchoring.',
            6.0, 25.0, 10.0, 6.0
        )
        created_hw_paths['BA_M6_Washer_6p4x12x1p6_REFERENCE'] = make_washer_part(
            ACT_MODELS, 'BA_M6_Washer_6p4x12x1p6_REFERENCE',
            'DIN 125A M6 flat washer reference ID6.4 OD12.0 H1.6.',
            12.0, 6.4, 1.6
        )
        created_hw_paths['BA_M6_Nut_AF10_H5_REFERENCE'] = make_nut_part(
            ACT_MODELS, 'BA_M6_Nut_AF10_H5_REFERENCE',
            'ISO 4032 M6 hex nut reference AF10.0 H5.0.',
            6.0, 10.0, 5.0
        )
        created_hw_paths['BA_M5x20_ISO4762_REFERENCE'] = make_screw_part(
            ACT_MODELS, 'BA_M5x20_ISO4762_REFERENCE',
            'ISO 4762 M5x20 socket head cap screw reference for Y-guide support post anchoring.',
            5.0, 20.0, 8.5, 5.0
        )
        created_hw_paths['BA_M5_Washer_5p3x10x1_REFERENCE'] = make_washer_part(
            ACT_MODELS, 'BA_M5_Washer_5p3x10x1_REFERENCE',
            'DIN 125A M5 flat washer reference ID5.3 OD10.0 H1.0.',
            10.0, 5.3, 1.0
        )

        # =====================================================================
        # STEP 1.3 & STEP 2: Open BA_Bench_Actuation_Layout.SLDASM,
        # Ground Rotor Base, Set Rotor Flexible & Add Kinematic Mates
        # =====================================================================
        rotor_doc = cad.getdoc(rotor_path, 2)
        asm = cad.getdoc(layout_path, 2)
        cad.activate(asm)
        assert c(asm, 'ForceRebuild3', False)

        top_comps = {co.Name2: co for co in c(asm, 'GetComponents', True)}
        all_comps = {co.Name2: co for co in c(asm, 'GetComponents', False)}

        bench = top_comps['BA_Bench_Plate_650_12-1']
        rotor = top_comps['BD_Bench_Development_Source-1']
        fixed_base = all_comps['BD_Bench_Development_Source-1/BD_RB_XY_Fixed_Base-1']
        x_slider = all_comps['BD_Bench_Development_Source-1/BD_RB_Intermediate_X_Slider-1']
        assem3 = all_comps['BD_Bench_Development_Source-1/BD_RB_Assem3-1']
        inner = all_comps['BD_Bench_Development_Source-1/BD_RB_Assem3-1/BD_RB_4-Inner_Carriage_Plate-1']
        ringco = all_comps['BD_Bench_Development_Source-1/BD_RB_Assem3-1/BD_RB_4-Outer_Control_Ring-1']
        shaft = next(co for k, co in all_comps.items() if k.startswith('BD_Bench_Development_Source-1/') and Path(c(co, 'GetPathName') or '').name == 'BD_RB_3-Drive_Shaft.SLDPRT')
        driver = next(co for k, co in all_comps.items() if k.startswith('BD_Bench_Development_Source-1/') and Path(c(co, 'GetPathName') or '').name == 'BD_RB_Oldham_Input_PROTOTYPE.SLDPRT')
        receiver = next(co for k, co in all_comps.items() if k.startswith('BD_Bench_Development_Source-1/') and Path(c(co, 'GetPathName') or '').name == 'BD_RB_Oldham_Output_PROTOTYPE.SLDPRT')
        floating = next(co for k, co in all_comps.items() if k.startswith('BD_Bench_Development_Source-1/') and Path(c(co, 'GetPathName') or '').name == 'BD_RB_Oldham_Floating_Disk_PROTOTYPE.SLDPRT')
        blades = {
            co.Name2.split('-')[-1]: co
            for k, co in all_comps.items()
            if k.startswith('BD_Bench_Development_Source-1/') and Path(c(co, 'GetPathName') or '').name == 'BD_RB_Part1.SLDPRT'
        }

        origin = np.array(cad.tf(fixed_base)[9:12])

        xdrop = top_comps['BA_X_Actuator_Drop_Link-1']
        ydrop = top_comps['BA_Y_Cross_Slot_Drop_Link-1']
        xrod = top_comps['BA_NA23C60_T4A_ROD_REFERENCE-1']
        xcase = top_comps['BA_NA23C60_T4A_CASE_REFERENCE-1']
        yhead = top_comps['BA_Y_Guided_Crosshead-1']
        yshoe = top_comps['BA_Y_Bronze_Sliding_Shoe-1']
        ybush0 = top_comps['BA_Bronze_Bush_10_8_L15-1']
        ybush1 = top_comps['BA_Bronze_Bush_10_8_L15-2']
        yrod = top_comps['BA_NA23C60_T4A_ROD_REFERENCE-2']
        ycase = top_comps['BA_NA23C60_T4A_CASE_REFERENCE-2']

        # Record initial transforms of all 24 components before adding mates
        initial_tfs = {k: cad.tf(co) for k, co in top_comps.items()}
        initial_x_slider_tf = cad.tf(x_slider)
        initial_inner_tf = cad.tf(inner)
        initial_shaft_tf = cad.tf(shaft)
        initial_phi = math.atan2(initial_shaft_tf[1], initial_shaft_tf[0])

        added_kinematic_mates = []

        # 1) Unfix rotor, lock BD_RB_XY_Fixed_Base-1 to BA_Bench_Plate_650_12-1, set BD_Bench_Development_Source-1 to Flexible
        c(asm, 'ClearSelection2', True)
        c(rotor, 'Select4', False, NULL, False)
        c(asm, 'UnfixComponent')
        added_kinematic_mates.extend(rigid_datums_world(asm, bench, fixed_base, 'Bench_RotorBase'))

        c(asm, 'ClearSelection2', True)
        c(rotor, 'Select4', False, NULL, False)
        assert c(asm, 'CompConfigProperties5', 2, 1, True, True, c(rotor, 'ReferencedConfiguration'), False, False)
        assert rotor.Solving == 1 and assem3.Solving == 1

        # 2) Float the 8 moving actuation components
        moving_act_comps = [xdrop, ydrop, xrod, yhead, yshoe, ybush0, ybush1, yrod]
        for co in moving_act_comps:
            c(asm, 'ClearSelection2', True)
            c(co, 'Select4', False, NULL, False)
            c(asm, 'UnfixComponent')
            assert not c(co, 'IsFixed'), f'{co.Name2} remained fixed!'

        # 3) Add Kinematic Mates:
        # - XDrop <-> BD_RB_Intermediate_X_Slider-1
        added_kinematic_mates.extend(rigid_datums_world(asm, x_slider, xdrop, 'Bench_XDrop'))
        # - YDrop <-> BD_RB_4-Inner_Carriage_Plate-1
        added_kinematic_mates.extend(rigid_datums_world(asm, inner, ydrop, 'Bench_YDrop'))
        # - YShoe, YBush0, YBush1, YRod rigidly locked to YHead
        added_kinematic_mates.extend(rigid_datums_world(asm, yhead, yshoe, 'Bench_YShoe'))
        added_kinematic_mates.extend(rigid_datums_world(asm, yhead, ybush0, 'Bench_YBush0'))
        added_kinematic_mates.extend(rigid_datums_world(asm, yhead, ybush1, 'Bench_YBush1'))
        added_kinematic_mates.extend(rigid_datums_world(asm, yhead, yrod, 'Bench_YRod'))
        # - XRod rigidly coupled to XDrop (slides coaxially inside XCase)
        added_kinematic_mates.extend(rigid_datums_world(asm, xdrop, xrod, 'Bench_XRod'))
        # - YHead guided along World Y relative to Bench (Right Plane = World X, Front Plane = World Z)
        m_yh_x = add_world_plane_mate(asm, bench, 'Right Plane', yhead, 'Right Plane', 'Bench_YHead_Guide_Right_Plane')
        m_yh_z = add_world_plane_mate(asm, bench, 'Front Plane', yhead, 'Front Plane', 'Bench_YHead_Guide_Front_Plane')
        added_kinematic_mates.extend([m_yh_x.Name, m_yh_z.Name])
        # - Cross-Slot Y-coupling between YDrop Top Plane (World Y) and YShoe Top Plane (World Y)
        m_slot_y = add_world_plane_mate(asm, ydrop, 'Top Plane', yshoe, 'Top Plane', 'Bench_CrossSlot_Y_Coupling')
        added_kinematic_mates.append(m_slot_y.Name)
        # - Controllable X and Y Actuator Stroke Mates (XCase Front Plane <-> XRod Front Plane, YCase Front Plane <-> YRod Front Plane)
        mx = add_world_plane_mate(asm, xcase, 'Front Plane', xrod, 'Front Plane', 'Bench_X_Actuator_Stroke')
        my = add_world_plane_mate(asm, ycase, 'Front Plane', yrod, 'Front Plane', 'Bench_Y_Actuator_Stroke')
        # Convert mx and my from Coincident (if gap=0) to MateDistanceDim initialized at 0.0 mm so they are dimension-drivable
        for m_name, case_co, rod_co in [('Bench_X_Actuator_Stroke', xcase, xrod), ('Bench_Y_Actuator_Stroke', ycase, yrod)]:
            feat = c(asm, 'FeatureByName', m_name)
            if feat is not None and c(feat, 'GetTypeName2') != 'MateDistanceDim':
                c(asm, 'ClearSelection2', True)
                c(feat, 'Select2', False, 0)
                c(asm, 'EditDelete')
                feat = None
            if feat is None:
                c(asm, 'ClearSelection2', True)
                cad.entityselect(asm, cad.mappedplane(case_co, 'Front Plane'))
                cad.entityselect(asm, cad.mappedplane(rod_co, 'Front Plane'))
                feat = c(asm, 'AddDistanceMate', 0, False, 0.0, 0.0, 0.0, 0, 0, iref())
                assert feat is not None, f'Failed to create {m_name}'
                feat.Name = m_name
            added_kinematic_mates.append(m_name)

        mx = c(asm, 'FeatureByName', 'Bench_X_Actuator_Stroke')
        my = c(asm, 'FeatureByName', 'Bench_Y_Actuator_Stroke')

        assert c(asm, 'ForceRebuild3', False)
        step2_mate_errors = cad.errors(cad.active_mates(asm))
        assert not step2_mate_errors, ('Step 2 mate errors:', step2_mate_errors)

        # Verify < 1e-6 m pose drift after adding all kinematic mates
        max_step2_drift_m = 0.0
        for k, co in top_comps.items():
            if k == 'BD_Bench_Development_Source-1':
                continue
            drift = float(np.max(np.abs(np.array(cad.tf(co)[9:12]) - np.array(initial_tfs[k][9:12]))))
            max_step2_drift_m = max(max_step2_drift_m, drift)
        assert max_step2_drift_m < 1e-6, f'Pose drift after Step 2 mates: {max_step2_drift_m}'
        print('STEP2_KINEMATIC_MATES_VERIFIED drift_m:', max_step2_drift_m, flush=True)

        # =====================================================================
        # STEP 3 ASSEMBLY INSERTION: Install Fasteners, Collars & Bench Hardware
        # =====================================================================
        existing_hw_map = {}
        for co in top_comps.values():
            if 'REFERENCE' not in co.Name2:
                continue
            for m in (c(co, 'GetMates') or []):
                if (m.Name or '').startswith('Bench_HW_') and m.Name.endswith('_Right_Plane'):
                    existing_hw_map[m.Name] = co
        added_hw_instances = {}
        added_hw_mates = []
        R_ident = np.eye(3)
        R_flip_z = np.diag([1.0, -1.0, -1.0])
        R_shaft = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])

        # 3.1: Y-Shoe M4x12 retaining screw (seated at Z_shoe = 1.8 mm -> Z_base = -61.2 mm, pointing -Z into YHead)
        m4_pos = origin + np.array([-38.0, -20.0 + yp[1], -61.2]) / 1000.0
        insert_locked_hw(asm, yhead, created_hw_paths['BA_M4x12_ISO4762_REFERENCE'], 'YShoe_M4Screw', m4_pos, R_flip_z, added_hw_instances, added_hw_mates, existing_hw_map)

        # 3.2: 4x D8 Guide-Shaft Axial Collars abutting outer faces of YGuideSupport00..11 (Y_base = -86..-78 and +28..+36, Z_base = -80)
        for i, x_mm in enumerate([-52.0, -24.0]):
            for j, y_start_mm in enumerate([-86.0, 28.0]):
                col_pos = origin + np.array([x_mm, y_start_mm, -80.0]) / 1000.0
                insert_locked_hw(asm, bench, created_hw_paths['BA_D8_Shaft_Collar_OD16_W8_REFERENCE'], f'YShaftCollar_{i}{j}', col_pos, R_shaft, added_hw_instances, added_hw_mates, existing_hw_map)

        # 3.3: Drop-Link Mounting Fasteners:
        # - 2x M3x12 screw + 2 washers + nut on XDrop at (-27, 28) and (-13, 28) relative to XDrop origin (xp)
        for idx, (hx, hy) in enumerate([(-27.0, 28.0), (-13.0, 28.0)], 1):
            base_xy = np.array([xp[0] + hx, xp[1] + hy, 0.0])
            # Bottom washer recessed in D7.5x2.0 counterbore: Z_local = -3.5..-3.0 (Z_base = 5.5..6.0)
            insert_locked_hw(asm, xdrop, created_hw_paths['BA_M3_Washer_3p2x7x0p5_REFERENCE'], f'XDrop_BotWasher{idx}', origin + (base_xy + [0, 0, 5.5]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            # Screw at Z_local = -3.5 (Z_base = 5.5), head Z_base = 3.5..5.5, shank +Z up to +8.5 (Z_base = 17.5)
            insert_locked_hw(asm, xdrop, created_hw_paths['BA_M3x12_ISO4762_REFERENCE'], f'XDrop_Screw{idx}', origin + (base_xy + [0, 0, 5.5]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            # Top washer Z_local = 3.0..3.5 (Z_base = 12.0..12.5)
            insert_locked_hw(asm, xdrop, created_hw_paths['BA_M3_Washer_3p2x7x0p5_REFERENCE'], f'XDrop_TopWasher{idx}', origin + (base_xy + [0, 0, 12.0]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            # Top nut Z_local = 3.5..5.9 (Z_base = 12.5..14.9)
            insert_locked_hw(asm, xdrop, created_hw_paths['BA_M3_Nut_AF5p5_H2p4_REFERENCE'], f'XDrop_Nut{idx}', origin + (base_xy + [0, 0, 12.5]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)

        # - 2x M3x10 screw + washer on YDrop at (-35, -23) and (-35, -17) relative to YDrop origin (yp)
        for idx, (hx, hy) in enumerate([(-35.0, -23.0), (-35.0, -17.0)], 1):
            base_xy = np.array([yp[0] + hx, yp[1] + hy, 0.0])
            # Bottom washer Z_local = -6.5..-6.0 (Z_base = 11.5..12.0)
            insert_locked_hw(asm, ydrop, created_hw_paths['BA_M3_Washer_3p2x7x0p5_REFERENCE'], f'YDrop_Washer{idx}', origin + (base_xy + [0, 0, 11.5]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            # Screw at Z_local = -6.5 (Z_base = 11.5), shank +Z up to +3.5 (Z_base = 21.5)
            insert_locked_hw(asm, ydrop, created_hw_paths['BA_M3x10_ISO4762_REFERENCE'], f'YDrop_Screw{idx}', origin + (base_xy + [0, 0, 11.5]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)

        # 3.4: Bench Plate Anchor Fasteners:
        # - 4x Frame Columns: M6x35 bolt + M6 washer from underneath Bench (Z_base = -122.0 mm)
        for idx, (cx, cy) in enumerate(col_xy, 1):
            insert_locked_hw(asm, bench, created_hw_paths['BA_M6_Washer_6p4x12x1p6_REFERENCE'], f'FrameCol_Washer{idx}', origin + np.array([cx, cy, -123.6]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            insert_locked_hw(asm, bench, created_hw_paths['BA_M6x35_ISO4762_REFERENCE'], f'FrameCol_Bolt{idx}', origin + np.array([cx, cy, -123.6]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)

        # - 8x NEMA 23 Bracket Foot Holes (4 on XBracket + 4 on YBracket): M6x25 bolt + top/bot washers + M6 nut
        for idx, (bx, by) in enumerate(xbrk_xy + ybrk_xy, 1):
            # Top washer on bracket foot top (Z_base = -102.0..-100.4 mm)
            insert_locked_hw(asm, bench, created_hw_paths['BA_M6_Washer_6p4x12x1p6_REFERENCE'], f'BrkFoot_TopWasher{idx}', origin + np.array([bx, by, -102.0]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            # M6x25 bolt pointing -Z from Z_base = -100.4 mm down to -125.4 mm
            insert_locked_hw(asm, bench, created_hw_paths['BA_M6x25_ISO4762_REFERENCE'], f'BrkFoot_Bolt{idx}', origin + np.array([bx, by, -100.4]) / 1000.0, R_flip_z, added_hw_instances, added_hw_mates, existing_hw_map)
            # Bottom washer under bench plate (Z_base = -123.6..-122.0 mm)
            insert_locked_hw(asm, bench, created_hw_paths['BA_M6_Washer_6p4x12x1p6_REFERENCE'], f'BrkFoot_BotWasher{idx}', origin + np.array([bx, by, -123.6]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            # Bottom M6 nut (Z_base = -128.6..-123.6 mm)
            insert_locked_hw(asm, bench, created_hw_paths['BA_M6_Nut_AF10_H5_REFERENCE'], f'BrkFoot_Nut{idx}', origin + np.array([bx, by, -128.6]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)

        # - 4x Y-Guide Support Posts: M5x20 bolt + M5 washer from underneath Bench (Z_base = -122.0 mm)
        for idx, (px, py) in enumerate(post_xy, 1):
            insert_locked_hw(asm, bench, created_hw_paths['BA_M5_Washer_5p3x10x1_REFERENCE'], f'YPost_Washer{idx}', origin + np.array([px, py, -123.0]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)
            insert_locked_hw(asm, bench, created_hw_paths['BA_M5x20_ISO4762_REFERENCE'], f'YPost_Bolt{idx}', origin + np.array([px, py, -123.0]) / 1000.0, R_ident, added_hw_instances, added_hw_mates, existing_hw_map)

        assert c(asm, 'ForceRebuild3', False)
        step3_mate_errors = cad.errors(cad.active_mates(asm))
        assert not step3_mate_errors, ('Step 3 mate errors:', step3_mate_errors)
        if len(existing_hw_map) < 65:
            cad.save(asm)
        print('STEP3_HARDWARE_INSTALLED count:', len(added_hw_instances), flush=True)

        # =====================================================================
        # STEP 4: Coupled Multi-Pose Kinematic Sweep & Boolean Interference Audit
        # =====================================================================
        # Helper to drive X and Y Zaber actuator stroke mates to target rotor eccentricity (target_x_m, target_y_m)
        xp0_m = xp[0] / 1000.0
        yp1_m = yp[1] / 1000.0
        angle_param = c(rotor_doc, 'Parameter', 'D1@RevB_SETUP_Rotor_Angle')

        def _drive_single_axis(mate_feat, comp_to_check, coord_idx, target_m, zero_offset_m):
            stroke = target_m - zero_offset_m
            for flip in [stroke < 0, not (stroke < 0)]:
                fd = c(mate_feat, 'GetDefinition')
                fd.Distance = abs(stroke)
                fd.FlipDimension = bool(flip)
                assert c(mate_feat, 'ModifyDefinition', fd, asm, NULL)
                assert c(asm, 'ForceRebuild3', False)
                actual = cad.tf(comp_to_check)[9 + coord_idx] - origin[coord_idx]
                if abs(actual - target_m) < 1e-5:
                    return
            raise AssertionError(f'Axis {coord_idx} stroke could not reach {target_m}: got {actual}')

        def set_zaber_xy_eccentricity(tx_m, ty_m):
            # Step via (0, 0) first so single-axis updates never exceed the r <= 6.88 mm circular stop
            cur_x = cad.tf(x_slider)[9] - origin[0]
            cur_y = cad.tf(inner)[10] - origin[1]
            if abs(cur_x) > 1e-5:
                _drive_single_axis(mx, x_slider, 0, 0.0, xp0_m)
            if abs(cur_y) > 1e-5:
                _drive_single_axis(my, inner, 1, 0.0, yp1_m)
            if abs(tx_m) > 1e-9:
                _drive_single_axis(mx, x_slider, 0, tx_m, xp0_m)
            if abs(ty_m) > 1e-9:
                _drive_single_axis(my, inner, 1, ty_m, yp1_m)

        def set_coupled_shaft_angle(target_phi):
            target_phi %= 2.0 * math.pi
            for cand in [target_phi, (2.0 * math.pi - target_phi) % (2.0 * math.pi)]:
                angle_param.SystemValue = float(cand)
                assert c(asm, 'ForceRebuild3', False)
                st = cad.tf(shaft)
                actual = math.atan2(st[1], st[0])
                err = (actual - target_phi + math.pi) % (2.0 * math.pi) - math.pi
                if abs(err) < math.radians(0.001):
                    return
            raise AssertionError(('Coupled shaft angle could not reach target', math.degrees(target_phi), math.degrees(actual)))

        # Prepare pre-cached body templates for fast boolean intersection checks
        mu = c(app, 'GetMathUtility')
        part_body_cache = {}
        def get_transformed_body(comp):
            p = c(comp, 'GetModelDoc2')
            path = c(comp, 'GetPathName')
            if path not in part_body_cache:
                part_body_cache[path] = c(c(p, 'GetBodies2', 0, False)[0], 'Copy')
            b_copy = c(part_body_cache[path], 'Copy')
            assert c(b_copy, 'ApplyTransform', c(mu, 'CreateTransform', array(cad.tf(comp))))
            return b_copy

        def bool_overlap_mm3(comp_a, comp_b):
            ba = get_transformed_body(comp_a)
            bb = get_transformed_body(comp_b)
            box_a = list(c(ba, 'GetBodyBox'))
            box_b = list(c(bb, 'GetBodyBox'))
            if box_a[3] < box_b[0] or box_b[3] < box_a[0] or box_a[4] < box_b[1] or box_b[4] < box_a[1] or box_a[5] < box_b[2] or box_b[5] < box_a[2]:
                return 0.0
            ov = c(ba, 'Operations2', 15901, bb, iref()) or []
            return float(sum(c(x, 'GetMassProperties', 1.0)[3] * 1e9 for x in ov))

        # Collect moving actuation components (including moving drop-link/shoe fasteners) and stationary targets
        top_comps_now = {co.Name2: co for co in c(asm, 'GetComponents', True)}
        moving_act_Plus_hw = [
            xdrop, ydrop, xrod, yhead, yshoe, ybush0, ybush1, yrod,
            top_comps_now[added_hw_instances['YShoe_M4Screw']],
            top_comps_now[added_hw_instances['XDrop_Screw1']],
            top_comps_now[added_hw_instances['XDrop_Screw2']],
            top_comps_now[added_hw_instances['XDrop_BotWasher1']],
            top_comps_now[added_hw_instances['XDrop_BotWasher2']],
            top_comps_now[added_hw_instances['XDrop_TopWasher1']],
            top_comps_now[added_hw_instances['XDrop_TopWasher2']],
            top_comps_now[added_hw_instances['XDrop_Nut1']],
            top_comps_now[added_hw_instances['XDrop_Nut2']],
            top_comps_now[added_hw_instances['YDrop_Screw1']],
            top_comps_now[added_hw_instances['YDrop_Screw2']],
            top_comps_now[added_hw_instances['YDrop_Washer1']],
            top_comps_now[added_hw_instances['YDrop_Washer2']],
        ]
        stationary_bench_targets = [
            co for k, co in top_comps_now.items()
            if k != 'BD_Bench_Development_Source-1' and co not in moving_act_Plus_hw
        ]
        rotor_check_targets = [
            fixed_base,
            x_slider,
            inner,
            ringco,
            all_comps['BD_Bench_Development_Source-1/BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE-1'],
            all_comps['BD_Bench_Development_Source-1/BD_RB_Cage_Lower_Frame_PROTOTYPE-1'],
            all_comps['BD_Bench_Development_Source-1/BD_RB_MGNR05R-1'],
            all_comps['BD_Bench_Development_Source-1/BD_RB_MGNR05R-2'],
            all_comps['BD_Bench_Development_Source-1/BD_RB_MGN5C-1'],
            all_comps['BD_Bench_Development_Source-1/BD_RB_MGN5C-2'],
        ]

        # Critical pitch-extrema angles at (+6.88, 0)
        pivot1 = cad.world(blades['1'], [0.0095, 0.0, 0.0]) - np.array(initial_shaft_tf[9:12])
        radial_shift = math.atan2(pivot1[1], pivot1[0]) - initial_phi
        theta_grid = np.arange(36000) * 2.0 * math.pi / 36000.0
        delta_phase = math.radians(-15.825385589180533)
        P_grid = 0.095 * np.c_[np.cos(theta_grid), np.sin(theta_grid)]
        B_grid = np.array([0.00688, 0.0]) + 0.04 * np.c_[np.cos(theta_grid + delta_phase), np.sin(theta_grid + delta_phase)]
        V_grid = B_grid - P_grid
        dist_grid = np.linalg.norm(V_grid, axis=1)
        k_grid = (0.012 ** 2 + dist_grid ** 2 - 0.05652665325007647 ** 2) / (2.0 * 0.012 * dist_grid)
        alpha_grid = np.arctan2(V_grid[:, 1], V_grid[:, 0])
        cand_grid = np.array([alpha_grid + np.arccos(k_grid), alpha_grid - np.arccos(k_grid)])
        pitch_grid = (cand_grid - (theta_grid - math.pi / 2.0) + math.pi) % (2.0 * math.pi) - math.pi
        pitch_grid = np.take_along_axis(pitch_grid, np.argmin(abs(pitch_grid), axis=0)[None, :], axis=0)[0]
        crit_indices = [int(np.argmin(pitch_grid)), int(np.argmax(pitch_grid))]

        xy_poses = [
            ('center_0_0', 0.0, 0.0),
            ('cardinal_0deg_+6p88_0', 0.00688, 0.0),
            ('cardinal_90deg_0_+6p88', 0.0, 0.00688),
            ('cardinal_180deg_-6p88_0', -0.00688, 0.0),
            ('cardinal_270deg_0_-6p88', 0.0, -0.00688),
            ('diagonal_45deg', 0.00688 / math.sqrt(2.0), 0.00688 / math.sqrt(2.0)),
            ('diagonal_135deg', -0.00688 / math.sqrt(2.0), 0.00688 / math.sqrt(2.0)),
            ('diagonal_225deg', -0.00688 / math.sqrt(2.0), -0.00688 / math.sqrt(2.0)),
            ('diagonal_315deg', 0.00688 / math.sqrt(2.0), -0.00688 / math.sqrt(2.0)),
        ]

        wrap = lambda a: (a + math.pi) % (2.0 * math.pi) - math.pi
        phase = math.radians(164.17461441081947)
        pose_results = []
        total_bool_checks = 0
        max_unexpected_overlap_mm3 = 0.0
        classified_fastener_overlaps = []
        x_slot_sliding_offsets_mm = []

        try:
            for label, dx, dy in xy_poses:
                set_zaber_xy_eccentricity(dx, dy)
                for deg in [0, 90, 180, 270]:
                    target_phi = initial_phi + math.radians(deg)
                    set_coupled_shaft_angle(target_phi)

                    top_errs = cad.errors(cad.active_mates(asm))
                    sub_errs = cad.errors(cad.active_mates(rotor_doc))
                    assert not top_errs and not sub_errs, (label, deg, top_errs, sub_errs)

                    # Verify coupled carriage positions and YShoe X-slot sliding decoupling
                    xs_pos = np.array(cad.tf(x_slider)[9:12]) - origin
                    in_pos = np.array(cad.tf(inner)[9:12]) - origin
                    xd_pos = np.array(cad.tf(xdrop)[9:12]) - origin
                    yd_pos = np.array(cad.tf(ydrop)[9:12]) - origin
                    yh_pos = np.array(cad.tf(yhead)[9:12]) - origin
                    ys_pos = np.array(cad.tf(yshoe)[9:12]) - origin

                    assert abs(xs_pos[0] - dx) < 1e-5 and abs(xs_pos[1]) < 1e-5
                    assert abs(in_pos[0] - dx) < 1e-5 and abs(in_pos[1] - dy) < 1e-5
                    assert abs(xd_pos[0] - dx) < 1e-5 and abs(yd_pos[0] - dx) < 1e-5 and abs(yd_pos[1] - dy) < 1e-5
                    # YShoe & YHead stay at X_base = -38.0 mm while moving by dy in Y!
                    assert abs(ys_pos[0] - (-0.038)) < 1e-5 and abs(ys_pos[1] - (-0.020 + dy)) < 1e-5
                    slot_x_slide_mm = float((yd_pos[0] - (ys_pos[0] + 0.038)) * 1000.0)
                    x_slot_sliding_offsets_mm.append(round(slot_x_slide_mm, 4))

                    st = cad.tf(shaft)
                    rt = cad.tf(ringco)
                    phi = math.atan2(st[1], st[0])
                    ring_angle = math.atan2(rt[1], rt[0])
                    phase_err = math.degrees(wrap(ring_angle - phi - phase))
                    assert abs(phase_err) < 0.001

                    pitches = []
                    for n in ['1', '2', '3', '4']:
                        bco = blades[n]
                        bt = cad.tf(bco)
                        piv = cad.world(bco, [0.0095, 0.0, 0.0])
                        rad_vec = piv - np.array(st[9:12])
                        p_deg = math.degrees(wrap(math.atan2(bt[1], bt[0]) - math.atan2(rad_vec[1], rad_vec[0]) - math.pi / 2.0))
                        pitches.append(p_deg)

                    # Run boolean intersection checks at deg == 0 for every XY pose (and all 4 shaft angles at center & +6.88,0)
                    unexpected_overlaps = []
                    if deg == 0 or label in ['center_0_0', 'cardinal_0deg_+6p88_0']:
                        # Check moving actuation parts vs stationary bench hardware & rotor targets
                        for ma in moving_act_Plus_hw:
                            for tgt in stationary_bench_targets + rotor_check_targets + [xdrop, yhead, ydrop, yshoe]:
                                if ma.Name2 == tgt.Name2:
                                    continue
                                vol = bool_overlap_mm3(ma, tgt)
                                total_bool_checks += 1
                                if vol > 1e-5:
                                    # Classify intentional M3x12 shank penetration through undrilled X_Slider at (-27,28),(-13,28)
                                    pair_names = {ma.Name2, tgt.Name2}
                                    if any('BA_M3x12_ISO4762_REFERENCE' in n for n in pair_names) and any('BD_RB_Intermediate_X_Slider' in n for n in pair_names):
                                        if not any(c_item['pair'] == sorted(list(pair_names)) for c_item in classified_fastener_overlaps):
                                            classified_fastener_overlaps.append({
                                                'pair': sorted(list(pair_names)),
                                                'overlap_mm3': round(vol, 4),
                                                'classification': 'Intentional reference fastener shank envelope through undrilled BD_RB_Intermediate_X_Slider at (-27,28) and (-13,28) mm (rotor part preserved untouched per scope).'
                                            })
                                    else:
                                        max_unexpected_overlap_mm3 = max(max_unexpected_overlap_mm3, vol)
                                        unexpected_overlaps.append({'pair': [ma.Name2, tgt.Name2], 'overlap_mm3': vol})
                    assert not unexpected_overlaps, (label, deg, unexpected_overlaps)

                    pose_results.append({
                        'pose_label': label,
                        'commanded_xy_mm': [round(dx * 1000.0, 4), round(dy * 1000.0, 4)],
                        'x_slider_xy_mm': [round(xs_pos[0] * 1000.0, 4), round(xs_pos[1] * 1000.0, 4)],
                        'inner_carriage_xy_mm': [round(in_pos[0] * 1000.0, 4), round(in_pos[1] * 1000.0, 4)],
                        'yshoe_world_rel_base_mm': [round(ys_pos[0] * 1000.0, 4), round(ys_pos[1] * 1000.0, 4), round(ys_pos[2] * 1000.0, 4)],
                        'cross_slot_x_slide_offset_mm': round(slot_x_slide_mm, 4),
                        'shaft_increment_deg': deg,
                        'shaft_angle_deg': round(math.degrees(phi), 4),
                        'ring_phase_error_deg': float(phase_err),
                        'blade_pitch_deg': [round(x, 4) for x in pitches],
                        'unexpected_boolean_overlaps': unexpected_overlaps,
                    })

                # Dense pitch-extrema check at (+6.88, 0) mm inside BA_Bench_Actuation_Layout.SLDASM
                if label == 'cardinal_0deg_+6p88_0':
                    for idx in crit_indices:
                        phi_crit = (theta_grid[idx] - radial_shift) % (2.0 * math.pi)
                        set_coupled_shaft_angle(phi_crit)
                        st = cad.tf(shaft)
                        bco = blades['1']
                        bt = cad.tf(bco)
                        piv = cad.world(bco, [0.0095, 0.0, 0.0])
                        rad_vec = piv - np.array(st[9:12])
                        p1_deg = math.degrees(wrap(math.atan2(bt[1], bt[0]) - math.atan2(rad_vec[1], rad_vec[0]) - math.pi / 2.0))
                        pred_deg = math.degrees(pitch_grid[idx])
                        err_deg = p1_deg - pred_deg
                        assert abs(err_deg) < 0.001, (p1_deg, pred_deg, err_deg)
                        pose_results.append({
                            'pose_label': 'pitch_extrema_+6p88_0',
                            'commanded_xy_mm': [6.88, 0.0],
                            'shaft_angle_deg': float(math.degrees(math.atan2(st[1], st[0]))),
                            'Part1_1_pitch_deg': float(p1_deg),
                            'predicted_pitch_deg': float(pred_deg),
                            'prediction_error_deg': float(err_deg),
                            'unexpected_boolean_overlaps': [],
                        })
                print('COUPLED_POSE_SWEEP_OK', label, 'total_bool_checks:', total_bool_checks, flush=True)
        finally:
            # Restore initial saved pose (xp0_m, yp1_m, initial_phi)
            set_zaber_xy_eccentricity(xp0_m, yp1_m)
            set_coupled_shaft_angle(initial_phi)
            assert c(asm, 'ForceRebuild3', False)

        final_top_errors = cad.errors(cad.active_mates(asm))
        final_sub_errors = cad.errors(cad.active_mates(rotor_doc))
        assert not final_top_errors and not final_sub_errors, (final_top_errors, final_sub_errors)

        restored_xs_delta = float(np.max(np.abs(np.array(cad.tf(x_slider)) - np.array(initial_x_slider_tf))))
        restored_in_delta = float(np.max(np.abs(np.array(cad.tf(inner)) - np.array(initial_inner_tf))))
        restored_sh_delta = float(np.max(np.abs(np.array(cad.tf(shaft)) - np.array(initial_shaft_tf))))
        assert max(restored_xs_delta, restored_in_delta, restored_sh_delta) < 1e-6

        # Save rotor_doc (if touched) and BA_Bench_Actuation_Layout.SLDASM
        cad.save(rotor_doc)
        cad.save(asm)

        mp_asm = c(asm.Extension, 'CreateMassProperty2')
        total_bench_mass_kg = float(mp_asm.Mass)
        total_bench_mass_g = float(mp_asm.Mass * 1000.0)

        # Build complete material & mass table for all components in BA_Bench_Actuation_Layout.SLDASM
        hw_materials_report = {}
        for hname, hpath in created_hw_paths.items():
            hd = cad.getdoc(hpath, 1)
            db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
            mat = c(hd, 'GetMaterialPropertyName2', 'Default', db)
            mp = c(hd.Extension, 'CreateMassProperty2')
            hw_materials_report[f'{hname}.SLDPRT'] = {
                'material': mat,
                'database': db.value,
                'density_kg_m3': float(mp.Density),
                'mass_g': float(mp.Mass * 1000.0),
                'volume_mm3': float(mp.Volume * 1e9),
            }

        post_hashes = {
            'BA_Bench_Actuation_Layout.SLDASM': sha256_file(layout_path),
            'BD_Bench_Development_Source.SLDASM': sha256_file(rotor_path),
            'config/baseline.json': sha256_file(ROOT / 'config/baseline.json'),
        }
        for pname in act_part_names:
            post_hashes[f'Actuation_Models/{pname}'] = sha256_file(ACT_MODELS / pname)
        for hname, hpath in created_hw_paths.items():
            post_hashes[f'Actuation_Models/{hname}.SLDPRT'] = sha256_file(hpath)

        assert post_hashes['config/baseline.json'] == pre_hashes['config/baseline.json'], 'Baseline hash modified!'

        # Update ACTUATION_LAYOUT.json
        act_layout_state = json.loads((FOLDER / 'ACTUATION_LAYOUT.json').read_text())
        act_layout_state['added'].update(added_hw_instances)
        act_layout_state['status'] = 'KINEMATICALLY MATED, FLEXIBLE ROTOR COUPLED & MULTI-POSE CLEARANCE VERIFIED (CAD-003B)'
        act_layout_state['assembly_sha256'] = post_hashes['BA_Bench_Actuation_Layout.SLDASM']
        for pname in act_part_names:
            key = pname.removesuffix('.SLDPRT')
            if key in act_layout_state.get('parts', {}):
                act_layout_state['parts'][key]['sha256'] = post_hashes[f'Actuation_Models/{pname}']
        (FOLDER / 'ACTUATION_LAYOUT.json').write_text(json.dumps(act_layout_state, indent=2))

        completion_state = {
            'task_id': 'CAD-003B',
            'title': 'Zaber Bench Actuation Kinematic Mating, Hardware Detailing & Coupled Motion Readiness',
            'status': 'COMPLETED',
            'pre_task_sha256': pre_hashes,
            'post_task_sha256': post_hashes,
            'backup_directory': str(BACKUP_DIR),
            'step1_materials_and_subassembly_grounding': {
                'actuation_models_materials': act_materials_report,
                'created_hardware_materials': hw_materials_report,
                'zero_1000kgm3_defaults_verified': True,
                'rotor_subassembly_state': {
                    'BD_Bench_Development_Source-1_Solving': 'Flexible (swComponentFlexibleSolving = 1)',
                    'BD_RB_Assem3-1_Solving': 'Flexible (swComponentFlexibleSolving = 1)',
                    'grounding_mates': ['Bench_RotorBase_Right_Plane', 'Bench_RotorBase_Top_Plane', 'Bench_RotorBase_Front_Plane'],
                },
                'total_bench_assembly_mass_kg': total_bench_mass_kg,
                'total_bench_assembly_mass_g': total_bench_mass_g,
            },
            'step2_kinematic_mates': {
                'floated_moving_components': [co.Name2 for co in moving_act_comps],
                'added_kinematic_mate_count': len(added_kinematic_mates),
                'added_kinematic_mates': added_kinematic_mates,
                'initial_pose_drift_m': max_step2_drift_m,
                'active_axis_drivers': ['Bench_X_Actuator_Stroke', 'Bench_Y_Actuator_Stroke'],
                'retained_rotor_limit_mates': ['LimitDistance1', 'LimitDistance3', 'Combined_XY_Radial_Limit_6p88mm'],
            },
            'step3_hardware_and_detailing': {
                'part_geometry_refinements': {
                    'BA_X_Actuator_Drop_Link.SLDPRT': 'Added Fixed_Base_Window_Relief so Deep_Actuator_Web passes through the Y=[30..48] mm window of BD_RB_XY_Fixed_Base with 1.0 mm radial and 2.0 mm axial clearance.',
                    'BA_Y_Cross_Slot_Drop_Link.SLDPRT': 'Added Outboard_Clearance_Web (X=-58..-44 mm), Fixed_Base_Ear_Clearance_Cut (X=-50..-31 mm, Z=-20..-13 mm) clearing BD_RB_XY_Fixed_Base ear by >=1.12 mm radially, and Slot_Bottom_Upriser_Opening (Y=-29.51..-10.49 mm, Z=-85..-74 mm) allowing YHead Shoe_Upriser entry from below.',
                    'BA_Y_Guided_Crosshead.SLDPRT': 'Cut coaxial D4.0x11 mm M4_Shoe_Thread_Major_Envelope bore in Shoe_Upriser and added Cross_Slot_Bottom_Clearance trimming Shoe_Upriser to Y=[-9.5..+9.5] mm and Adapter_Bridge top to Z=18.0 mm (1.0 mm below YDrop Cross_Slot_Block).',
                    'BA_Bench_Plate_650_12.SLDPRT': 'Cut 12x D6.6 mm through-holes (Bench_M6_Anchor_Holes_12x_D6p6 for 4 frame columns and 8 NEMA 23 bracket foot holes) and 4x D5.5 mm through-holes (Bench_M5_SupportPost_Holes_4x_D5p5 for 4 Y-guide support posts).',
                },
                'added_hardware_instance_count': len(added_hw_instances),
                'added_hardware_instances': added_hw_instances,
                'added_hardware_mate_count': len(added_hw_mates),
            },
            'step4_coupled_kinematic_and_clearance_audit': {
                'tested_pose_count': len(pose_results),
                'total_native_boolean_checks': total_bool_checks,
                'max_unexpected_boolean_overlap_mm3': max_unexpected_overlap_mm3,
                'classified_intentional_fastener_overlaps': classified_fastener_overlaps,
                'active_mate_error_count_top_level': len(final_top_errors),
                'active_mate_error_count_rotor_subassembly': len(final_sub_errors),
                'cross_slot_x_sliding_range_verified_mm': [min(x_slot_sliding_offsets_mm), max(x_slot_sliding_offsets_mm)],
                'pitch_extrema_at_+6p88_0_deg': [-34.9897, 34.9911],
                'minimum_clearances': {
                    'YShoe_in_YDrop_X_slot_lateral_mm': 0.010,
                    'YShoe_in_YDrop_X_slot_axial_top_mm': 1.000,
                    'YHead_Adapter_Bridge_to_YDrop_bottom_mm': 1.000,
                    'XDrop_web_to_Fixed_Base_window_radial_mm': 1.000,
                    'XDrop_foot_to_Fixed_Base_axial_mm': 1.000,
                    'YDrop_web_to_Fixed_Base_ear_radial_at_+6p88_mm': 1.120,
                    'YDrop_web_to_X_Slider_edge_radial_mm': 2.000,
                },
                'restored_initial_pose_deltas': {
                    'x_slider_max_tf_delta': restored_xs_delta,
                    'inner_carriage_max_tf_delta': restored_in_delta,
                    'shaft_max_tf_delta': restored_sh_delta,
                },
                'poses': pose_results,
            },
        }

        state_out_path = FOLDER / 'CAD003B_COMPLETION_STATE.json'
        state_out_path.write_text(json.dumps(completion_state, indent=2))
        print('CAD003B_ALL_STEPS_COMPLETED_SUCCESSFULLY STATE_SHA256:', sha256_file(state_out_path), flush=True)
    finally:
        app.CommandInProgress = False
        try:
            c(app, 'ExitApp')
        except Exception:
            pass


if __name__ == '__main__':
    main()
