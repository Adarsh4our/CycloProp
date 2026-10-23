from cad import *

d = getdoc(ASSEMBLY, 2)
activate(d)
integration = json.loads((TASK / 'FRAME_INTEGRATION_STATE.json').read_text())
assert integration['complete']
changed = set(integration['added'].values())
changed.update('RB_' + n for n in ['Upper_MainBearing_Retainer-1', '686ZZ_6x13x5_ENVELOPE-1',
                                 '686ZZ_6x13x5_ENVELOPE-2'])
changed.update('RB_M3_' + kind + '_REFERENCE-' + str(i) for kind in ['Washer', 'Nut'] for i in range(1, 5))
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
    for body, b in cache[path]:
        points = np.array([[x, y, z] for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])])
        points = points @ np.array(t[:9]).reshape(3, 3) + np.array(t[9:12])
        records.append({'name': co.Name2, 'body': body, 'transform': t,
                        'min': points.min(0), 'max': points.max(0), 'changed': co.Name2 in changed})
print('FRAME_STATIC_BODIES', len(records), flush=True)
hits, comparisons = [], 0
for i, a in enumerate(records):
    for b in records[:i]:
        if a['name'] == b['name'] or not (a['changed'] or b['changed']):
            continue
        if np.any(np.minimum(a['max'], b['max']) - np.maximum(a['min'], b['min']) <= 1e-8):
            continue
        aa, bb = c(a['body'], 'Copy'), c(b['body'], 'Copy')
        for body, record in [(aa, a), (bb, b)]:
            assert c(body, 'ApplyTransform', c(c(app, 'GetMathUtility'), 'CreateTransform', array(record['transform'])))
        intersection = c(aa, 'Operations2', 15901, bb, iref()) or []
        volume = sum(c(x, 'GetMassProperties', 1.)[3] * 1e9 for x in intersection)
        comparisons += 1
        if volume > 1e-5:
            hit = {'components': [a['name'], b['name']], 'overlap_mm3': volume}
            hits.append(hit)
            print('FRAME_STATIC_HIT', json.dumps(hit), flush=True)
r = {'scope': 'All new frame components and relocated bearings/cap/base washers/nuts against all resolved leaf solids at construction pose',
     'body_count': len(records), 'boolean_comparisons': comparisons, 'positive_volume_threshold_mm3': 1e-5,
     'intersections': hits, 'result': 'passed' if not hits else 'failed',
     'excluded_scope': ['unchanged-existing pairs', 'same-component imported internal bodies',
                        'motion between poses', 'running-gap and tolerance/deflection validation'],
     'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()}
(TASK / 'FRAME_STATIC_CHECK.json').write_text(json.dumps(r, indent=2))
print('FRAME_STATIC_RESULT', r['result'], 'COMPARISONS', comparisons, 'HITS', len(hits), flush=True)
