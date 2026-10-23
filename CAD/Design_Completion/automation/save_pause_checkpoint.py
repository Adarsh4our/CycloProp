from cad import *
from datetime import datetime, timezone

stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
folder = TASK / 'Checkpoints' / stamp
folder.mkdir(parents=True, exist_ok=False)
saved = []
doc = c(app, 'GetFirstDocument')
while doc:
    nextdoc = c(doc, 'GetNext')
    path = c(doc, 'GetPathName')
    if path and Path(path).parent == OUT and c(doc, 'GetSaveFlag'):
        save(doc)
        saved.append(path)
    doc = nextdoc
d = getdoc(ASSEMBLY, 2)
activate(d)
ro = roots(d)
constraints = {}
for name in ['RevB_SETUP_Rotor_Angle', 'RevB_SETUP_Ring_Angle', 'LimitDistance3', 'LimitDistance1']:
    f = c(d, 'FeatureByName', name)
    row = {'exists': f is not None, 'suppressed': c(f, 'IsSuppressed') if f else None}
    if f and name.startswith('Limit'):
        row['advanced_limit'] = c(f, 'GetDefinition').IsAdvancedMate
    constraints[name] = row
baseline = hashlib.sha256((ROOT / 'config/baseline.json').read_bytes()).hexdigest()
assert baseline == '2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f'
assert len(ro) == 323
assert not (TASK / 'BLADE_CARTRIDGE_INTEGRATION_STATE.json').exists()
manifest = {str(p.relative_to(OUT)): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
            for p in OUT.rglob('*') if p.is_file() and p.suffix.upper() in ['.SLDPRT', '.SLDASM', '.SLDDRW'] and not p.name.startswith('~$')}
for name in ['FRAME_INTEGRATION_STATE.json', 'COUPLING_INTEGRATION_STATE.json', 'COUPLING_DRIVE_CHECK.json',
             'COUPLING_XY_CHECK.json', 'NATIVE_PITCH_EXTREMA_CHECK.json', 'COUPLING_STATIC_CHECK.json',
             'BLADE_CARTRIDGE_UNIT_STATE.json', 'BLADE_JOURNAL_GEOMETRY_CHECK.json', 'PART_BUILD_RECORD.json',
             'MECHANICAL_COMPLETION_REPORT.md']:
    shutil.copy2(TASK / name, folder / name)
shutil.copy2(ASSEMBLY, folder / ASSEMBLY.name)
result = {'status': 'PAUSED AT EXPLICIT USER REQUEST', 'timestamp_utc': stamp, 'checkpoint_folder': str(folder),
          'assembly': str(ASSEMBLY), 'assembly_sha256': hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest(),
          'assembly_dirty': c(d, 'GetSaveFlag'), 'root_components': len(ro), 'saved_task_documents': saved,
          'constraints': constraints, 'baseline_sha256': baseline,
          'selected_transforms': {name: tf(ro[name]) for name in ['3-Drive_Shaft-1', 'Part1-1', 'Part1-2', 'Part1-3', 'Part1-4']},
          'native_files': manifest,
          'next_step': 'Review unexecuted integrate_blade_cartridges.py and its restart handling, then integrate8 cartridge subassemblies. Main rotor/endplates are unchanged by cartridge work so far.'}
(TASK / 'PAUSE_CHECKPOINT.json').write_text(json.dumps(result, indent=2))
(folder / 'PAUSE_CHECKPOINT.json').write_text(json.dumps(result, indent=2))
print('PAUSED_CHECKPOINT_SAVED', folder, 'ROOTS', len(ro), 'DIRTY', result['assembly_dirty'], flush=True)
