from cad import *

folder = TASK / 'Bench_Prototype'
state_path = folder / 'BLADE_ROTOR_INTEGRATION.json'
state = json.loads(state_path.read_text())
d = getdoc(Path(state['assembly']), 2)
activate(d)
blades = {co.Name2: co for co in c(d, 'GetComponents', True)
          if Path(c(co, 'GetPathName')).name == 'BD_RB_Part1.SLDPRT'}
recovery = folder / 'Before_Width_Repair.SLDASM'
assert not recovery.exists()
assert c(d.Extension, 'SaveAs', str(recovery), 0, 3, NULL, iref(), iref())
changed = []
for n in range(1, 5):
    co = next(co for name, co in blades.items() if name.endswith('Part1-' + str(n)))
    p = c(co, 'GetModelDoc2')
    faces = []
    for z in [0., .220]:
        possible = [face for body in c(p, 'GetBodies2', 0, False) if 'Thrust_Shoulder' in body.Name
                    for face in c(body, 'GetFaces')
                    if c(c(face, 'GetSurface'), 'IsPlane') and
                    abs(c(face, 'GetBox')[2]-z) < 1e-8 and abs(c(face, 'GetBox')[5]-z) < 1e-8]
        assert possible, (n, z)
        face = max(possible, key=lambda f: c(f, 'GetArea'))
        faces.append(c(co, 'GetCorrespondingEntity', face))
    name = 'Width1' if n == 1 else 'Independent_Part1_' + str(n) + '_Span_Centre'
    feature = c(d, 'FeatureByName', name)
    fd = c(feature, 'GetDefinition')
    fd.TabSelection = array(faces, pythoncom.VT_DISPATCH)
    assert c(feature, 'ModifyDefinition', fd, d, NULL), name
    changed.append(name)
assert c(d, 'ForceRebuild3', False)
state['mate_errors'] = errors(active_mates(d))
state['width_repair'] = {'changed_tab_references': changed,
                         'scope': 'Replaced deleted proxy span faces by metal shoulder faces at the same0/220mm planes; width references/constraint type unchanged.'}
state['max_pose_delta'] = float(max(np.max(abs(np.array(tf(co))-state['before_blade_transforms'][name]))
                                    for name, co in blades.items()))
save(d)
state['assembly_sha256'] = hashlib.sha256(Path(state['assembly']).read_bytes()).hexdigest()
state['geometry_and_mates_complete'] = not state['mate_errors'] and state['max_pose_delta'] < 1e-6
state['complete'] = False
state['status'] = 'GEOMETRY/MATES VERIFIED; MIXED-BODY MATERIAL READBACK AND FABRICATION/PHYSICAL QUALIFICATION REMAIN OPEN'
state_path.write_text(json.dumps(state, indent=2))
assert state['geometry_and_mates_complete'], (state['mate_errors'], state['max_pose_delta'])
print('BLADE_GEOMETRY_MATES_PRESERVED', changed, 'max_pose_delta', state['max_pose_delta'], flush=True)
