from cad import *

STATE = TASK / 'COUPLING_INTERFACE_CHANGES.json'
d = getdoc(ASSEMBLY, 2)
activate(d)
assert not c(d, 'GetSaveFlag'), 'Preserve unexpected unsaved assembly work before proceeding'
ro = roots(d)
shaft = c(ro['3-Drive_Shaft-1'], 'GetModelDoc2')
ringco = next(co for co in c(d, 'GetComponents', False) if logical(co.Name2).endswith('/4-Outer_Control_Ring-1'))
receiver = c(ringco, 'GetModelDoc2')
recovery = TASK / 'Recovery/Before_Coupling_Interfaces'
recovery.mkdir(parents=True, exist_ok=True)
s = json.loads(STATE.read_text()) if STATE.exists() else {'parts': {}, 'ring_wall_probes': []}
angles = [math.pi / 8 + i * math.pi / 2 for i in range(4)]
points = [(.03 * math.cos(a), 0., .03 * math.sin(a)) for a in angles]

def persist():
    STATE.write_text(json.dumps(s, indent=2))

def protect(part):
    path = Path(c(part, 'GetPathName'))
    assert path.parent == OUT, path
    if path.name not in s['parts']:
        assert not c(part, 'GetSaveFlag'), path
        assert not (recovery / path.name).exists(), path
        shutil.copy2(path, recovery / path.name)
        s['parts'][path.name] = {'before_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        persist()
    return path

app.CommandInProgress = True
try:
    protect(receiver)
    if not c(receiver, 'FeatureByName', 'RevB_Oldham_Four_M2_Blind_Thread_Major'):
        body = c(receiver, 'GetBodies2', 0, False)[0]
        for point in points:
            tool = c(c(app, 'GetModeler'), 'CreateBodyFromCyl', array(list(point) + [0., 1., 0., .0025, .0058]))
            hits = c(c(body, 'Copy'), 'Operations2', 15901, tool, iref()) or []
            volume = sum(c(b, 'GetMassProperties', 1.)[3] for b in hits)
            expected = math.pi * .0025 ** 2 * .0058
            assert abs(volume - expected) < 1e-12, ('Insufficient solid ring wall', point, volume, expected)
            s['ring_wall_probes'].append({'centre_m': point, 'solid_cylinder_D5_depth5p8_mm3': volume * 1e9})
        persist()
        face_circles(receiver, 1, 0., points, .001)
        cut(receiver, 'RevB_Oldham_Four_M2_Blind_Thread_Major', .0058)
    if not c(receiver, 'FeatureByName', 'RevB_Oldham_Four_D3p02_Pilot_Pockets'):
        face_circles(receiver, 1, 0., points, .00151)
        cut(receiver, 'RevB_Oldham_Four_D3p02_Pilot_Pockets', .0011)
    inspect_part(receiver)
    save(receiver)
    path = Path(c(receiver, 'GetPathName'))
    s['parts'][path.name].update({'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **inspect_part(receiver)})
    persist()
    protect(shaft)
    if not c(shaft, 'FeatureByName', 'RevB_Oldham_D2_Drive_Pin_Clocked_Hole'):
        activate(shaft)
        a = math.radians(164.17461441081947)
        u = np.array([math.cos(a), math.sin(a), 0.])
        start = np.array([0., 0., .022925]) - .008 * u
        tool = c(c(app, 'GetModeler'), 'CreateBodyFromCyl', array(start.tolist() + u.tolist() + [.001, .016]))
        assert tool
        f = c(shaft, 'CreateFeatureFromBody3', tool, False, 1)
        assert f
        f.Name = 'RevB_Oldham_Crosspin_Cutting_Tool'
        bodies = sorted(c(shaft, 'GetBodies2', 0, False), key=lambda b: c(b, 'GetMassProperties', 1.)[3])
        assert len(bodies) == 2
        f = c(shaft.FeatureManager, 'InsertCombineFeature', 15902, bodies[-1], array([bodies[0]], pythoncom.VT_DISPATCH))
        assert f
        f.Name = 'RevB_Oldham_D2_Drive_Pin_Clocked_Hole'
    assert c(shaft, 'EditRebuild3')
    inspect_part(shaft)
    save(shaft)
    path = Path(c(shaft, 'GetPathName'))
    s['parts'][path.name].update({'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **inspect_part(shaft)})
    activate(d)
    assert c(d, 'ForceRebuild3', False)
    save(d)
    s.update({'complete': True, 'shaft_crosspin_local_z_mm': 22.925, 'shaft_crosspin_clock_deg': 164.17461441081947,
              'ring_hole_PCD_mm': 60., 'ring_angles_deg': [22.5 + 90 * i for i in range(4)],
              'ring_thread': 'M2x0.4; CAD major diameter envelope; usable engagement4mm below pilot',
              'ring_pilot': 'D3.02 depth1.1 nominal; fit/tolerance release pending', 'recovery': str(recovery)})
    persist()
    print('COUPLING_INTERFACES_IMPLEMENTED', flush=True)
finally:
    app.CommandInProgress = False
