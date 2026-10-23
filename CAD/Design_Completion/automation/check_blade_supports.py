from cad import *

d = getdoc(ASSEMBLY, 2)
activate(d)
s = json.loads((TASK / 'BLADE_CARTRIDGE_INTEGRATION_STATE.json').read_text())
assert s['complete']
ro = roots(d)
changed_roots = set(s['added'].values())
roles = json.loads((SUPPORT / 'connection_roles.json').read_text())
changed_roots.update('RB_' + roles[end + 'Endplate'] for end in ['Mech', 'Drive'])
changed_roots.update('RB_' + roles[end + 'Hub' + str(i) + 'TopWasher'] for end in ['Mech', 'Drive'] for i in range(4))
correction = TASK / 'UPPER_CAP_HEAD_CORRECTION.json'
if correction.exists():
    changed_roots.update(json.loads(correction.read_text())['added'].values())
    old_result = TASK / 'BLADE_SUPPORT_STATIC_CHECK.json'
    recovery = TASK / 'Recovery/Before_Upper_Cap_Button_Heads'
    if old_result.exists() and not (recovery / old_result.name).exists():
        shutil.copy2(old_result, recovery / old_result.name)
records, cache = [], {}
for co in c(d, 'GetComponents', False):
    if c(co, 'GetSuppression') == 0:
        continue
    p = c(co, 'GetModelDoc2')
    if p is None or c(p, 'GetType') != 1:
        continue
    path = c(co, 'GetPathName')
    if path not in cache:
        cache[path] = [(c(b, 'Copy'), list(c(b, 'GetBodyBox'))) for b in c(p, 'GetBodies2', 0, False) or []]
    t = tf(co)
    top = co.Name2.split('/')[0]
    for body, box in cache[path]:
        points = np.array([[x, y, z] for x in (box[0], box[3]) for y in (box[1], box[4]) for z in (box[2], box[5])])
        points = points @ np.array(t[:9]).reshape(3, 3) + np.array(t[9:12])
        records.append({'name': co.Name2, 'body': body, 't': t, 'min': points.min(0), 'max': points.max(0),
                        'changed': top in changed_roots})
print('BLADE_SUPPORT_BODIES', len(records), flush=True)
hits, comparisons = [], 0
for i, a in enumerate(records):
    for b in records[:i]:
        if a['name'] == b['name'] or not (a['changed'] or b['changed']):
            continue
        if np.any(np.minimum(a['max'], b['max']) - np.maximum(a['min'], b['min']) <= 1e-8):
            continue
        aa, bb = c(a['body'], 'Copy'), c(b['body'], 'Copy')
        for body, row in [(aa, a), (bb, b)]:
            assert c(body, 'ApplyTransform', c(c(app, 'GetMathUtility'), 'CreateTransform', array(row['t'])))
        overlap = c(aa, 'Operations2', 15901, bb, iref()) or []
        volume = sum(c(x, 'GetMassProperties', 1.)[3] * 1e9 for x in overlap)
        comparisons += 1
        if volume > 1e-5:
            hit = {'components': [a['name'], b['name']], 'overlap_mm3': volume}
            hits.append(hit)
            print('BLADE_SUPPORT_HIT', json.dumps(hit), flush=True)
clearances = []
for n in range(1, 5):
    blade = ro['Part1-' + str(n)]
    ends = [world(blade, [.0095, 0., z]) for z in [0., .220]]
    gaps = []
    for end, B in zip(['Mech', 'Drive'], ends):
        unit = c(d, 'GetComponentByName', s['added'][end + 'Cartridge' + str(n)])
        U = tf(unit)
        inner = np.array([0., 0., .00195]) @ np.array(U[:9]).reshape(3, 3) + np.array(U[9:12])
        gap = abs(B[2] - inner[2]) * 1000
        gaps.append(gap)
        assert abs(gap - .2) < .001, (end, n, gap)
    clearances.append({'blade': n, 'nominal_thrust_film_gaps_mm': gaps, 'total_endfloat_mm': sum(gaps)})
r = {'scope': 'Installed cartridge internals, moved endplates/head washers, shims and replacement screws against all resolved leaf solids at saved pose',
     'body_count': len(records), 'boolean_comparisons': comparisons, 'threshold_mm3': 1e-5, 'intersections': hits,
     'blade_axial_gaps': clearances, 'result': 'passed' if not hits else 'failed',
     'excluded': ['unchanged pairs', 'same-component imported internals', 'motion between poses', 'loaded gaps/tolerances',
                  'actual bearing internals/contacts; purchased envelope is solid annulus'],
     'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()}
(TASK / 'BLADE_SUPPORT_STATIC_CHECK.json').write_text(json.dumps(r, indent=2))
print('BLADE_SUPPORT_STATIC_RESULT', r['result'], comparisons, flush=True)
