"""Compare selected recovery/saved/live assembly state without overwriting it."""
from capture_starting_point import *
import shutil
import numpy as np


def probe(doc):
    components = {co.Name2.removeprefix('RB_'): co for co in call(doc, 'GetComponents', True)}
    watch = ['3-Drive_Shaft-1', 'Assem3-1'] + ['Part1-' + str(n) for n in range(1, 5)]
    poses = {name: list(call(components[name], 'GetTotalTransform', True).ArrayData) for name in watch}
    constraints = {}
    for name in ['LimitDistance3', 'LimitDistance1', 'RevB_SETUP_Rotor_Angle', 'RevB_SETUP_Ring_Angle']:
        feature = call(doc, 'FeatureByName', name)
        row = {'suppressed': bool(call(feature, 'IsSuppressed'))}
        if name.startswith('Limit'):
            fd = call(feature, 'GetDefinition')
            row.update(distance_mm=fd.Distance * 1000, advanced=bool(fd.IsAdvancedMate))
        constraints[name] = row
    return {'root_count': len(components), 'poses': poses, 'constraints': constraints,
            'configuration': doc.ConfigurationManager.ActiveConfiguration.Name}


def main():
    pythoncom.CoInitialize()
    app = win32com.client.dynamic.Dispatch(win32com.client.GetActiveObject('SldWorks.Application'))
    live = call(app, 'GetOpenDocumentByName', str(ASSEMBLY))
    assert live is not None
    state = json.loads((TASK / 'STARTING_POINT_CHECKPOINT.json').read_text())
    folder = Path(state['folder'])
    before = probe(live)
    result = {'live_before': before, 'comparisons': {}, 'source_files_changed': []}
    for label, source in [('prior_balloon_live_recovery', Path(state['latest_recovery']['path'])),
                          ('saved_working_assembly', ASSEMBLY)]:
        copied = folder / (label + '.SLDASM')
        assert not copied.exists()
        shutil.copy2(source, copied)
        error = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        doc = call(app, 'OpenDoc6', str(copied), 2, 3, '', error, warning)
        assert doc is not None and not error.value, (label, error.value, warning.value)
        try:
            measured = probe(doc)
            measured['open_warning'] = warning.value
            measured['source_sha256'] = digest(source)
            measured['max_pose_delta_from_live'] = {
                name: float(np.max(abs(np.array(t) - before['poses'][name])))
                for name, t in measured['poses'].items()}
            result['comparisons'][label] = measured
            print(label, measured['max_pose_delta_from_live'], flush=True)
        finally:
            call(app, 'CloseDoc', call(doc, 'GetTitle'))
    part = call(app, 'GetOpenDocumentByName', str(TASK / 'RevB_Isolated/RB_Part1.SLDPRT'))
    assert part is not None
    f = call(part, 'FirstFeature')
    features = []
    while f:
        features.append({'name': f.Name, 'kind': call(f, 'GetTypeName2')})
        f = call(f, 'GetNextFeature')
    result['blade_geometry'] = {'features': features, 'bodies': []}
    for body in call(part, 'GetBodies2', 0, False):
        mp = list(call(body, 'GetMassProperties', 1.))
        result['blade_geometry']['bodies'].append({'box_m': list(call(body, 'GetBodyBox')),
                                                  'geometric_mass_properties_density_1': mp})
    result['live_after'] = probe(live)
    result['live_pose_unchanged'] = before == result['live_after']
    result['source_files_changed'] = [p for p, row in state['manifest'].items()
                                       if digest(ROOT / p) != row['sha256']]
    result['interpretation'] = 'Recovery and saved assemblies opened only as uniquely named read-only comparison copies; current live pose retained. No rebuild/motion or saved-file replacement requested.'
    (folder / 'RECOVERY_COMPARISON.json').write_text(json.dumps(result, indent=2))
    (TASK / 'STARTING_RECOVERY_COMPARISON.json').write_text(json.dumps(result, indent=2))
    assert result['live_pose_unchanged'], 'Read-only comparison altered the live pose; copies retained for diagnosis'
    assert not result['source_files_changed'], result['source_files_changed']
    print('RECOVERY_COMPARISON_PRESERVED_LIVE_AND_DISK', flush=True)


if __name__ == '__main__':
    main()
