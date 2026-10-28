#!/usr/bin/env python3
"""
Interactive Live 3D SolidWorks Viewport Motion Player for BA_Bench_Actuation_Layout.SLDASM.
Spins the rotor, blades, pitch links, and Oldham coupling live in the SolidWorks 2026
viewport at e = (+6.88, 0.0) mm and then restores the exact initial saved pose.
"""

import json
import math
import sys
from pathlib import Path
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

import cad
from cad import c, app, NULL

BENCH_DIR = REPO_ROOT / "CAD" / "Design_Completion" / "Bench_Prototype"
ROTOR_ASM_PATH = BENCH_DIR / "Bench_Rotor" / "BD_Bench_Development_Source.SLDASM"
TOP_ASM_PATH = BENCH_DIR / "BA_Bench_Actuation_Layout.SLDASM"


def main():
    app.Visible = True
    app.CommandInProgress = False
    try:
        c(app, "DocumentVisible", True, 1)
        c(app, "DocumentVisible", True, 2)
    except Exception:
        pass

    rotor_doc = cad.getdoc(ROTOR_ASM_PATH, 2)
    asm = cad.getdoc(TOP_ASM_PATH, 2)
    cad.activate(asm)
    assert c(asm, "ForceRebuild3", False)
    try:
        c(asm, "ViewZoomtofit2")
    except Exception:
        pass

    inspect = json.loads((BENCH_DIR / "ACTUATION_START_INSPECTION.json").read_text())
    xp0_m = next(r for r in inspect if "X_Slider_Drive_Tab_" in r["name"])["pos_mm"][0] / 1000.0
    yp1_m = next(r for r in inspect if "Y_Carriage_Drive_Tab_" in r["name"])["pos_mm"][1] / 1000.0

    all_comps = [co for co in c(asm, "GetComponents", False) if not c(co, "IsSuppressed")]
    all_comps_map = {co.Name2: co for co in all_comps}
    fixed_base = all_comps_map["BD_Bench_Development_Source-1/BD_RB_XY_Fixed_Base-1"]
    x_slider = all_comps_map["BD_Bench_Development_Source-1/BD_RB_Intermediate_X_Slider-1"]
    inner = all_comps_map["BD_Bench_Development_Source-1/BD_RB_Assem3-1/BD_RB_4-Inner_Carriage_Plate-1"]
    shaft = next(co for co in all_comps if Path(c(co, "GetPathName") or "").name == "BD_RB_3-Drive_Shaft.SLDPRT")
    origin = np.array(cad.tf(fixed_base)[9:12])

    initial_shaft_tf = cad.tf(shaft)
    initial_phi = math.atan2(initial_shaft_tf[1], initial_shaft_tf[0])
    mx = c(asm, "FeatureByName", "Bench_X_Actuator_Stroke")
    my = c(asm, "FeatureByName", "Bench_Y_Actuator_Stroke")
    angle_param = c(rotor_doc, "Parameter", "D1@RevB_SETUP_Rotor_Angle")

    def _drive_single_axis(mate_feat, comp_to_check, coord_idx, target_m, zero_offset_m):
        stroke = target_m - zero_offset_m
        for flip in [stroke < 0, not (stroke < 0)]:
            fd = c(mate_feat, "GetDefinition")
            fd.Distance = abs(stroke)
            fd.FlipDimension = bool(flip)
            assert c(mate_feat, "ModifyDefinition", fd, asm, NULL)
            assert c(asm, "ForceRebuild3", False)
            actual = cad.tf(comp_to_check)[9 + coord_idx] - origin[coord_idx]
            if abs(actual - target_m) < 1e-5:
                return

    def set_zaber_xy_eccentricity(tx_m, ty_m):
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

    def set_coupled_shaft_angle(target_phi: float):
        target_phi %= 2.0 * math.pi
        for cand in [target_phi, (2.0 * math.pi - target_phi) % (2.0 * math.pi)]:
            angle_param.SystemValue = float(cand)
            assert c(asm, "ForceRebuild3", False)
            st = cad.tf(shaft)
            actual = math.atan2(st[1], st[0])
            err = (actual - target_phi + math.pi) % (2.0 * math.pi) - math.pi
            if abs(err) < math.radians(0.001):
                return

    try:
        print("Playing 2 full 360-deg live revolutions in SolidWorks 2026 at e = (+6.88, 0.0) mm...", flush=True)
        set_coupled_shaft_angle(initial_phi + math.radians(270.0))
        set_zaber_xy_eccentricity(0.00688, 0.0)
        for rev in range(2):
            for step_i in range(72):
                inc_deg = step_i * 5.0
                set_coupled_shaft_angle(initial_phi + math.radians(inc_deg))
            print(f"  Completed live revolution {rev + 1}/2", flush=True)
    finally:
        set_coupled_shaft_angle(initial_phi + math.radians(270.0))
        set_zaber_xy_eccentricity(xp0_m, yp1_m)
        set_coupled_shaft_angle(initial_phi)
        assert c(asm, "ForceRebuild3", False)
        print("Restored exact initial pose in SolidWorks 2026.", flush=True)


if __name__ == "__main__":
    main()
