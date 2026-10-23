from cad import *

STATE_PATH = TASK / 'FRAME_INTEGRATION_STATE.json'
d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
base = ro['XY_Fixed_Base-1']
base_t = tf(base)
origin = np.array(base_t[9:12])
assert np.max(abs(np.array(base_t[:9]).reshape(3, 3) - np.eye(3))) < 1e-8

if STATE_PATH.exists():
    s = json.loads(STATE_PATH.read_text())
    assert not s.get('complete'), 'Frame already installed; inspect instead of rerunning'
else:
    recovery = TASK / 'Recovery/Before_Frame_Integration'
    recovery.mkdir(parents=True, exist_ok=True)
    assert not (recovery / ASSEMBLY.name).exists()
    assert c(d.Extension, 'SaveAs', str(recovery / ASSEMBLY.name), 0, 3, NULL, iref(), iref())
    s = {'backup': str(recovery), 'added': {}, 'mates': [],
         'before_transforms': {name: tf(co) for name, co in ro.items()}, 'removed': []}
    STATE_PATH.write_text(json.dumps(s, indent=2))


def persist():
    STATE_PATH.write_text(json.dumps(s, indent=2))


def attach(co, point, rotation, prefix):
    position = origin + np.array(point) / 1000
    set_transform(co, position, rotation)
    axes = [('Right Plane', 0), ('Top Plane', 1), ('Front Plane', 2)]
    for child_plane, ci in axes:
        name = prefix + '_' + child_plane.replace(' ', '_')
        if c(d, 'FeatureByName', name):
            continue
        cr = np.array(rotation)
        pi = int(np.argmax(abs(cr[ci])))
        assert abs(cr[ci, pi]) > .999999
        alignment = 0 if cr[ci, pi] > 0 else 1
        signed = point[pi] / 1000
        entities = [mappedplane(base, axes[pi][0]), mappedplane(co, child_plane)]
        c(d, 'ClearSelection2', True)
        for entity in entities:
            entityselect(d, entity)
        if abs(signed) < 1e-9:
            f = c(d, 'AddMate5', 0, alignment, False, 0., 0., 0., 0., 0., 0., 0., 0., False, False, 0, iref())
        else:
            gap = abs(signed)
            f = c(d, 'AddDistanceMate', alignment, signed < 0, gap, gap, gap, 0, 0, iref())
        assert f, name
        f.Name = name
        if abs(signed) >= 1e-9:
            fd = c(f, 'GetDefinition')
            fd.FlipDimension = signed < 0
            assert c(f, 'ModifyDefinition', fd, d, NULL)
        s['mates'].append(name)
    persist()


def insert(key, file, point, rotation=None):
    if rotation is None:
        rotation = np.eye(3)
    if key in s['added']:
        co = c(d, 'GetComponentByName', s['added'][key])
        assert co, key
    else:
        path = OUT / file
        assert path.is_file(), path
        getdoc(path)
        activate(d)
        position = origin + np.array(point) / 1000
        co = c(d, 'AddComponent5', str(path), 0, '', False, '', *map(float, position))
        assert co
        s['added'][key] = co.Name2
        persist()
    attach(co, point, rotation, 'RevB_Frame_' + key)
    print('FRAME_ATTACHED', key, flush=True)
    return co


old_keys = json.loads((SUPPORT / 'connection_roles.json').read_text())
obsolete = ['Frame_Mounting_RevA-1', 'Lower_MainBearing_OuterSpacer_L3p5-1', 'Lower_MainBearing_Retainer-1']
obsolete += [n for n in ro if n.startswith(('Stage_Support_L36p5-', 'M3x55_Frame_Screw_REFERENCE-'))]
obsolete += [old_keys['MainCap1' + label + str(i)] for label in ['Screw', 'Washer'] for i in range(3)]
relocate = ['686ZZ_6x13x5_ENVELOPE-1', '686ZZ_6x13x5_ENVELOPE-2', 'Upper_MainBearing_Retainer-1']
relocate += [old_keys['Frame' + label + str(i)] for label in ['Washer', 'Nut'] for i in range(1, 5)]

