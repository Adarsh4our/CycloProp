from pathlib import Path
from shaft_angle_drive import drive_shaft_angle
exec(Path(__file__).with_name('check_coupling_drive.py').read_text().split('\napp.CommandInProgress = True', 1)[0])
CHECK_PATH = TASK / 'COUPLING_XY_CHECK.json'
result['scope'] = 'Native shaft mate drive at centred carriage and maximum eccentricity6.88mm; physical coupling closure checked. No independent ring positioning.'
base = np.array(tf(ro['XY_Fixed_Base-1'])[9:12])
previous_xy = np.array(tf(ringco)[9:11]) - base[:2]
original_angle = c(hold, 'GetDefinition').Angle
original_flip = c(hold, 'GetDefinition').FlipDimension
app.CommandInProgress = True
try:
    assert set_axis_positions(d, 0., 0.)
    result['eccentricity_mm'] = 0.
    measure(0.)
    assert max(abs(p) for p in rows[-1]['blade_pitch_deg']) < .001
    assert set_axis_positions(d, .00688, 0.)
    result['eccentricity_mm'] = 6.88
    for deg in range(0, 361, 30):
        flip = drive_shaft_angle(d, shaft, hold, original_angle + math.radians(deg), c, NULL)
        measure(deg)
        rows[-1]['shaft_drive_flip_dimension'] = flip
    result['result'] = 'passed sampled native full revolution at maximum radial travel and centred closure'
except Exception as exc:
    result['result'] = 'failed'
    result['failure'] = str(exc)
    raise
finally:
    fd = c(hold, 'GetDefinition')
    fd.Angle = original_angle
    fd.FlipDimension = original_flip
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    assert set_axis_positions(d, 0., 0.)
    assert set_axis_positions(d, float(previous_xy[0]), float(previous_xy[1]))
    result['restored_xy_mm'] = (previous_xy * 1000).tolist()
    result['restored_shaft_transform'] = tf(shaft)
    save(d)
    CHECK_PATH.write_text(json.dumps(result, indent=2))
    app.CommandInProgress = False
