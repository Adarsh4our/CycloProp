from cad import *
import xml.etree.ElementTree as ET

STATE = TASK / 'MATERIAL_CORRECTION_STATE.json'
resume = '--resume-inspected' in sys.argv
assert not STATE.exists() or resume, 'Inspect existing material correction state; do not blindly repeat'
d = getdoc(ASSEMBLY, 2)
activate(d)
recovery = TASK / 'Recovery/Before_Material_Reconciliation'
recovery.mkdir(parents=True, exist_ok=True)
if not resume:
    assert not (recovery / ASSEMBLY.name).exists()
    assert c(d.Extension, 'SaveAs', str(recovery / ASSEMBLY.name), 0, 3, NULL, iref(), iref())
custom = Path(r'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\custom materials\CycloProp_Prototype_Densities.sldmat')
assert custom.exists()

assignments = {
    'RB_Endplate_Hub_Interface_RevA.SLDPRT': (str(custom), 'G10_FR4_1850_DENSITY_ONLY_PROVISIONAL', 'Rev3 specifies1.85g/cm3 G10; replaces18g target override with volume-based mass. Laminate/strength remain unverified.'),
    'RB_4-Inner_Carriage_Plate.SLDPRT': (MAT_DB, '7075-T6 (SN)', 'Rev3 inner-carriage7075 intent; provisional machining material, not supplied certificate.'),
    'RB_4-Outer_Control_Ring.SLDPRT': (MAT_DB, '7075-T6 (SN)', 'Existing7075 intent retained using installed library; removes9g target override.'),
    'RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE.SLDPRT': (MAT_DB, '7075-T6 (SN)', 'Existing7075 arm intent retained using installed library; removes2.5g target override.'),
    'RB_XY_Fixed_Base.SLDPRT': (MAT_DB, '6061-T6 (SS)', 'Selected provisional bench-prototype aluminum, consistent with the new cage; strength/fatigue not released.'),
    'RB_Intermediate_X_Slider.SLDPRT': (MAT_DB, '6061-T6 (SS)', 'Selected provisional bench-prototype aluminum; actual supplied stock/strength remain unverified.'),
    'RB_Shaft_Drive_Hub_RevA.SLDPRT': (MAT_DB, '7075-T6 (SN)', 'Selected provisional aluminum for machined pinned hub; does not resolve supplied material certification.'),
    'RB_Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE.SLDPRT': (str(custom), 'CFRP_TUBE_1550_DENSITY_ONLY_PROVISIONAL', 'Documented CFRP density used for tube mass only. Fiber architecture, modulus, bond and supplied dimensions unverified.'),
    'RB_Ball_Insert_D5_Bore2p1_H3_REFERENCE.SLDPRT': (MAT_DB, 'AISI 4340 Steel, normalized', 'Steel density proxy for custom ball insert; finish/hardness/grade and wear require release.')}
parts = {}
for co in c(d, 'GetComponents', False):
    if c(co, 'GetSuppression') == 0:
        continue
    part = c(co, 'GetModelDoc2')
    if part and c(part, 'GetType') == 1:
        path = Path(c(co, 'GetPathName'))
        if path.name in assignments:
            assert path.parent == OUT, path
            assert co.ReferencedConfiguration == 'Default', (path, co.ReferencedConfiguration)
            parts[path.name] = part
assert set(parts) == set(assignments), ('Missing targeted active references', set(assignments) - set(parts))
s = {'status': 'IN PROGRESS', 'backup': str(recovery), 'parts': {}, 'custom_density_database': str(custom),
     'limits': ['Only listed parts/configurations corrected. Other unassigned parts and purchased-envelope proxies remain identified in revised BOM.',
                'No actual hardware mass, certified material grade or strength approval is inferred.',
                'Blade monolithic solid remains a geometry proxy without a composite manufacturing/material definition.']}