app.CommandInProgress = True
d.ActiveView.EnableGraphicsUpdate = False
d.EnableAssemblyRebuild = True
d.FeatureManager.EnableFeatureTree = False
d.FeatureManager.EnableFeatureTreeWindow = False
try:
    if not s.get('obsolete_removed'):
        mate_names = set()
        for name in obsolete + relocate:
            assert name in ro, name
            for f in c(ro[name], 'GetMates') or []:
                # Keep the upper cap's valid washer/screw attachments.
                if name == 'Upper_MainBearing_Retainer-1' and f.Name.startswith('Conn_MainCap2'):
                    continue
                mate_names.add(f.Name)
        c(d, 'ClearSelection2', True)
        for name in mate_names:
            f = c(d, 'FeatureByName', name)
            assert f and c(f, 'Select2', True, 0), name
        assert c(d.Extension, 'DeleteSelection2', 0)
        c(d, 'ClearSelection2', True)
        for name in obsolete:
            assert c(ro[name], 'Select4', True, NULL, False), name
        assert c(d.Extension, 'DeleteSelection2', 0)
        s['removed'] = obsolete
        s['removed_mates'] = sorted(mate_names)
        s['obsolete_removed'] = True
        persist()
        print('OLD_FRAME_REMOVED', len(obsolete), flush=True)
    insert('LowerFrame', 'RB_Cage_Lower_Frame_PROTOTYPE.SLDPRT', [0, 0, 0])
    insert('UpperFrame', 'RB_Cage_Upper_Support_PROTOTYPE.SLDPRT', [0, 0, 0])
    insert('Pedestal', 'RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT', [0, 0, 0])
    insert('LowerCap', 'RB_Lower_Bearing_Top_Cap_PROTOTYPE.SLDPRT', [0, 0, 46.5])
    for key, point in [('686ZZ_6x13x5_ENVELOPE-1', [0, 0, 41.5]),
                       ('686ZZ_6x13x5_ENVELOPE-2', [0, 0, 294.7]),
                       ('Upper_MainBearing_Retainer-1', [0, 0, 293.5])]:
        rr = np.array(s['before_transforms'][key][:9]).reshape(3, 3)
        attach(ro[key], point, rr, 'RevB_Frame_' + key.replace('-', '_'))
    for i, (x, y) in enumerate([(x, y) for x in [-105., 105.] for y in [-85., 85.]], 1):
        insert('Tube' + str(i), 'RB_Cage_Tube_OD8_ID6_L308_PROTOTYPE.SLDPRT', [x, y, -4])
        insert('TieRod' + str(i), 'RB_Cage_TieRod_M3_L327_REFERENCE.SLDPRT', [x, y, -13.5])
        for label, z in [('Bottom', -8.5), ('Top', 308.)]:
            insert('TieWasher' + label + str(i), 'RB_M3_Washer_REFERENCE.SLDPRT', [x, y, z])
        for label, z in [('Bottom', -10.9), ('Top', 308.5)]:
            insert('TieNut' + label + str(i), 'RB_M3_Nut_REFERENCE.SLDPRT', [x, y, z])
    for i, (x, y) in enumerate([(x, y) for x in [-24., 24.] for y in [-70., 70.]], 1):
        insert('BaseSpacer' + str(i), 'RB_Base_Spacer_OD6_ID3p4_L4.SLDPRT', [x, y, -4])
        insert('BaseBolt' + str(i), 'RB_M3x16_Base_Screw_REFERENCE.SLDPRT', [x, y, -8.5])
        insert('BaseHeadWasher' + str(i), 'RB_M3_Washer_REFERENCE.SLDPRT', [x, y, -8.5])
        attach(ro[old_keys['FrameWasher' + str(i)]], [x, y, 3.], np.eye(3), 'RevB_Frame_BaseNutWasher' + str(i))
        attach(ro[old_keys['FrameNut' + str(i)]], [x, y, 3.5], np.eye(3), 'RevB_Frame_BaseNut' + str(i))
    for i in range(3):
        x, y = 8.3 * math.cos(math.pi / 6 + i * 2 * math.pi / 3), 8.3 * math.sin(math.pi / 6 + i * 2 * math.pi / 3)
        insert('PedestalScrew' + str(i), 'RB_M2x8_Pedestal_Screw_REFERENCE.SLDPRT', [x, y, -8.3])
        insert('PedestalWasher' + str(i), 'RB_M2_Washer_2p2x5x0p3_REFERENCE.SLDPRT', [x, y, -8.3])
        insert('CapScrew' + str(i), 'RB_M2x5_Bearing_Cap_Screw_REFERENCE.SLDPRT', [x, y, 47.8], np.diag([1., -1., -1.]))
        insert('CapWasher' + str(i), 'RB_M2_Washer_2p2x5x0p3_REFERENCE.SLDPRT', [x, y, 47.5])
    d.EnableAssemblyRebuild = False
    assert c(d, 'ForceRebuild3', False)
    mate_errors = errors(active_mates(d))
    s['mate_errors'] = mate_errors
    persist()
    assert not mate_errors, mate_errors
    for name in ['3-Drive_Shaft-1', 'Part1-1', 'Part1-2', 'Part1-3', 'Part1-4']:
        assert np.max(abs(np.array(tf(ro[name])) - s['before_transforms'][name])) < 1e-7, name
    save(d)
    s['complete'] = True
    s['status'] = 'native structure and reference hardware installed; collision and strength checks pending'
    s['assembly_sha256'] = hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()
    persist()
    print('FRAME_INSTALLED_CLEAN_REBUILD', flush=True)
finally:
    d.EnableAssemblyRebuild = False
    d.FeatureManager.EnableFeatureTree = True
    d.FeatureManager.EnableFeatureTreeWindow = True
    d.ActiveView.EnableGraphicsUpdate = True
    app.CommandInProgress = False
    c(d, 'GraphicsRedraw2')
