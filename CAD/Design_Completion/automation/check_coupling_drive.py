from cad import *

state = json.loads((TASK / 'COUPLING_INTEGRATION_STATE.json').read_text())
assert state['complete']
d = getdoc(ASSEMBLY, 2)
activate(d)
recovery = TASK / 'Recovery/Before_Native_Drag_Check'
recovery.mkdir(parents=True, exist_ok=True)
if not (recovery / ASSEMBLY.name).exists():
    shutil.copy2(ASSEMBLY, recovery / ASSEMBLY.name)
ro = roots(d)
shaft = ro['3-Drive_Shaft-1']
ringco = next(co for co in c(d, 'GetComponents', False) if logical(co.Name2).endswith('/4-Outer_Control_Ring-1'))
floating = c(d, 'GetComponentByName', state['added']['Floating'])
driver = c(d, 'GetComponentByName', state['added']['Input'])
receiver = c(d, 'GetComponentByName', state['added']['Output'])
hold = c(d, 'FeatureByName', 'RevB_SETUP_Rotor_Angle')
original = tf(shaft)
maps = json.loads((TASK / 'REV_B_STATE.json').read_text())['maps']
rows = []
CHECK_PATH = TASK / 'COUPLING_DRIVE_CHECK.json'
wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
initial_phi = math.atan2(original[1], original[0])
phase = math.radians(164.17461441081947)
result = {'scope': 'Shaft alone driven using IDragOperator relaxation; ring not independently positioned. Construction XY fixed.',
          'poses': rows, 'thresholds': {'angle_deg': .001, 'joint_position_mm': .001, 'rod_length_mm': .001},
          'excluded': ['continuous collision clearance', 'loaded/contact backlash behavior', 'wear/thermal/dynamic rating']}

def measure(deg):
    st, rt, it, ot, ft = [tf(co) for co in [shaft, ringco, driver, receiver, floating]]
    phi = math.atan2(st[1], st[0])
    ring_angle = math.atan2(rt[1], rt[0])
    phase_error = math.degrees(wrap(ring_angle - phi - phase))
    coupling_rotation_error = max(abs(np.array(it[:9]) - ot[:9]))
    R = np.array(ot[:9]).reshape(3, 3)
    delta_output = (np.array(ft[9:12]) - ot[9:12]) @ R.T
    delta_input = (np.array(ft[9:12]) - it[9:12]) @ R.T
    links = []
    for key, mapping in maps.items():
        a = world(ro[mapping['ArmBall']], [0., 0., 0.])
        b = world(ro[mapping['RingBall']], [0., 0., 0.])
        links.append({'link': key, 'centre_distance_mm': float(np.linalg.norm(a - b) * 1000),
                      'axial_error_mm': float((a[2] - b[2]) * 1000),
                      'socket_errors_mm': [float(np.linalg.norm(world(ro[mapping[k]], [0., 0., 0.]) - p) * 1000)
                                           for k, p in [('ArmSocket', a), ('RingSocket', b)]]})
    pitches = []
    for n in range(1, 5):
        co = ro['Part1-' + str(n)]
        t = tf(co)
        pivot = world(co, [.0095, 0., 0.])
        radial = pivot - np.array(st[9:12])
        # Blade +X is leading-to-trailing chord; it opposes the arm's +Y datum.
        pitch = math.degrees(wrap(math.atan2(t[1], t[0]) - math.atan2(radial[1], radial[0]) - math.pi / 2))
        pitches.append(pitch)
    row = {'shaft_increment_deg': deg, 'shaft_angle_deg': math.degrees(phi), 'ring_phase_error_deg': phase_error,
           'shaft_drive_error_deg': math.degrees(wrap(phi - initial_phi - math.radians(deg))),
           'coupling_rotation_error': float(coupling_rotation_error),
           'output_slide_error_mm': float(delta_output[0] * 1000),
           'input_slide_error_mm': float(delta_input[1] * 1000),
           'floating_axial_error_mm': float((delta_output[2] - .0042) * 1000), 'links': links, 'blade_pitch_deg': pitches}
    rows.append(row)
    CHECK_PATH.write_text(json.dumps(result, indent=2))
    assert abs(phase_error) < .001, row
    assert abs(row['shaft_drive_error_deg']) < .001, row
    assert coupling_rotation_error < 1e-5, row
    assert max(abs(row[k]) for k in ['output_slide_error_mm', 'input_slide_error_mm', 'floating_axial_error_mm']) < .001, row
    for link in links:
        assert abs(link['centre_distance_mm'] - 56.52665325007647) < .001, link
        assert abs(link['axial_error_mm']) < .001 and max(link['socket_errors_mm']) < .001, link
    assert max(abs(x) for x in pitches) < 35.01, row
    print('PHYSICAL_DRIVE_POSE', deg, 'PHASE_ERROR_DEG', round(phase_error, 7), 'PITCHES', [round(p, 3) for p in pitches], flush=True)

app.CommandInProgress = True
drag = None
try:
    assert c(hold, 'SetSuppression2', 0, 1, None)
    measure(0.)
    mu = c(app, 'GetMathUtility')
    point = c(mu, 'CreatePoint', array(original[9:12]))
    axis = c(mu, 'CreateVector', array([0., 0., 1.]))
    increment = c(mu, 'CreateTransformRotateAxis', point, axis, math.radians(5))
    drag = c(d, 'GetDragOperator')
    assert c(drag, 'AddComponent', shaft, False)
    drag.CollisionDetectionEnabled = False
    drag.DynamicClearanceEnabled = False
    drag.TransformType = 1
    drag.DragMode = 2
    drag.UseAbsoluteTransform = False
    assert c(drag, 'BeginDrag')
    for deg in range(5, 361, 5):
        assert c(drag, 'DragAsUI', increment), ('Shaft drag failed', deg)
        if deg % 30 == 0:
            measure(deg)
    assert c(drag, 'EndDrag')
    drag = None
    result['result'] = 'passed sampled native full revolution at construction XY offset'
finally:
    if drag is not None:
        c(drag, 'EndDrag')
    # Preserve a usable, recoverable construction pose even if a check fails.
    assert c(hold, 'SetSuppression2', 1, 1, None)
    c(d, 'ForceRebuild3', False)
    result['restored_shaft_transform'] = tf(shaft)
    result['rotor_setup_hold_restored'] = not c(hold, 'IsSuppressed')
    result['ring_setup_hold_suppressed'] = c(c(d, 'FeatureByName', 'RevB_SETUP_Ring_Angle'), 'IsSuppressed')
    save(d)
    (TASK / 'COUPLING_DRIVE_CHECK.json').write_text(json.dumps(result, indent=2))
    app.CommandInProgress = False