if resume:
    s=json.loads(STATE.read_text())
    assert not s.get('complete')
    for name,row in s['parts'].items():
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==row['sha256'],('Changed saved material part',name)
s['custom_density_database']=str(custom)
STATE.write_text(json.dumps(s, indent=2))
app.CommandInProgress = True
try:
    for name, part in parts.items():
        path = OUT / name
        if name in s['parts']:
            print('PRESERVED_PREVIOUS_MATERIAL_CORRECTION',name,flush=True)
            continue
        dirty_before = bool(c(part, 'GetSaveFlag'))
        if not (recovery / name).exists():
            shutil.copy2(path, recovery / name)
        if dirty_before:
            live = recovery / ('LIVE_BEFORE_' + name)
            if not live.exists():
                assert c(part.Extension, 'SaveAs', str(live), 0, 3, NULL, iref(), iref())
        mp = c(part.Extension, 'CreateMassProperty2')
        options = c(mp, 'GetOverrideOptions')
        if resume:
            inspect_path = recovery / ('INSPECT_ORIGINAL_' + name)
            if not inspect_path.exists(): shutil.copy2(recovery / name, inspect_path)
            assert hashlib.sha256(inspect_path.read_bytes()).hexdigest() == hashlib.sha256((recovery / name).read_bytes()).hexdigest()
            before_part = getdoc(inspect_path, readonly=True)
            assert Path(c(before_part, 'GetPathName')) == inspect_path
        else:
            before_part = part
        before_mp = c(before_part.Extension, 'CreateMassProperty2')
        before_options = c(before_mp, 'GetOverrideOptions')
        old_db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
        old_material = c(before_part, 'GetMaterialPropertyName2', 'Default', old_db)
        before = {'dirty_flag_before': dirty_before, 'material': old_material, 'material_database': old_db.value, 'mass_g': before_mp.Mass * 1000, 'mass_override': before_options.OverrideMass,
                  'sha256': hashlib.sha256((recovery / name).read_bytes()).hexdigest()}
        s.setdefault('attempts', {})[name] = {'before': before}
        STATE.write_text(json.dumps(s, indent=2))
        if options.OverrideMass:
            options.OverrideMass = False
            assert c(mp, 'SetOverrideOptions', options, 1, None)
        database, material, reason = assignments[name]
        c(part, 'SetMaterialPropertyName2', 'Default', database, material)
        db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
        assert c(part, 'GetMaterialPropertyName2', 'Default', db) == material
        mp = c(part.Extension, 'CreateMassProperty2')
        assert not c(mp, 'GetOverrideOptions').OverrideMass
        assert mp.Mass > 0 and mp.Volume > 0
        expected_density = 1850. if material.startswith('G10_') else 1550. if material.startswith('CFRP_') else 2810. if material.startswith('7075') else 2700. if material.startswith('6061') else 7850.
        effective_density = mp.Mass / mp.Volume
        assert abs(effective_density - expected_density) < .01, (name, effective_density, expected_density)
        c(part.Extension.CustomPropertyManager(''), 'Add3', 'MATERIAL_BASIS', 30, reason, 2)
        c(part.Extension.CustomPropertyManager(''), 'Add3', 'MASS_STATUS', 30, 'VOLUME-BASED PROVISIONAL CAD MASS; NOT MEASURED HARDWARE MASS', 2)
        save(part)
        s['parts'][name] = {'before': before, 'after_mass_g': mp.Mass * 1000, 'mass_override': False,
                            'effective_density_kg_m3': effective_density, 'configuration': 'Default', 'assigned_material': material, 'database_readback': db.value, 'reason': reason,
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        STATE.write_text(json.dumps(s, indent=2))
        print('MATERIAL_MASS_CORRECTED', name, round(mp.Mass * 1000, 3), flush=True)
    activate(d)
    assert c(d, 'ForceRebuild3', False)
    save(d)
    s['complete'] = True
    s['status'] = 'Listed native assignments/target overrides corrected; full register and physical validation remain separate'
    s['assembly_sha256'] = hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()
    STATE.write_text(json.dumps(s, indent=2))
finally:
    app.CommandInProgress = False
