from cad import *
import ast

tree = ast.parse(Path(__file__).with_name('build_blade_cartridge.py').read_text())
descriptions = {ast.literal_eval(call.args[0]): ast.literal_eval(call.args[1]) for call in ast.walk(tree)
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'make_part'}
records = json.loads(BUILD_LOG.read_text())
expected = {'RB_Blade_Bearing_Cartridge_PROTOTYPE': [-2.5, 1.8],
            'RB_F693ZZ_3x8x4_FLANGE9p5x0p9_ENVELOPE': [-2.5, 1.5],
            'RB_Blade_Bearing_Outer_Cap_PROTOTYPE': [-3., -1.3],
            'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE': [-1., 0.],
            'RB_Blade_Inner_Race_Spacer_OD4_ID3p05_H0p3': [1.5, 1.8],
            'RB_Blade_Thrust_Film_OD4_ID3p05_H0p15': [1.8, 1.95],
            'RB_Hub_Endplate_Shim_H0p65_PROTOTYPE': [3., 3.65],
            'RB_M2p5x10_Hub_Screw_REFERENCE': [-10., 2.5]}
app.CommandInProgress = True
try:
    for name, description in descriptions.items():
        path = OUT / (name + '.SLDPRT')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == records[name]['sha256']
        part = getdoc(path)
        if name == 'RB_Hub_Endplate_Shim_H0p65_PROTOTYPE':
            f = c(part, 'FeatureByName', 'Four_D2p8_PCD22')
            fd = c(f, 'GetDefinition')
            assert c(fd, 'AccessSelections', part, NULL)
            c(fd, 'SetEndCondition', True, 1)
            assert c(f, 'ModifyDefinition', fd, part, NULL)
        evidence = inspect_part(part)
        evidence['exact_box_m'] = exact_box(c(part, 'GetBodies2', 0, False)[0])
        axial = np.array(evidence['exact_box_m'])[[2, 5]] * 1000
        assert np.max(abs(axial - expected[name])) < 1e-5, (name, axial, expected[name])
        if name in ['RB_Blade_Bearing_Cartridge_PROTOTYPE', 'RB_Blade_Bearing_Outer_Cap_PROTOTYPE',
                    'RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE']:
            assert c(part, 'FeatureByName', 'Two_Pin_Wrench_Holes_D1p2')
            description = description.replace('spanner feature pending manufacturing definition.', 'TwoD1.2 pin-wrench holes implemented; tooling engagement and torque remain provisional.')
            description = description.replace('spanner feature, torque/locking, tolerances', 'twoD1.2 pin-wrench holes implemented; torque/locking and tolerances')
        c(part.Extension.CustomPropertyManager(''), 'Add3', 'DESIGN_DESCRIPTION', 30, description, 2)
        save(part)
        records[name].update(evidence)
        records[name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        records[name]['description'] = description
        BUILD_LOG.write_text(json.dumps(records, indent=2))
        print('CARTRIDGE_FINAL_EXTENTS_CHECKED', name, axial.tolist(), flush=True)
finally:
    app.CommandInProgress = False
