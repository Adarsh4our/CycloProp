from cad import *

STATE = TASK / 'UPPER_CAP_HEAD_CORRECTION.json'
d = getdoc(ASSEMBLY, 2)
activate(d)
if STATE.exists():
    prior = json.loads(STATE.read_text())
    assert '--resume-inspected' in sys.argv and not prior.get('added') and not prior.get('complete'), 'Inspect partial correction before recovery'
ro = roots(d)
roles = json.loads((SUPPORT / 'connection_roles.json').read_text())
capco = ro['Upper_MainBearing_Retainer-1']
recovery = TASK / 'Recovery/Before_Upper_Cap_Button_Heads'
recovery.mkdir(parents=True, exist_ok=True)
if (recovery / ASSEMBLY.name).exists():
    expected = json.loads((TASK / 'BLADE_CARTRIDGE_INTEGRATION_STATE.json').read_text())['assembly_sha256']
    assert hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest() == expected, 'Saved assembly changed since cartridge integration'
    assert len(ro) == 333
    for name, old_t in prior['old_screw_transforms'].items():
        assert np.max(abs(np.array(tf(ro[name])) - old_t)) < 1e-8, 'Unexpected live screw change'
else:
    assert c(d.Extension, 'SaveAs', str(recovery / ASSEMBLY.name), 0, 3, NULL, iref(), iref())
old = {roles['MainCap2Screw' + str(i)]: tf(ro[roles['MainCap2Screw' + str(i)]]) for i in range(3)}
s = {'backup': str(recovery), 'old_screw_transforms': old, 'added': {}, 'mates': [],
     'reason': '0.07849mm3 saved-pose head clash after0.65mm endplate shims; upper-cap button heads seated directly on cap remove0.3mm washers and reduce head height2.0 to1.3mm.',
     'source': 'https://novarametalli.it/contents/en-uk/d519_micro_socket_button_head_screws.html',
     'supplier_reference': 'VTBE-2x4, M2x0.4x4, D3.5 head,H1.3, nominal grade10.9; source geometry is not a procurement certificate.'}
STATE.write_text(json.dumps(s, indent=2))
app.CommandInProgress = True
try:
    def build(part):
        ring(part, 3.5, 0., 0., 1.3, 'Conservative_Button_Head_Envelope')
        ring(part, 2., 0., -4., 0., 'M2x0p4x4_Thread_Major_Envelope')
    path = make_part('RB_M2x4_Button_Head_D3p5_H1p3_REFERENCE',
        'M2x0.4x4 button-head reference per Novara VTBE-2x4: headD3.5H1.3. '
        'Conservative cylindrical head envelope; dome/drive/thread helices omitted. Upper main-bearing cap seats directly without washers. '
        'Nominal3mm thread engagement,1.3mm bottom clearance and0.975mm axial head/hub-bolt gap. '
        'Library4340 is mass proxy; procure certified10.9 or verified equivalent, qualified torque/locking and actual tolerance before release.',
        'AISI 4340 Steel, normalized', build)
    activate(d)
    names = sorted({f.Name for label in ['Screw', 'Washer'] for i in range(3)
                    for f in c(ro[roles['MainCap2' + label + str(i)]], 'GetMates') or []})
    assert names and all(n.startswith('Conn_MainCap2') for n in names), names
    s['removed_mates'] = names
    c(d, 'ClearSelection2', True)
    for name in names:
        f = c(d, 'FeatureByName', name)
        assert f and c(f, 'Select2', True, 0), name
    assert c(d.Extension, 'DeleteSelection2', 0)
    c(d, 'ClearSelection2', True)
    for label in ['Screw', 'Washer']:
        for i in range(3):
            co = ro[roles['MainCap2' + label + str(i)]]
            assert c(co, 'Select4', True, NULL, False)
    assert c(d.Extension, 'DeleteSelection2', 0)
    for i, (name, t) in enumerate(old.items()):
        activate(d)
        R = np.array(t[:9]).reshape(3, 3)
        pos = np.array(t[9:12]) - .0003 * R[2]
        co = c(d, 'AddComponent5', str(path), 0, '', False, '', *map(float, pos))
        assert co
        set_transform(co, pos, R)
        s['added'][str(i)] = co.Name2
        STATE.write_text(json.dumps(s, indent=2))
        mate_name = 'RevB_UpperCap_ButtonHead' + str(i)
        lock(d, capco, co, mate_name)
        s['mates'].append(mate_name)
    assert c(d, 'ForceRebuild3', False)
    s['mate_errors'] = errors([c(d, 'FeatureByName', n) for n in s['mates']])
    assert not s['mate_errors'], s['mate_errors']
    save(d)
    s.update({'complete': True, 'status': 'Implemented; affected mates pass. Native collision recheck pending.',
              'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()})
    STATE.write_text(json.dumps(s, indent=2))
    print('UPPER_CAP_HEADS_CORRECTED', flush=True)
finally:
    app.CommandInProgress = False
