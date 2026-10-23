"""Verify preservation and archive the numerical requirements work as a checkpoint."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT / 'CAD/Design_Completion'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = json.loads((TASK / 'STARTING_POINT_CHECKPOINT.json').read_text())
    comparison = json.loads((TASK / 'STARTING_RECOVERY_COMPARISON.json').read_text())
    loads = json.loads((TASK / 'MECHANICAL_LOAD_ENVELOPE.json').read_text())
    assert loads['source_sha256'] == sha(TASK / 'automation/mechanical_load_envelope.py')
    for p, digest in loads['input_sha256'].items():
        assert sha(ROOT / p) == digest, p
    assert loads['baseline_sha256'] == start['baseline_sha256'] == sha(ROOT / 'config/baseline.json')
    source_rows = {p: row for p, row in start['manifest'].items()
                   if Path(p).suffix.upper() in ('.SLDPRT', '.SLDASM', '.SLDDRW', '.PDF', '.SLDMAT')}
    changed = [p for p, row in source_rows.items() if sha(ROOT / p) != row['sha256']]
    assert not changed, changed
    assert comparison['live_pose_unchanged'] and not comparison['source_files_changed']
    assert not start['unresolved_active'] and not start['active_mate_errors']
    assert len(start['live_copies']) == 3
    for row in start['live_copies']:
        assert sha(Path(row['copy'])) == row['sha256']
        assert row['source_path_after'] == row['source'] and row['dirty_after']
    folder = Path(start['folder'])
    archive = folder / 'DISK_START.zip'
    assert sha(archive) == start['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for p, row in start['manifest'].items():
            assert hashlib.sha256(z.read(p.replace('\\', '/'))).hexdigest() == row['sha256'], p
    state = {
        'utc': datetime.now(timezone.utc).isoformat(),
        'overall_status': 'INCOMPLETE: starting state preserved; numerical load/acceptance proposals prepared; no physical release',
        'starting_checkpoint': str(folder),
        'baseline_sha256': start['baseline_sha256'],
        'working_assembly_sha256': start['assembly_sha256'],
        'native_and_drawing_sources_checked_unchanged': len(source_rows),
        'source_changes': changed,
        'verification': {'disk_archive_CRC_and_all_member_SHA256': 'passed',
                         'three_dirty_assembly_copies': 'passed',
                         'read_only_recovery_comparison_preserved_live_pose': 'passed',
                         'numerical_self_checks': loads['self_checks'],
                         'native_rebuild_motion_clearance': 'not performed',
                         'physical_inspection_or_tests': 'not performed'},
        'steps': {
            '1': 'Completed scoped inventory, disk archive, separate dirty-source copies, recovery comparison and evidence currency check; solver DOF not established.',
            '2': 'Draft numerical register and sampled load model complete for review; external inputs/approval and omitted dynamics remain open.',
            '3': 'Not completed: native blade geometric COM identified; construction, real inertia, supplier fits and loaded endfloat remain unresolved.',
            '4': 'Not completed: old servo screen invalid as full selection basis; no adequately documented replacement/drive or priced purchase list.',
            '5': 'Not completed: provisional pitch-error allocation exposes joint/timing issues; no new fits or geometry released.',
            '6': 'Not completed: final frozen geometry, native campaign and 19 hidden-item drawing details outstanding.',
            '7': 'Not performed: no supplied hardware, fabrication, assembly, retention tests or guarded speed qualification.'},
        'release_gates': {'fabrication': 'HOLD', 'assembly_acceptance': 'NOT PERFORMED', 'powered_test': 'HOLD'},
        'next_work': ['Define actual skin/core/spar and metal trunnion geometry/process, then recompute first mass moment and inertia.',
                      'Resolve realistic external load/command/duty limits and distributed linkage dynamics; do not size from inertia-only history.',
                      'Recheck arm/trunnion/rod/bearing/Oldham/post loads; revise interfaces only against the updated design.',
                      'Select documented actuator and main drive hardware before a priced purchase BOM.'],
        'not_authorized_or_performed': ['purchases', 'fabrication', 'powered testing'],
    }
    paths = [TASK / name for name in ['NUMERICAL_REQUIREMENTS_REGISTER.md', 'MECHANICAL_LOAD_ENVELOPE.json',
                                      'CURRENT_RESUME_NOTES.md', 'MECHANICAL_COMPLETION_REPORT.md',
                                      'STARTING_POINT_CHECKPOINT.json', 'STARTING_RECOVERY_COMPARISON.json']]
    paths += [TASK / 'automation' / name for name in ['capture_starting_point.py', 'compare_starting_recovery.py',
                                                     'mechanical_load_envelope.py', 'finalize_requirements_checkpoint.py']]
    state['deliverables'] = {str(p.relative_to(TASK)): sha(p) for p in paths}
    (TASK / 'REMAINING_IMPLEMENTATION_STATUS.json').write_text(json.dumps(state, indent=2))
    paths.append(TASK / 'REMAINING_IMPLEMENTATION_STATUS.json')
    package = folder / 'REQUIREMENTS_WORK.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, str(p.relative_to(TASK)))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
    manifest = {'archive': str(package), 'sha256': sha(package), 'status': state['overall_status'],
                'utc': state['utc'], 'deliverables': state['deliverables']}
    (folder / 'REQUIREMENTS_MANIFEST.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'preserved_native_and_drawing_files': len(source_rows),
                      'requirements_archive': str(package), 'release_gates': state['release_gates']}, indent=2))


if __name__ == '__main__':
    main()
