from cad import *

STATE = TASK / 'SOCKET_CAP_INTEGRATION_STATE.json'
d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
maps = json.loads((TASK / 'REV_B_STATE.json').read_text())['maps']
assert json.loads((TASK / 'BLADE_SUPPORT_STATIC_CHECK.json').read_text())['result'] == 'passed'
cap_path = OUT / 'RB_Ball_Socket_Threaded_Retaining_Cap_PROTOTYPE.SLDPRT'
assert cap_path.exists()
sockets = {number + side: ro[mapping[side + 'Socket']] for number, mapping in maps.items() for side in ['Arm', 'Ring']}
part = c(next(iter(sockets.values())), 'GetModelDoc2')
part_path = Path(c(part, 'GetPathName'))
assert part_path.parent == OUT
if STATE.exists():
    raise AssertionError('Socket integration state exists. Inspect partial/native state before recovery; never blindly reinsert.')
recovery = TASK / 'Recovery/Before_Capped_Sockets'
recovery.mkdir(parents=True, exist_ok=True)
assert not (recovery / ASSEMBLY.name).exists()
assert c(d.Extension, 'SaveAs', str(recovery / ASSEMBLY.name), 0, 3, NULL, iref(), iref())
shutil.copy2(part_path, recovery / part_path.name)
s = {'backup': str(recovery), 'part_before_sha256': hashlib.sha256(part_path.read_bytes()).hexdigest(),
     'before_transforms': {name: tf(co) for name, co in ro.items()}, 'caps': {}, 'mates': [],
     'status': 'IN PROGRESS; NOT FABRICATION RELEASED'}
STATE.write_text(json.dumps(s, indent=2))
app.CommandInProgress = True
try:
    face_circles(part, 2, .0022, [(0., 0., .0022)], .003)
    cut(part, 'RevB_M6x0p35_Cap_Female_Thread_Major_Pocket', .0014)
    assert c(part, 'EditRebuild3')
    s['body_check'] = inspect_part(part)
    c(part, 'SetMaterialPropertyName2', 'Default', MAT_DB, '7075-T6 (SN)')
    db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
    assert c(part, 'GetMaterialPropertyName2', 'Default', db) == '7075-T6 (SN)'
    assert not c(c(part.Extension, 'CreateMassProperty2'), 'GetOverrideOptions').OverrideMass
    c(part.Extension.CustomPropertyManager(''), 'Add3', 'DESIGN_DESCRIPTION', 30,
      'Machined7075-T6 socket body withD6 top opening andM6x0.35 female cap thread Z0.8..2.2. '
      'Open cap to insertD5 ball; retained cap supplies upperD5.05 spherical seat andD4.4 mouth. '
      'Original lower spherical seat, neck, rod bondboreD2.1x2.7 and centres preserved. '
      'Thread is major envelope; taps/runouts/fit, lubrication, anti-loosening, proof pullout and fatigue not released.', 2)
    save(part)
    s['body_after_sha256'] = hashlib.sha256(part_path.read_bytes()).hexdigest()
    STATE.write_text(json.dumps(s, indent=2))
    getdoc(cap_path)
    for key, socket in sockets.items():
        activate(d)
        t = tf(socket)
        co = c(d, 'AddComponent5', str(cap_path), 0, '', False, '', *t[9:12])
        assert co
        set_transform(co, t[9:12], np.array(t[:9]).reshape(3, 3))
        s['caps'][key] = co.Name2
        STATE.write_text(json.dumps(s, indent=2))
        name = 'RevB_Socket_' + key + '_Threaded_Cap'
        lock(d, socket, co, name)
        s['mates'].append(name)
        STATE.write_text(json.dumps(s, indent=2))
    assert c(d, 'ForceRebuild3', False)
    s['mate_errors'] = errors(active_mates(d))
    STATE.write_text(json.dumps(s, indent=2))
    assert not s['mate_errors'], s['mate_errors']
    for name, old in s['before_transforms'].items():
        assert np.max(abs(np.array(tf(ro[name])) - old)) < 1e-6, name
    save(d)
    s.update({'complete': True, 'status': 'Eight capped spherical joints installed; nominal geometry/rebuild checked. Physical thread locking, wear, pullout and fatigue remain unverified.',
              'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest(),
              'assembly_method': 'Unthread cap, insert ball throughD6body opening, thread cap to flange seat, then install existing ball/spacer bolt stack.',
              'preserved': ['Ball centres', '56.526653mm rod length', 'Tube insertion2.5mm', 'D2.1 bond bore', 'Spherical articulation'],
              'locking_status': 'No qualified torque/anti-loosening process or physical proof test available; required before operating release.'})
    STATE.write_text(json.dumps(s, indent=2))
    print('EIGHT_CAPPED_SPHERICAL_JOINTS_INSTALLED', flush=True)
finally:
    app.CommandInProgress = False
