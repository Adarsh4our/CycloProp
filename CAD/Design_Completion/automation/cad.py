from pathlib import Path
import json, math, hashlib, shutil

SUPPORT = Path(__file__).resolve().parent / 'support'
exec((SUPPORT / 'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__', 1)[0])

TASK = ROOT / 'CAD/Design_Completion'
OUT = TASK / 'RevB_Isolated'
ASSEMBLY = OUT / 'RB_Assem20_Design_RevB.SLDASM'
BUILD_LOG = TASK / 'PART_BUILD_RECORD.json'
MAT_DB = r'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat'


def c(o, name, *args):
    if name not in o._olerepr_.mapFuncs:
        o._FlagAsMethod(name)
    return getattr(o, name)(*args)


def logical(name):
    return '/'.join(p.removeprefix('RB_') for p in name.split('/'))


def roots(doc):
    return {logical(co.Name2): co for co in c(doc, 'GetComponents', True)}


def tf(co):
    return list(c(co, 'GetTotalTransform', True).ArrayData)


def world(co, point):
    t = tf(co)
    return np.array(point) @ np.array(t[:9]).reshape(3, 3) + np.array(t[9:12])


def set_transform(co, position, rotation):
    co.Transform2 = c(c(app, 'GetMathUtility'), 'CreateTransform',
                      array(np.array(rotation).flatten().tolist() + list(map(float, position)) + [1., 0., 0., 0.]))


def ring(d, od, bore, z0, z1, name):
    sketch(d)
    circle(d, 0, 0, od / 2)
    if bore:
        circle(d, 0, 0, bore / 2)
    return extrude(d, z0, z1, name)


def face_rectangles(d, z, rectangles, name, depth):
    activate(d)
    faces = [f for b in c(d, 'GetBodies2', 0, False) for f in c(b, 'GetFaces')
             if c(c(f, 'GetSurface'), 'IsPlane') and
             abs(c(f, 'GetBox')[2] - z / 1000) < 1e-8 and abs(c(f, 'GetBox')[5] - z / 1000) < 1e-8]
    assert faces, (name, z)
    c(d, 'ClearSelection2', True)
    assert c(max(faces, key=lambda f: c(f, 'GetArea')), 'Select4', False, NULL)
    c(d.SketchManager, 'InsertSketch', True)
    d.SketchManager.AddToDB = True
    t = list(d.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
    for x0, y0, x1, y1 in rectangles:
        points = [np.array([x, y, z]) / 1000 @ np.array(t[:9]).reshape(3, 3) + np.array(t[9:12])
                  for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
        assert max(abs(p[2]) for p in points) < 1e-8
        for a, b in zip(points, points[1:] + points[:1]):
            c(d.SketchManager, 'CreateLine', float(a[0]), float(a[1]), 0., float(b[0]), float(b[1]), 0.)
    close_sketch(d)
    return cut(d, name, depth / 1000)


def inspect_part(d):
    bodies = c(d, 'GetBodies2', 0, False) or []
    assert len(bodies) == 1, ('Expected one connected solid', c(d, 'GetPathName'), len(bodies))
    volume = c(bodies[0], 'GetMassProperties', 1.)[3]
    assert volume > 1e-12
    features = []
    f = c(d, 'FirstFeature')
    while f:
        kind = c(f, 'GetTypeName2')
        if kind in ['Boss', 'Extrusion', 'Cut', 'Revolution', 'Fillet']:
            warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
            code = c(f, 'GetErrorCode2', warning)
            if code:
                features.append({'name': f.Name, 'code': code, 'warning': warning.value})
        f = c(f, 'GetNextFeature')
    assert not features, features
    return {'body_count': 1, 'volume_mm3': volume * 1e9, 'box_m': list(c(bodies[0], 'GetBodyBox')),
            'feature_errors': features}


def exact_box(body):
    limits = [0.] * 6
    for axis in range(3):
        for positive in [False, True]:
            direction = [0., 0., 0.]
            direction[axis] = 1. if positive else -1.
            point = [win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.) for _ in range(3)]
            assert c(body, 'GetExtremePoint', *direction, *point)
            limits[axis + (3 if positive else 0)] = point[axis].value
    return limits


def make_part(name, description, material, build):
    path = OUT / (name + '.SLDPRT')
    records = json.loads(BUILD_LOG.read_text()) if BUILD_LOG.exists() else {}
    if path.exists():
        assert name in records, ('Unrecorded/partial part exists; inspect before recovery', path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == records[name]['sha256'], path
        return path
    d, path = newpart(name, description)
    build(d)
    assert c(d, 'EditRebuild3')
    evidence = inspect_part(d)
    c(d, 'SetMaterialPropertyName2', 'Default', MAT_DB, material)
    db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
    assert c(d, 'GetMaterialPropertyName2', 'Default', db) == material
    mp = c(d.Extension, 'CreateMassProperty2')
    assert not c(mp, 'GetOverrideOptions').OverrideMass
    evidence.update({'path': str(path), 'material': material, 'material_database': db.value,
                     'mass_g': mp.Mass * 1000, 'override_mass': False,
                     'status': 'PROTOTYPE / NOT RELEASED FOR FABRICATION'})
    c(d.Extension.CustomPropertyManager(''), 'Add3', 'DESIGN_STATUS', 30,
      'PROTOTYPE / NOT RELEASED FOR FABRICATION', 2)
    save(d, path)
    evidence['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    records[name] = evidence
    BUILD_LOG.write_text(json.dumps(records, indent=2))
    print('BUILT_CHECKED', name, 'MASS_G', round(evidence['mass_g'], 3), flush=True)
    return path
