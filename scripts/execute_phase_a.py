import win32com.client
import os
import sys

def run_phase_a():
    print("=== CYCLOPROP TASK 2: KINEMATIC & CONSTRAINT FIX ===", flush=True)
    sw = win32com.client.Dispatch('SldWorks.Application')
    sw.Visible = True
    sw.UserControl = True
    print(f"Connected to SolidWorks Rev: {sw.RevisionNumber}", flush=True)

    assem_path = os.path.abspath(r"CAD\Assem9.SLDASM")
    print(f"Opening assembly: {assem_path}...", flush=True)
    doc = sw.OpenDoc(assem_path, 2) # swDocASSEMBLY = 2
    if not doc:
        print("Error: Could not open assembly!", flush=True)
        return False

    title = doc.GetTitle
    if callable(title): title = title()
    print(f"Active Document: {title}", flush=True)

    comps = doc.GetComponents(True)
    print(f"Total top-level components: {len(comps)}", flush=True)

    # 1. Locate 2-Endplate_Hub-1
    target = None
    for c in comps:
        name = c.Name2
        if callable(name): name = name()
        if "2-Endplate_Hub-1" in name:
            target = c
            break

    if not target:
        print("Error: 2-Endplate_Hub-1 not found!", flush=True)
        return False

    is_fixed_before = target.IsFixed
    if callable(is_fixed_before): is_fixed_before = is_fixed_before()
    print(f"Component: {target.Name2} | Fixed before: {is_fixed_before}", flush=True)

    if is_fixed_before:
        print("Unfixing 2-Endplate_Hub-1...", flush=True)
        sel_ok = target.Select2(False, 0)
        print(f" - Select2: {sel_ok}", flush=True)
        doc.UnfixComponent()
        is_fixed_after = target.IsFixed
        if callable(is_fixed_after): is_fixed_after = is_fixed_after()
        print(f" - Fixed after: {is_fixed_after}", flush=True)
    else:
        print("2-Endplate_Hub-1 is already floating!", flush=True)

    # 2. Rebuild
    print("Rebuilding model (EditRebuild3)...", flush=True)
    rb = doc.EditRebuild3
    if callable(rb): rb = rb()
    print(f"Rebuild result: {rb}", flush=True)

    # 3. Save
    print("Saving assembly (Save2 silent)...", flush=True)
    try:
        saved = doc.Save2(True)
        print(f"Save2 returned: {saved}", flush=True)
    except Exception as e:
        print(f"Save2 exception: {e}", flush=True)
        try:
            doc.Save()
            print("Save() succeeded", flush=True)
        except Exception as e2:
            print(f"Save() exception: {e2}", flush=True)

    # 4. Audit all components
    print("\n=== VERIFYING COMPONENT STATES ===", flush=True)
    comps = doc.GetComponents(True)
    all_ok = True
    for i, c in enumerate(comps):
        name = c.Name2
        if callable(name): name = name()
        is_fix = c.IsFixed
        if callable(is_fix): is_fix = is_fix()
        
        status = "FIXED" if is_fix else "FLOATING"
        # Only 6-Mounting_Chassis_Frame should be fixed
        if "6-Mounting_Chassis_Frame" in name:
            expected = True
        else:
            expected = False
            
        check = "OK" if is_fix == expected else "MISMATCH"
        if is_fix != expected: all_ok = False
        print(f" [{i:02d}] {name:35s} : {status:8s} (Expected: {'FIXED' if expected else 'FLOATING'}) -> {check}", flush=True)

    print(f"\nConstraint Status: {'ALL CONSTRAINTS VERIFIED OK!' if all_ok else 'SOME CONSTRAINTS NEED ATTENTION'}", flush=True)

    # 5. Mass Properties
    print("\n=== EXTRACTING MASS PROPERTIES ===", flush=True)
    try:
        ext = doc.Extension
        mp = ext.CreateMassProperty()
        if mp:
            mass_kg = mp.Mass
            if callable(mass_kg): mass_kg = mass_kg()
            mass_g = mass_kg * 1000.0
            
            cog = mp.CenterOfMass
            if callable(cog): cog = cog()
            
            print(f"Total Assembly Mass: {mass_g:.2f} g (Target: <= 312.0 g)", flush=True)
            if cog:
                cog_x = cog[0] * 1000.0
                cog_y = cog[1] * 1000.0
                cog_z = cog[2] * 1000.0
                print(f"Center of Mass (X, Y, Z): ({cog_x:.2f}, {cog_y:.2f}, {cog_z:.2f}) mm", flush=True)
                print(f"Target Z COG: ~120.00 mm (Mid-span of 220mm blades)", flush=True)
    except Exception as e:
        print(f"Mass property extraction error: {e}", flush=True)

    print("\nPhase A Complete!", flush=True)
    return True

if __name__ == '__main__':
    run_phase_a()
