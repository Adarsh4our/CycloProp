from cad import *

STATE = TASK / 'BLADE_CARTRIDGE_INTEGRATION_STATE.json'
d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
roles = json.loads((SUPPORT / 'connection_roles.json').read_text())
inspection = json.loads((TASK / 'BLADE_AXIAL_INTERFACE_INSPECTION.json').read_text())
assert json.loads((TASK / 'BLADE_CARTRIDGE_UNIT_STATE.json').read_text())['complete']
assert all(r['result'].startswith('passed') for r in json.loads((TASK / 'BLADE_JOURNAL_GEOMETRY_CHECK.json').read_text())['checks'])
shaft = ro['3-Drive_Shaft-1']
plates = {end: ro[roles[end + 'Endplate']] for end in ['Mech', 'Drive']}
hubs = {end: ro[roles[end + 'Hub']] for end in ['Mech', 'Drive']}
platepart = c(plates['Mech'], 'GetModelDoc2')
if STATE.exists():
    s = json.loads(STATE.read_text())
    assert not s.get('complete'), 'Cartridges already installed; inspect instead of rerunning'
    assert '--resume-inspected' in sys.argv, 'Partial integration exists. Inspect live state before an explicit recovery run.'
else:
    checkpoint = json.loads((TASK / 'PAUSE_CHECKPOINT.json').read_text())
    assert hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest() == checkpoint['assembly_sha256'], 'Source changed since saved checkpoint'
    assert len(ro) == 323, 'Unexpected source component inventory'
    recovery = TASK / 'Recovery/Before_Blade_Cartridge_Integration'
    recovery.mkdir(parents=True, exist_ok=True)
    assert not (recovery / ASSEMBLY.name).exists()
    assert c(d.Extension, 'SaveAs', str(recovery / ASSEMBLY.name), 0, 3, NULL, iref(), iref())
    p = Path(c(platepart, 'GetPathName'))
    assert p.parent == OUT
    shutil.copy2(p, recovery / p.name)
    s = {'backup': str(recovery), 'added': {}, 'mates': [], 'completed': [],
         'before_transforms': {name: tf(co) for name, co in ro.items()},
         'original_width_mates': {}, 'old_blade_axis_mates': {}, 'removed': []}
    for n in range(1, 5):
        name = 'Part1-' + str(n)
        s['original_width_mates'][name] = next(m['name'] for m in inspection[name]['mates'] if m['type'] == 'MateWidth')
        s['old_blade_axis_mates'][name] = next(m['name'] for m in inspection[name]['mates'] if m['type'] == 'MateConcentric' and
                                               any('Endplate_Hub_Interface' in str(e['component']) for e in m['entities']))

def persist():
    STATE.write_text(json.dumps(s, indent=2))

def remove_features(names):
    c(d, 'ClearSelection2', True)
    found = []
    for name in names:
        f = c(d, 'FeatureByName', name)
        if f:
            assert c(f, 'Select2', True, 0), name
            found.append(name)
    if found:
        assert c(d.Extension, 'DeleteSelection2', 0), found

def rigid(parent, child, name):
    if not c(d, 'FeatureByName', name):
        lock(d, parent, child, name)
        s['mates'].append(name)
        persist()

def insert(key, file, point, rotation, parent, kind=1):
    if key in s['added']:
        co = c(d, 'GetComponentByName', s['added'][key])
        assert co
        rigid(parent, co, 'RevB_BladeSupport_' + key)
        return co
    path = OUT / file
    getdoc(path, kind)
    activate(d)
    co = c(d, 'AddComponent5', str(path), 0, '', False, '', *map(float, point))
    assert co
    set_transform(co, point, rotation)
    s['added'][key] = co.Name2
    persist()
    rigid(parent, co, 'RevB_BladeSupport_' + key)
    return co

