from cad import *

recovery = TASK / 'Recovery/Before_Cartridge_Axial_Refinement'
recovery.mkdir(parents=True, exist_ok=True)
records = json.loads(BUILD_LOG.read_text())
def exact_z(part):
    body = c(part, 'GetBodies2', 0, False)[0]
    result = []
    for sign in [-1., 1.]:
        xyz = [win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.) for _ in range(3)]
        assert c(body, 'GetExtremePoint', 0., 0., sign, *xyz)
        result.append(xyz[2].value * 1000)
    return result
changes = {
    'RB_Blade_Bearing_Cartridge_PROTOTYPE': [
        ('D10_Pilot_And_M10x0p5_Thread_Envelope', -1., 1.5),
        ('Outer_Race_Inner_Shoulder_ID7p4', 1.5, 1.8),
        ('Flanged_Race_Pocket_D9p6', -2.5, -1.6),
        ('M14x0p5_Bearing_Cap_Boss', -1.6, -1.)],
    'RB_F693ZZ_3x8x4_FLANGE9p5x0p9_ENVELOPE': [
        ('F693ZZ_External_Envelope_3x8x4', -2.5, 1.5), ('Flange_9p5x0p9', -2.5, -1.6)],
    'RB_Blade_Bearing_Outer_Cap_PROTOTYPE': [
        ('Outer_Flange_Contact_Annulus_ID8p2', -3., -2.5), ('M14x0p5_Internal_Thread_Envelope', -2.5, -1.3)],
    'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE': []}

app.CommandInProgress = True
try:
    for name, features in changes.items():
        p = OUT / (name + '.SLDPRT')
        assert hashlib.sha256(p.read_bytes()).hexdigest() == records[name]['sha256']
        if records[name].get('axial_refinement'):
            continue
        if (recovery / p.name).exists():
            assert p.read_bytes() == (recovery / p.name).read_bytes(), 'Recovery source differs'
        else:
            shutil.copy2(p, recovery / p.name)
        part = getdoc(p)
        activate(part)
        for feature, z0, z1 in features:
            f = c(part, 'FeatureByName', feature)
            assert f
            fd = c(f, 'GetDefinition')
            assert c(fd, 'AccessSelections', part, NULL)
            fd.FromOffsetDistance = abs(z0) / 1000
            fd.FromOffsetReverse = z0 < 0
            c(fd, 'SetDepth', True, (z1 - z0) / 1000)
            assert c(f, 'ModifyDefinition', fd, part, NULL), feature
        if name == 'RB_Blade_Bearing_Cartridge_PROTOTYPE':
            face_circles(part, 2, .0018, [(-.006, 0., .0018), (.006, 0., .0018)], .0006)
            cut(part, 'Two_Pin_Wrench_Holes_D1p2', .000301)
        elif name == 'RB_Blade_Bearing_Outer_Cap_PROTOTYPE':
            face_circles(part, 2, -.003, [(-.0071, 0., -.003), (.0071, 0., -.003)], .0006)
            cut(part, 'Two_Pin_Wrench_Holes_D1p2', .0005001)
        elif name == 'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE' and not c(part, 'FeatureByName', 'Two_Pin_Wrench_Holes_D1p2'):
            face_circles(part, 2, 0., [(-.006, 0., 0.), (.006, 0., 0.)], .0006)
            cut(part, 'Two_Pin_Wrench_Holes_D1p2', .001001)
        if name == 'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE':
            f = c(part, 'FeatureByName', 'Two_Pin_Wrench_Holes_D1p2')
            fd = c(f, 'GetDefinition')
            assert c(fd, 'AccessSelections', part, NULL)
            c(fd, 'SetEndCondition', True, 1)
            assert c(f, 'ModifyDefinition', fd, part, NULL)
        assert c(part, 'EditRebuild3')
        evidence = inspect_part(part)
        bounds = {'RB_Blade_Bearing_Cartridge_PROTOTYPE': [-2.5, 1.8],
                  'RB_F693ZZ_3x8x4_FLANGE9p5x0p9_ENVELOPE': [-2.5, 1.5],
                  'RB_Blade_Bearing_Outer_Cap_PROTOTYPE': [-3., -1.3],
                  'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE': [-1., 0.]}[name]
        evidence['exact_axial_extent_mm'] = exact_z(part)
        assert np.max(abs(np.array(evidence['exact_axial_extent_mm']) - bounds)) < 1e-5, (name, evidence, bounds)
        c(part.Extension.CustomPropertyManager(''), 'Add3', 'AXIAL_REFINEMENT', 30,
          'Bearing inboard faceZ1.5, outer flange faceZ-2.5; H0.3 inner-ring spacer. Selected to increase mechanism arm/cap nominal gap to0.85mm.', 2)
        save(part)
        records[name].update(evidence)
        records[name]['axial_refinement'] = 'Implemented before integration; bearing moved inward0.5mm and cap shortened accordingly. Pin-wrench holes added to custom retention parts.'
        records[name]['mass_g'] = c(part.Extension, 'CreateMassProperty2').Mass * 1000
        records[name]['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
        BUILD_LOG.write_text(json.dumps(records, indent=2))
        print('CARTRIDGE_AXIAL_REFINED', name, flush=True)
finally:
    app.CommandInProgress = False
