from cad import *

d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
shaft = c(ro['3-Drive_Shaft-1'], 'GetModelDoc2')
pedestal = getdoc(OUT / 'RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT')
records = json.loads(BUILD_LOG.read_text())
recovery = TASK / 'Recovery/Before_Frame_Interfaces'
recovery.mkdir(parents=True, exist_ok=True)

app.CommandInProgress = True
try:
    f = c(pedestal, 'FeatureByName', 'Base_Three_M2_Blind_Thread_Major_Envelopes')
    if f:
        p = Path(c(pedestal, 'GetPathName'))
        assert not (recovery / p.name).exists()
        shutil.copy2(p, recovery / p.name)
        fd = c(f, 'GetDefinition')
        assert c(fd, 'AccessSelections', pedestal, NULL)
        c(fd, 'SetDepth', True, .00401)
        assert c(f, 'ModifyDefinition', fd, pedestal, NULL)
        f.Name = 'Base_Three_M2_Through_Thread_Major_Envelopes'
        inspect_part(pedestal)
        save(pedestal)
        records[p.stem].update(inspect_part(pedestal))
        records[p.stem]['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
        records[p.stem]['mass_g'] = c(pedestal.Extension, 'CreateMassProperty2').Mass * 1000
        records[p.stem]['base_thread_revision'] = 'M2x0.4 THROUGH 4mm flange. M2x8 plus0.3washer gives3.7mm nominal engagement and0.3mm recess.'
        BUILD_LOG.write_text(json.dumps(records, indent=2))
    if c(shaft, 'FeatureByName', 'RevB_Lower_Shaft_Nose_Clearance_2mm') is None:
        p = Path(c(shaft, 'GetPathName'))
        assert p.parent == OUT
        assert not (recovery / p.name).exists()
        shutil.copy2(p, recovery / p.name)
        face_circles(shaft, 2, 0., [(0., 0., 0.)], .0031)
        cut(shaft, 'RevB_Lower_Shaft_Nose_Clearance_2mm', .002)
        assert abs(c(c(shaft, 'GetBodies2', 0, False)[0], 'GetBodyBox')[2] - .002) < 1e-8
        inspect_part(shaft)
        save(shaft)
    activate(d)
    assert c(d, 'ForceRebuild3', False)
    errors_now = errors(active_mates(d))
    assert not errors_now, errors_now
    save(d)
    report = {'status': 'implemented; native rebuild/mates checked at construction pose',
              'shaft_nose_removed_mm': 2., 'shaft_solid_axial_extent_mm': [2., 275.],
              'shaft_assembly_origin_changed': False, 'pedestal_head_bottom_base_mm': 32.8,
              'pedestal_floor_top_base_mm': 35., 'shaft_nose_base_mm': 35.575,
              'nominal_nose_clearance_mm': .575, 'pedestal_base_threads': '3xM2x0.4 through4mm flange',
              'mate_errors': errors_now, 'recovery': str(recovery)}
    (TASK / 'FRAME_INTERFACE_CHANGES.json').write_text(json.dumps(report, indent=2))
    print('FRAME_INTERFACES_SAVED', flush=True)
finally:
    app.CommandInProgress = False