app.CommandInProgress = True
d.ActiveView.EnableGraphicsUpdate = False
try:
    persist()
    if 'endplates_spaced' not in s['completed']:
        for blade_name, width_name in s['original_width_mates'].items():
            assert c(c(d, 'FeatureByName', width_name), 'SetSuppression2', 0, 1, None)
            name = 'RevB_Cartridge_SETUP_' + blade_name.replace('-', '_')
            if not c(d, 'FeatureByName', name):
                c(d, 'ClearSelection2', True)
                for ent in [mappedplane(shaft, 'Front Plane'), mappedplane(ro[blade_name], 'Front Plane')]:
                    entityselect(d, ent)
                f = c(d, 'AddDistanceMate', 0, False, .0325, .0325, .0325, 0, 0, iref())
                assert f
                f.Name = name
        removal = ['Conn_' + end + 'Endplate_Rigid' for end in plates]
        removal += ['Conn_' + end + 'Hub' + str(i) + label + '_Rigid' for end in plates for i in range(4)
                    for label in ['TopWasher', 'Bolt']]
        remove_features(removal)
        for end, plate in plates.items():
            old = s['before_transforms'][roles[end + 'Endplate']]
            rotation = np.array(old[:9]).reshape(3, 3)
            set_transform(plate, np.array(old[9:12]) + .00065 * rotation[2], rotation)
            rigid(hubs[end], plate, 'RevB_' + end + '_Endplate_Spaced_H0p65')
            for i in range(4):
                washer = ro[roles[end + 'Hub' + str(i) + 'TopWasher']]
                old = s['before_transforms'][roles[end + 'Hub' + str(i) + 'TopWasher']]
                hrot = np.array(tf(hubs[end])[:9]).reshape(3, 3)
                set_transform(washer, np.array(old[9:12]) + .00065 * hrot[2], np.array(old[:9]).reshape(3, 3))
                rigid(hubs[end], washer, 'RevB_' + end + '_HubHeadWasher' + str(i))
        for blade_name, width_name in s['original_width_mates'].items():
            remove_features(['RevB_Cartridge_SETUP_' + blade_name.replace('-', '_')])
            assert c(c(d, 'FeatureByName', width_name), 'SetSuppression2', 1, 1, None)
        assert c(d, 'ForceRebuild3', False)
        for n in range(1, 5):
            name = 'Part1-' + str(n)
            assert np.max(abs(np.array(tf(ro[name])) - s['before_transforms'][name])) < 1e-6, name
        s['completed'].append('endplates_spaced')
        persist()
        print('ENDPLATES_SPACED_BLADE_TRANSFORMS_PRESERVED', flush=True)
    if 'hub_hardware_replaced' not in s['completed']:
        c(d, 'ClearSelection2', True)
        for end in plates:
            for i in range(4):
                name = roles[end + 'Hub' + str(i) + 'Bolt']
                assert c(ro[name], 'Select4', True, NULL, False)
                s['removed'].append(name)
        assert c(d.Extension, 'DeleteSelection2', 0)
        for end, hub in hubs.items():
            ht = tf(hub)
            R = np.array(ht[:9]).reshape(3, 3)
            insert(end + 'HubShim', 'RB_Hub_Endplate_Shim_H0p65_PROTOTYPE.SLDPRT', ht[9:12], R, hub)
            for i in range(4):
                a = math.pi / 4 + i * math.pi / 2
                point = np.array([.011 * math.cos(a), .011 * math.sin(a), .00565]) @ R + np.array(ht[9:12])
                insert(end + 'HubBolt' + str(i), 'RB_M2p5x10_Hub_Screw_REFERENCE.SLDPRT', point, R, hub)
        s['completed'].append('hub_hardware_replaced')
        persist()
    for end, plate in plates.items():
        pt = tf(plate)
        R = np.array(pt[:9]).reshape(3, 3)
        unit_R = np.array([R[0], -R[1], -R[2]])
        outside = world(plate, [0., 0., .0015])
        for n in range(1, 5):
            key = end + 'Cartridge' + str(n)
            pivot = world(ro['Part1-' + str(n)], [.0095, 0., 0.])
            delta = pivot - outside
            point = outside + delta - np.dot(delta, unit_R[2]) * unit_R[2]
            unit = insert(key, 'RB_Blade_Bearing_Cartridge_Set_PROTOTYPE.SLDASM', point, unit_R, plate, 2)
            if end == 'Mech':
                name = 'RevB_Part1_' + str(n) + '_Bearing_Axis'
                if not c(d, 'FeatureByName', name):
                    bearing = next(ch for ch in c(unit, 'GetChildren') if 'F693ZZ_' in ch.Name2)
                    remove_features([s['old_blade_axis_mates']['Part1-' + str(n)]])
                    mate(d, 1, name, [cyl(bearing, 0., 0., .0015), cyl(ro['Part1-' + str(n)], .0095, 0., .0015)])
                    s['mates'].append(name)
                    persist()
    if 'endplate_holes_enlarged' not in s['completed']:
        if not c(platepart, 'FeatureByName', 'RevB_Four_Cartridge_Pilot_Holes_D10p02_R95'):
            face_circles(platepart, 2, 0., [(x, y, 0.) for x, y in [(.095, 0.), (0., .095), (-.095, 0.), (0., -.095)]], .00501)
            f = cut(platepart, 'RevB_Four_Cartridge_Pilot_Holes_D10p02_R95', .0015)
            fd = c(f, 'GetDefinition')
            assert c(fd, 'AccessSelections', platepart, NULL)
            c(fd, 'SetEndCondition', True, 1)
            assert c(f, 'ModifyDefinition', fd, platepart, NULL)
        inspect_part(platepart)
        save(platepart)
        s['completed'].append('endplate_holes_enlarged')
        persist()
    activate(d)
    assert c(d, 'ForceRebuild3', False)
    s['mate_errors'] = errors(active_mates(d))
    persist()
    assert not s['mate_errors'], s['mate_errors']
    for name in ['3-Drive_Shaft-1'] + ['Part1-' + str(n) for n in range(1, 5)]:
        assert np.max(abs(np.array(tf(ro[name])) - s['before_transforms'][name])) < 1e-6, name
    save(d)
    s.update({'complete': True, 'nominal_blade_endfloat_mm': .4, 'endplate_spacing_increase_mm': 1.3,
              'status': 'Cartridges and positive outer-race/G10 retention implemented; nominal centre width mates retained. Load/fit/life and axial-float clearance checks pending.',
              'nominal_hub_pilot_engagement_mm': .85, 'nominal_hub_bolt_protrusion_mm': 1.85,
              'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()})
    persist()
    print('EIGHT_BLADE_CARTRIDGES_INSTALLED', flush=True)
finally:
    d.ActiveView.EnableGraphicsUpdate = True
    app.CommandInProgress = False
    c(d, 'GraphicsRedraw2')
