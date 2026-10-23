from pathlib import Path
from shaft_angle_drive import drive_shaft_angle
exec(Path(__file__).with_name('check_coupling_drive.py').read_text().split('\napp.CommandInProgress = True', 1)[0])
result['scope'] = 'Native shaft angle mate drives assembly. Ring angle hold suppressed; no independently prescribed ring position.'
fd = c(hold, 'GetDefinition')
original_angle = fd.Angle
original_flip = fd.FlipDimension
previous_rows = []
if '--resume' in sys.argv:
    previous = json.loads(CHECK_PATH.read_text())
    previous_rows = previous['poses']
    assert [r['shaft_increment_deg'] for r in previous_rows] == [0., 30, 60, 90, 120]
    assert all(abs(r['shaft_drive_error_deg']) < .001 and abs(r['ring_phase_error_deg']) < .001 for r in previous_rows)
app.CommandInProgress = True
try:
    assert not c(hold, 'IsSuppressed')
    measure(0.)
    if previous_rows:
        rows.extend(previous_rows[1:])
        result['resumed_after_increment_deg'] = 120
        result['driving_reference'] = 'Assembly Front Plane added to resolve shaft angle direction beyond180degrees; prior0..120poses retained.'
    for deg in range(150 if previous_rows else 30, 361, 30):
        flip = drive_shaft_angle(d, shaft, hold, original_angle + math.radians(deg), c, NULL)
        measure(deg)
        rows[-1]['shaft_drive_flip_dimension'] = flip
    result['result'] = 'passed sampled native full revolution at construction XY offset'
except Exception as exc:
    result['result'] = 'failed'
    result['failure'] = str(exc)
    raise
finally:
    fd = c(hold, 'GetDefinition')
    fd.Angle = original_angle
    fd.FlipDimension = original_flip
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    assert c(d, 'ForceRebuild3', False)
    save(d)
    result['restored_shaft_transform'] = tf(shaft)
    result['rotor_setup_hold_active_as_drive'] = not c(hold, 'IsSuppressed')
    result['ring_setup_hold_suppressed'] = c(c(d, 'FeatureByName', 'RevB_SETUP_Ring_Angle'), 'IsSuppressed')
    (TASK / 'COUPLING_DRIVE_CHECK.json').write_text(json.dumps(result, indent=2))
    app.CommandInProgress = False
