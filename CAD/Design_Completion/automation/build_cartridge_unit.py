from cad import *

path = OUT / 'RB_Blade_Bearing_Cartridge_Set_PROTOTYPE.SLDASM'
statepath = TASK / 'BLADE_CARTRIDGE_UNIT_STATE.json'
assert not path.exists(), 'Inspect existing cartridge assembly; do not duplicate'
template = c(app, 'GetUserPreferenceStringValue', 9)
assert template
d = c(app, 'NewDocument', template, 0, 0., 0.)
assert d and c(d, 'GetType') == 2
save(d, path)
s = {'assembly': str(path), 'components': {}, 'mates': [],
     'representation': 'Rigid external envelopes for bearing/retention stack. Rolling internals omitted. Axisymmetric inner spacer/film rotation does not change these clearance envelopes; internal bearing behavior is not verified.'}
parts = [('Housing', 'RB_Blade_Bearing_Cartridge_PROTOTYPE'),
         ('Nut', 'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE'),
         ('Cap', 'RB_Blade_Bearing_Outer_Cap_PROTOTYPE'),
         ('Bearing', 'RB_F693ZZ_3x8x4_FLANGE9p5x0p9_ENVELOPE'),
         ('InnerSpacer', 'RB_Blade_Inner_Race_Spacer_OD4_ID3p05_H0p3'),
         ('ThrustFilm', 'RB_Blade_Thrust_Film_OD4_ID3p05_H0p15')]
app.CommandInProgress = True
try:
    for key, name in parts:
        partpath = OUT / (name + '.SLDPRT')
        assert partpath.exists()
        getdoc(partpath)
        activate(d)
        co = c(d, 'AddComponent5', str(partpath), 0, '', False, '', 0., 0., 0.)
        assert co
        if c(co, 'IsFixed'):
            c(d, 'ClearSelection2', True)
            assert c(co, 'Select4', False, NULL, False)
            c(d, 'UnfixComponent')
        set_transform(co, [0., 0., 0.], np.eye(3))
        if key == 'Housing':
            housing = co
            c(d, 'ClearSelection2', True)
            assert c(co, 'Select4', False, NULL, False)
            c(d, 'FixComponent')
            assert c(co, 'IsFixed')
        else:
            name = 'Cartridge_Envelope_' + key
            lock(d, housing, co, name)
            s['mates'].append(name)
        s['components'][key] = co.Name2
        statepath.write_text(json.dumps(s, indent=2))
    assert c(d, 'ForceRebuild3', False)
    assert not errors(active_mates(d))
    for co in c(d, 'GetComponents', True):
        assert np.max(abs(np.array(tf(co)) - [1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.])) < 1e-8
    c(d.Extension.CustomPropertyManager(''), 'Add3', 'DESIGN_STATUS', 30, 'PROTOTYPE / EXTERNAL ENVELOPES / NOT FABRICATION RELEASED', 2)
    save(d)
    s['complete'] = True
    s['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    statepath.write_text(json.dumps(s, indent=2))
    print('CARTRIDGE_UNIT_ASSEMBLED', flush=True)
finally:
    app.CommandInProgress = False
