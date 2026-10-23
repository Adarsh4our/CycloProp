"""Preserve disk files and dirty live documents without saving over a source."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile
import faulthandler

import pythoncom
import win32com.client
import win32com.client.dynamic

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT / 'CAD/Design_Completion'
ASSEMBLY = TASK / 'RevB_Isolated/RB_Assem20_Design_RevB.SLDASM'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(obj, name, *args):
    obj._FlagAsMethod(name)
    return getattr(obj, name)(*args)


def capture():
    faulthandler.dump_traceback_later(60, repeat=True)
    pythoncom.CoInitialize()
    # Attach only; never create another SolidWorks process.
    app = win32com.client.dynamic.Dispatch(win32com.client.GetActiveObject('SldWorks.Application'))
    doc = call(app, 'GetOpenDocumentByName', str(ASSEMBLY))
    assert doc is not None, 'Expected working assembly is not open; no documents changed'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = TASK / 'Checkpoints' / ('START_' + stamp)
    folder.mkdir()
    state = {'utc': datetime.now(timezone.utc).isoformat(), 'folder': str(folder),
             'working_assembly': str(ASSEMBLY), 'assembly_sha256': digest(ASSEMBLY),
             'baseline_sha256': digest(ROOT / 'config/baseline.json'),
             'scope': 'Read-only native inventory plus separate SaveAs-copy preservation; no rebuild or motion.',
             'open_documents': [], 'components': [], 'mates': [], 'constraints': {}, 'live_copies': []}
    files = [p for p in (TASK / 'RevB_Isolated').rglob('*')
             if p.is_file() and p.suffix.upper() in ('.SLDPRT', '.SLDASM') and not p.name.startswith('~$')]
    files += [p for p in (TASK / 'Drawings_Prototype').glob('*')
              if p.suffix.upper() in ('.SLDDRW', '.PDF', '.JSON', '.CSV') and not p.name.startswith('~$')]
    files += list((TASK / 'Materials').glob('*'))
    files += list(TASK.glob('*.json')) + list(TASK.glob('*.md'))
    files += [ROOT / 'config/baseline.json']
    files += list((TASK / 'automation').glob('*.py'))
    files = sorted(set(p for p in files if p.is_file()))
    state['manifest'] = {str(p.relative_to(ROOT)): {'sha256': digest(p), 'bytes': p.stat().st_size} for p in files}
    archive = folder / 'DISK_START.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for p in files:
            z.write(p, str(p.relative_to(ROOT)))
    state['archive_sha256'] = digest(archive)
    print('Disk archive preserved:', folder, flush=True)
    prior = TASK / 'Recovery/Balloon_Task_Final_Live_Source/LIVE_SOURCE_ASSOCIATIONS_PRESERVED.SLDASM'
    state['latest_recovery'] = {'path': str(prior), 'sha256': digest(prior), 'bytes': prior.stat().st_size}
    open_doc = call(app, 'GetFirstDocument')
    live = []
    while open_doc:
        path = call(open_doc, 'GetPathName')
        row = {'path': path, 'title': call(open_doc, 'GetTitle'),
               'dirty': bool(call(open_doc, 'GetSaveFlag')), 'type': call(open_doc, 'GetType')}
        state['open_documents'].append(row)
        print('Open document:', row, flush=True)
        if path and Path(path).is_relative_to(TASK / 'RevB_Isolated'):
            live.append((open_doc, row))
        open_doc = call(open_doc, 'GetNext')
    state['active_path'] = call(app.ActiveDoc, 'GetPathName') if app.ActiveDoc else None
    state['assembly_dirty_before'] = bool(call(doc, 'GetSaveFlag'))
    state['configuration'] = doc.ConfigurationManager.ActiveConfiguration.Name
    state['configurations'] = list(call(doc, 'GetConfigurationNames'))
    state['root_count'] = len(call(doc, 'GetComponents', True))
    print('Configurations and roots captured', flush=True)
    for co in call(doc, 'GetComponents', False):
        path = call(co, 'GetPathName')
        suppression = call(co, 'GetSuppression')
        model = call(co, 'GetModelDoc2')
        transform = call(co, 'GetTotalTransform', True)
        state['components'].append({'name': co.Name2, 'path': path, 'suppression': suppression,
                                    'referenced_configuration': co.ReferencedConfiguration,
                                    'virtual': bool(co.IsVirtual), 'resolved': model is not None,
                                    'transform': list(transform.ArrayData) if transform else None,
                                    'path_exists': Path(path).exists() if path else False})
    feature = call(doc, 'FirstFeature')
    print('Component inventory captured:', len(state['components']), flush=True)
    while feature:
        if call(feature, 'GetTypeName2') == 'MateGroup':
            sub = call(feature, 'GetFirstSubFeature')
            while sub:
                suppressed = bool(call(sub, 'IsSuppressed'))
                warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
                code = call(sub, 'GetErrorCode2', warning)
                state['mates'].append({'name': sub.Name, 'suppressed': suppressed,
                                       'code': code, 'warning': warning.value})
                sub = call(sub, 'GetNextSubFeature')
        feature = call(feature, 'GetNextFeature')
    for name in ['LimitDistance3', 'LimitDistance1', 'Combined_XY_Radial_Limit_6p88mm',
                 'RevB_SETUP_Rotor_Angle', 'RevB_SETUP_Ring_Angle']:
        f = call(doc, 'FeatureByName', name)
        row = {'exists': f is not None}
        if f:
            row['suppressed'] = bool(call(f, 'IsSuppressed'))
            if name.startswith('Limit') or name.startswith('Combined'):
                fd = call(f, 'GetDefinition')
                row.update(advanced=bool(fd.IsAdvancedMate), distance_mm=fd.Distance * 1000,
                           minimum_mm=fd.MinimumDistance * 1000, maximum_mm=fd.MaximumDistance * 1000)
        state['constraints'][name] = row
    print('Mates and travel constraints captured', flush=True)
    # Save copies last, after observing state. Option 3 is Silent | Copy.
    for live_doc, row in live:
        if row['dirty']:
            dest = folder / 'Live' / Path(row['path']).name
            dest.parent.mkdir(exist_ok=True)
            error = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            null = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
            ok = call(live_doc.Extension, 'SaveAs', str(dest), 0, 3, null, error, warning)
            assert ok and not error.value, (dest, error.value, warning.value)
            state['live_copies'].append({'source': row['path'], 'copy': str(dest),
                                         'sha256': digest(dest), 'save_warning': warning.value,
                                         'source_path_after': call(live_doc, 'GetPathName'),
                                         'dirty_after': bool(call(live_doc, 'GetSaveFlag'))})
    state['changed_disk_sources'] = [str(p.relative_to(ROOT)) for p in files
                                     if digest(p) != state['manifest'][str(p.relative_to(ROOT))]['sha256']]
    state['assembly_dirty_after'] = bool(call(doc, 'GetSaveFlag'))
    state['unresolved_active'] = [r['name'] for r in state['components'] if r['suppression'] != 0 and not r['resolved']]
    state['outside_active_references'] = [r for r in state['components'] if r['suppression'] != 0 and r['path']
                                        and not Path(r['path']).is_relative_to(TASK / 'RevB_Isolated')]
    state['active_mate_errors'] = [r for r in state['mates'] if not r['suppressed'] and r['code']]
    prior_models = json.loads((TASK / 'ASSEMBLY_BALLOON_DRAWING_STATE.json').read_text())['native_models_before']
    state['changed_since_balloon_disk_snapshot'] = [p for p, sha in prior_models.items() if digest(Path(p)) != sha]
    motion = json.loads((TASK / 'RESTORED_MOTION_CONSTRAINTS.json').read_text())
    by_name = {r['name'].removeprefix('RB_'): r for r in state['components']}
    state['watched_pose_delta_from_restored_motion'] = {
        name: max(abs(a - b) for a, b in zip(by_name[name]['transform'], before))
        for name, before in motion['before_transforms'].items()}
    index = json.loads((TASK / 'Drawings_Prototype/DRAWING_INDEX.json').read_text())
    state['drawing_currency'] = {name: digest(Path(row['model'])) == row['model_sha256']
                                for name, row in index['drawings'].items()}
    state['verification_limits'] = [
        'No rebuild, configuration switch, independent ring drive, collision or DOF solve performed.',
        'Recovery/live assembly bytes can differ due to save metadata/associations; no semantic equivalence inferred.',
        'Historical motion evidence stays scoped to its own geometry snapshot; final campaign remains required.']
    (folder / 'STARTING_POINT.json').write_text(json.dumps(state, indent=2))
    (TASK / 'STARTING_POINT_CHECKPOINT.json').write_text(json.dumps(state, indent=2))
    assert not state['changed_disk_sources'], state['changed_disk_sources']
    assert state['baseline_sha256'] == '2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f'
    print(json.dumps({k: state[k] for k in ['folder', 'assembly_dirty_before', 'assembly_dirty_after',
                     'root_count', 'configuration', 'unresolved_active', 'active_mate_errors',
                     'changed_disk_sources', 'changed_since_balloon_disk_snapshot', 'live_copies',
                     'watched_pose_delta_from_restored_motion']}, indent=2), flush=True)


if __name__ == '__main__':
    capture()
