from cad import *
d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
roles = json.loads((SUPPORT / 'connection_roles.json').read_text())
names = ['Part1-' + str(i) for i in range(1, 5)]
names += [roles[k] for k in ['MechHub', 'MechEndplate', 'DriveHub', 'DriveEndplate']]
result = {}
for name in names:
    co = ro[name]
    mates = []
    for f in c(co, 'GetMates') or []:
        row = {'name': f.Name, 'type': c(f, 'GetTypeName2'), 'suppressed': c(f, 'IsSuppressed')}
        definition = c(f, 'GetDefinition')
        for prop in ['Distance', 'FlipDimension', 'IsAdvancedMate']:
            try:
                row[prop] = getattr(definition, prop)
            except Exception:
                pass
        mate_data = c(f, 'GetSpecificFeature2')
        if mate_data:
            entities = []
            for i in range(c(mate_data, 'GetMateEntityCount')):
                entity = c(mate_data, 'MateEntity', i)
                other = entity.ReferenceComponent
                entities.append({'component': other.Name2 if other else None, 'reference_type': entity.ReferenceType,
                                 'entity_params': list(entity.EntityParams) if entity.EntityParams else None})
            row['entities'] = entities
        mates.append(row)
    result[name] = {'path': c(co, 'GetPathName'), 'transform': tf(co), 'mates': mates}
(TASK / 'BLADE_AXIAL_INTERFACE_INSPECTION.json').write_text(json.dumps(result, indent=2))
c(d, 'ShowNamedView2', '*Isometric', 7)
c(d, 'ViewZoomtofit2')
c(d, 'GraphicsRedraw2')
assert c(d, 'SaveBMP', str(TASK / 'REV_B_CAGE_COUPLING_PREVIEW.bmp'), 1600, 1200)
print('BLADE_AXIAL_INTERFACES_CAPTURED', flush=True)
