from cad import *
d = getdoc(OUT / 'RB_Part1.SLDPRT')
body = c(d, 'GetBodies2', 0, False)[0]
checks = []
for label, z0, z1 in [('Mechanism', -4.65, -.65), ('Drive', 220.65, 224.65)]:
    tool = c(c(app, 'GetModeler'), 'CreateBodyFromCyl', array([.0095, 0., z0 / 1000, 0., 0., 1., .0015, (z1 - z0) / 1000]))
    pieces = c(c(body, 'Copy'), 'Operations2', 15901, tool, iref()) or []
    actual = sum(c(b, 'GetMassProperties', 1.)[3] * 1e9 for b in pieces)
    expected = math.pi * 1.5 ** 2 * (z1 - z0)
    row = {'journal': label, 'interval_local_z_mm': [z0, z1], 'full_D3_cylinder_mm3': expected,
           'native_intersection_mm3': actual, 'missing_volume_mm3': expected - actual,
           'result': 'passed round journal envelope' if abs(expected - actual) < 1e-5 else 'failed incomplete round journal'}
    checks.append(row)
    print('BLADE_JOURNAL', label, row['result'], 'MISSING_VOLUME', round(expected - actual, 8), flush=True)
result = {'scope': 'Exact nominal solid-volume intersection over proposed F693ZZ bearing spans; does not establish tolerance, finish, hardness, material or pin/core bond',
          'part': c(d, 'GetPathName'), 'sha256': hashlib.sha256(Path(c(d, 'GetPathName')).read_bytes()).hexdigest(), 'checks': checks}
(TASK / 'BLADE_JOURNAL_GEOMETRY_CHECK.json').write_text(json.dumps(result, indent=2))
assert all(row['result'].startswith('passed') for row in checks), checks
