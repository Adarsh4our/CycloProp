"""Install separate-material blade construction in the isolated development rotor."""
from cad import *

folder = TASK / 'Bench_Prototype'
state_path = folder / 'BLADE_ROTOR_INTEGRATION.json'
resume = state_path.exists()
if resume:
    assert not json.loads(state_path.read_text()).get('complete'), 'Integration already recorded'
isolation = json.loads((folder / 'ROTOR_ISOLATION.json').read_text())
assembly = Path(isolation['assembly'])
d = getdoc(assembly, 2)
activate(d)
components = c(d, 'GetComponents', True)
blades = [co for co in components if Path(c(co, 'GetPathName')).name == 'BD_RB_Part1.SLDPRT']
assert len(blades) == 4
part = c(blades[0], 'GetModelDoc2')
path = Path(c(part, 'GetPathName'))
assert path.parent == assembly.parent
backup = folder / 'Before_Blade_Integration'
if not resume:
    backup.mkdir()
    shutil.copy2(path, backup / path.name)
    assert c(d.Extension, 'SaveAs', str(backup / assembly.name), 0, 3, NULL, iref(), iref())
before = json.loads(state_path.read_text())['before_blade_transforms'] if resume else {co.Name2: tf(co) for co in blades}
state = {'status': 'IN PROGRESS', 'assembly': str(assembly), 'part': str(path), 'backup': str(backup),
         'before_blade_transforms': before, 'body_materials': [],
         'root_support_revision': 'OD3.85x0.5 metal thrust shoulders at span ends; spar relieved0.5mm each end. Keeps overall shoulder span220mm. Minimum spacer/metal contact annulus evaluated separately.'}
