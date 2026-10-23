from cad import *

d = getdoc(ASSEMBLY, 2)
activate(d)
base = roots(d)['XY_Fixed_Base-1']
origin = np.array(tf(base)[9:12])
cache, components = {}, {}
for co in c(d, 'GetComponents', False):
    if c(co, 'GetSuppression') == 0:
        continue
    p = c(co, 'GetModelDoc2')
    if p is None or c(p, 'GetType') != 1:
        continue
    path = c(co, 'GetPathName')
    if path not in cache:
        cache[path] = [list(c(b, 'GetBodyBox')) for b in c(p, 'GetBodies2', 0, False) or []]
    t = tf(co)
    boxes = []
    for b in cache[path]:
        points = np.array([[x, y, z] for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])])
        points = (points @ np.array(t[:9]).reshape(3, 3) + np.array(t[9:12]) - origin) * 1000
        boxes.append([points.min(0).tolist(), points.max(0).tolist()])
    components[logical(co.Name2)] = {'path': path, 'transform': t, 'base_boxes_mm': boxes}
(TASK / 'PACKAGING_NATIVE_BOXES.json').write_text(json.dumps(components, indent=2))
print('GEOMETRY_SNAPSHOT_SAVED', len(components), flush=True)
