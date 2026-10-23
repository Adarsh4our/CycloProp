from cad import *

STATE = TASK / 'COUPLING_INTEGRATION_STATE.json'
d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
shaft = ro['3-Drive_Shaft-1']
ringco = next(co for co in c(d, 'GetComponents', False) if logical(co.Name2).endswith('/4-Outer_Control_Ring-1'))
rt = tf(ringco)
rr = np.array(rt[:9]).reshape(3, 3)
rotation = np.array([rr[0], rr[2], -rr[1]])
output_origin = np.array(rt[9:12]) + np.array([0., 0., .009])
shaft_origin = np.array(tf(shaft)[9:12])
base_origin = np.array(tf(ro['XY_Fixed_Base-1'])[9:12])
input_origin = shaft_origin + np.array([0., 0., .014325])
floating_origin = shaft_origin + np.dot(output_origin - shaft_origin, rotation[0]) * rotation[0]
floating_origin[2] = base_origin[2] + .0437
assert json.loads((TASK / 'COUPLING_INTERFACE_CHANGES.json').read_text())['complete']
if STATE.exists():
    s = json.loads(STATE.read_text())
    assert not s.get('complete'), 'Already integrated; inspect instead of rerunning'
else:
    recovery = TASK / 'Recovery/Before_Coupling_Integration'
    recovery.mkdir(parents=True, exist_ok=True)
    if (recovery / ASSEMBLY.name).exists():
        assert ASSEMBLY.read_bytes() == (recovery / ASSEMBLY.name).read_bytes(), 'Recovery source differs'
        assert len(ro) == 311, 'Unexpected components in recovered source'
        prior = json.loads((TASK / 'Recovery/Direct_Transform_Probe/COUPLING_INTEGRATION_STATE.json').read_text())
        assert np.max(abs(np.array(tf(shaft)) - prior['original_shaft_transform'])) < 1e-7
        assert np.max(abs(np.array(rt) - prior['original_ring_transform'])) < 1e-7
    else:
        assert not c(d, 'GetSaveFlag'), 'Unexpected user changes'
        shutil.copy2(ASSEMBLY, recovery / ASSEMBLY.name)
    s = {'added': {}, 'mates': [], 'backup': str(recovery),
         'original_shaft_transform': tf(shaft), 'original_ring_transform': rt}

def persist():
    STATE.write_text(json.dumps(s, indent=2))

def insert(key, file, position, rot=rotation):
    if key in s['added']:
        co = c(d, 'GetComponentByName', s['added'][key])
        assert co
        return co
    path = OUT / (file + '.SLDPRT')
    getdoc(path)
    activate(d)
    co = c(d, 'AddComponent5', str(path), 0, '', False, '', *map(float, position))
    assert co
    set_transform(co, position, rot)
    s['added'][key] = co.Name2
    persist()
    return co

def rigid(a, b, name):
    if c(d, 'FeatureByName', name):
        return
    lock(d, a, b, name)
    s['mates'].append(name)
    persist()

def plane(a, ap, b, bp, name, gap=0.):
    if c(d, 'FeatureByName', name):
        return
    c(d, 'ClearSelection2', True)
    for ent in [mappedplane(a, ap), mappedplane(b, bp)]:
        entityselect(d, ent)
    e = iref()
    if gap:
        f = c(d, 'AddDistanceMate', 0, False, gap, gap, gap, 0, 0, e)
    else:
        f = c(d, 'AddMate5', 0, 0, False, 0., 0., 0., 0., 0., 0., 0., 0., False, False, 0, e)
    assert f, (name, e.value)
    f.Name = name
    s['mates'].append(name)
    persist()
    print('COUPLING_MATE', name, flush=True)

app.CommandInProgress = True
try:
    output = insert('Output', 'RB_Oldham_Output_PROTOTYPE', output_origin)
    rigid(ringco, output, 'RevB_Oldham_Output_Piloted_Bolt_Attachment')
    driver = insert('Input', 'RB_Oldham_Input_PROTOTYPE', input_origin)
    rigid(shaft, driver, 'RevB_Oldham_Input_D6_Bore_D2_Crosspin')
    floating = insert('Floating', 'RB_Oldham_Floating_Disk_PROTOTYPE', floating_origin)
    for i in range(4):
        a = math.pi / 8 + i * math.pi / 2
        local = np.array([.03 * math.cos(a), .03 * math.sin(a), -.009])
        point = local @ rotation + output_origin
        co = insert('Pilot' + str(i), 'RB_Oldham_Output_Pilot_Standoff_L9', point)
        rigid(output, co, 'RevB_Oldham_Output_Pilot' + str(i))
        point = np.array([local[0], local[1], .0039]) @ rotation + output_origin
        co = insert('Screw' + str(i), 'RB_M2x18_Oldham_CSK_Screw_REFERENCE', point)
        rigid(output, co, 'RevB_Oldham_Output_Screw' + str(i))
    pinrot = np.array([[0., 0., -1.], [0., 1., 0.], [1., 0., 0.]]) @ rotation
    co = insert('InputPin', 'RB_DIN1481_D2x14_INSTALLED_REFERENCE', np.array([0., 0., .0086]) @ rotation + input_origin, pinrot)
    rigid(driver, co, 'RevB_Oldham_Input_Pin_Installed')
    plane(output, 'Right Plane', floating, 'Right Plane', 'RevB_Oldham_Output_Y_Slide_Centre')
    plane(output, 'Front Plane', floating, 'Front Plane', 'RevB_Oldham_Floating_Axial_Station', .0042)
    hold = c(d, 'FeatureByName', 'RevB_SETUP_Ring_Angle')
    assert hold
    if not c(hold, 'IsSuppressed'):
        assert c(hold, 'SetSuppression2', 0, 1, None)
    plane(driver, 'Top Plane', floating, 'Top Plane', 'RevB_Oldham_Input_X_Slide_Centre')
    assert c(d, 'ForceRebuild3', False)
    relevant = [c(d, 'FeatureByName', name) for name in s['mates']]
    errs = errors(relevant)
    s['mate_errors'] = errs
    persist()
    assert not errs, errs
    actual = tf(floating)
    assert np.max(abs(np.array(actual[9:12]) - floating_origin)) < 1e-7, (actual, floating_origin)
    save(d)
    s.update({'complete': True, 'status': 'Physical pin/bolt geometry and nominal sliding constraints installed; motion check pending',
              'ring_setup_hold_suppressed': True, 'rotor_setup_hold_active': True,
              'nominal_slot_side_clearance_mm': .05, 'nominal_axial_face_gap_mm': .2,
              'floating_transform': actual, 'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()})
    persist()
    print('COUPLING_INTEGRATED', flush=True)
finally:
    app.CommandInProgress = False
