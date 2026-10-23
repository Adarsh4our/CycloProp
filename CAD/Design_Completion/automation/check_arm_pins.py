from cad import *

d = getdoc(ASSEMBLY, 2)
activate(d)
s = json.loads((TASK / 'ARM_RETENTION_INTEGRATION_STATE.json').read_text())
assert s['complete']
ro = roots(d)
changed_roots = set(s['added'].values())
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
print('ARM_PIN_BODIES', len(records), flush=True)
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
            print('ARM_PIN_HIT', json.dumps(hit), flush=True)
r = {'scope': 'Four new installed arm crosspin envelopes against all resolved leaf solids at saved pose. Arm/blade cuts only remove material; component positions unchanged by integration.',
     'body_count': len(records), 'boolean_comparisons': comparisons, 'threshold_mm3': 1e-5, 'intersections': hits,
     'result': 'passed' if not hits else 'failed',
     'excluded': ['unchanged pairs', 'same-component imported internals', 'motion between poses', 'loaded gaps/tolerances',
                  'Unmodelled helical threads, loaded deformation and physical wear'],
     'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()}
(TASK / 'ARM_PIN_STATIC_CHECK.json').write_text(json.dumps(r, indent=2))
print('ARM_PIN_STATIC_RESULT', r['result'], comparisons, flush=True)