state_path.write_text(json.dumps(state, indent=2))
app.CommandInProgress = True
try:
    activate(part)
    if not c(part, 'FeatureByName', 'Bench_Remove_Undefined_Blade_Body_Retain_Exact_Journals'):
        body = c(part, 'GetBodies2', 0, False)[0]
        tool = c(c(app, 'GetModeler'), 'CreateBodyFromCyl', array([.0095, 0., 0., 0., 0., 1., .05, .220]))
        assert c(part, 'CreateFeatureFromBody3', tool, False, 1)
        others = [b for b in c(part, 'GetBodies2', 0, False) if b.Name != body.Name]
        assert len(others) == 1
        feature = c(part.FeatureManager, 'InsertCombineFeature', 15902, body, array(others, pythoncom.VT_DISPATCH))
        assert feature
        feature.Name = 'Bench_Remove_Undefined_Blade_Body_Retain_Exact_Journals'
    for z0, z1 in [(0, 30), (190, 220)]:
        name = 'Bench_Metal_Bond_Stem_' + str(z0)
        if not c(part, 'FeatureByName', name):
            sketch(part)
            circle(part, 9.5, 0, 1.2)
            extrude(part, z0, z1, name)
    for z0, z1 in [(0, .5), (219.5, 220)]:
        name = 'Bench_Metal_Thrust_Shoulder_' + str(z0)
        if not c(part, 'FeatureByName', name):
            sketch(part)
            circle(part, 9.5, 0, 1.925)
            extrude(part, z0, z1, name)
    # The installed version returns NoError for body material assignment but
    # does not retain/read it back. Keep the mixed body part unassigned and
    # report mass from explicit per-body geometry+density, without overrides.
    c(part, 'SetMaterialPropertyName2', 'Default', '', '')
    materials = [(b.Name, 7850.) for b in c(part, 'GetBodies2', 0, False) if 'Bench_Defined_' not in b.Name]
    custom = str(Path(r'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\custom materials\Bench_Blade_Densities.sldmat'))
    for key in ['skin', 'UD_upper', 'UD_lower', 'spar', 'core']:
        existing = c(part, 'FeatureByName', 'Bench_Defined_' + key)
        if existing:
            b = c(c(existing, 'GetFaces')[0], 'GetBody')
            materials.append((b.Name, 52. if key == 'core' else 1550.))
            continue
        source = getdoc(folder / ('BP_Blade_' + key + '.SLDPRT'))
        source_body = c(c(source, 'GetBodies2', 0, False)[0], 'Copy')
        if key in ['spar', 'core']:
            for z0 in [0., .2195]:
                radius = .01 if key == 'spar' else .001975
                cutter = c(c(app, 'GetModeler'), 'CreateBodyFromCyl', array([.0095, 0., z0, 0., 0., 1., radius, .0005]))
                cut_bodies = c(source_body, 'Operations2', 15902, cutter, iref())
                assert cut_bodies and len(cut_bodies) == 1
                source_body = cut_bodies[0]
        activate(part)
        prior = {b.Name for b in c(part, 'GetBodies2', 0, False)}
        feature = c(part, 'CreateFeatureFromBody3', source_body, False, 1)
        assert feature
        feature.Name = 'Bench_Defined_' + key
        added = [b for b in c(part, 'GetBodies2', 0, False) if b.Name not in prior]
        assert len(added) == 1
        b = added[0]
        material = 'BLADE_CORE_52_PROVISIONAL' if key == 'core' else 'BLADE_CFRP_1550_PROVISIONAL'
        code = c(b, 'SetMaterialProperty', 'Default', custom, material)
        db = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, '')
        state.setdefault('material_readback', {})[key] = {'return_code': code,
            'expected': material, 'actual': c(b, 'GetMaterialPropertyName', 'Default', db)}
        materials.append((b.Name, 52. if key == 'core' else 1550.))
    assert c(part, 'EditRebuild3')
    assert len(c(part, 'GetBodies2', 0, False)) == 7
    mass = first = j = 0.
    material_map = dict(materials)
    for b in c(part, 'GetBodies2', 0, False):
        density = material_map[b.Name]
        props = list(c(b, 'GetMassProperties', 1.))
        m = props[3] * density
        jp = density * props[8] + m * ((props[0] - .0095)**2 + props[1]**2)
        mass += m
        first += m * (props[0] - .0095)
        j += jp
        state['body_materials'].append({'body': b.Name, 'density_kg_m3': density, 'mass_kg': m, 'Jp_kgm2': jp,
                                        'COM_m': props[:3]})
    mp = c(part.Extension, 'CreateMassProperty2')
    assert not c(mp, 'GetOverrideOptions').OverrideMass
    state.update(calculated_mixed_material_mass_kg=mass, native_unassigned_proxy_mass_kg=mp.Mass,
                 native_body_material_assignment_verified=False, adhesive_allowance_kg=.0005,
                 mass_for_loads_kg=mass+.0005,
                 aft_COM_offset_for_loads_m=(first+.0005*.010)/(mass+.0005),
                 Jp_for_loads_kgm2=j+.0005*.010**2)
    state_path.write_text(json.dumps(state, indent=2))
    save(part)
    activate(d)
    rebuilt = c(d, 'ForceRebuild3', False)
    state['assembly_rebuild_return'] = bool(rebuilt)
    state['mate_errors'] = errors(active_mates(d))
    state['after_blade_transforms'] = {co.Name2: tf(co) for co in blades}
    state['max_pose_delta'] = max(np.max(abs(np.array(tf(co)) - before[co.Name2])) for co in blades)
    state['status'] = 'GEOMETRY INSTALLED; REBUILD/MATE REPAIR REQUIRED' if state['mate_errors'] else 'NATIVE GEOMETRY INSTALLED; MIXED BODY MATERIAL READBACK/PHYSICAL RELEASE HOLDS REMAIN'
    state_path.write_text(json.dumps(state, indent=2))
    save(d)
    state['assembly_sha256'] = hashlib.sha256(assembly.read_bytes()).hexdigest()
    state['part_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    state['complete'] = not state['mate_errors'] and state['max_pose_delta'] < 1e-6
    state_path.write_text(json.dumps(state, indent=2))
    print('BLADE_INTEGRATION', json.dumps({k: v for k, v in state.items() if k not in ['body_materials', 'before_blade_transforms', 'after_blade_transforms']}), flush=True)
finally:
    app.CommandInProgress = False
