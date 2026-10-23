from pathlib import Path
from shaft_angle_drive import drive_shaft_angle
exec(Path(__file__).with_name('check_coupling_drive.py').read_text().split('\napp.CommandInProgress = True', 1)[0])
CHECK_PATH = TASK / 'NATIVE_PITCH_EXTREMA_CHECK.json'
result['scope'] = 'Native physical coupling at dense-planar-analysis critical pitch positions, e6.88 along+X; no independent ring positioning.'
base = np.array(tf(ro['XY_Fixed_Base-1'])[9:12])
previous_xy = np.array(tf(ringco)[9:11]) - base[:2]
original_angle = c(hold, 'GetDefinition').Angle
original_flip = c(hold, 'GetDefinition').FlipDimension
pivot = world(ro['Part1-1'], [.0095, 0., 0.]) - np.array(original[9:12])
radial_shift = math.atan2(pivot[1], pivot[0]) - initial_phi
theta = np.arange(36000) * 2 * math.pi / 36000
delta = math.radians(-15.825385589180533)
P = .095 * np.c_[np.cos(theta), np.sin(theta)]
B = np.array([.00688, 0.]) + .04 * np.c_[np.cos(theta + delta), np.sin(theta + delta)]
V = B - P
distance = np.linalg.norm(V, axis=1)
k = (.012 ** 2 + distance ** 2 - (.05652665325007647) ** 2) / (2 * .012 * distance)
assert np.max(abs(k)) < 1
alpha = np.arctan2(V[:, 1], V[:, 0])
candidates = np.array([alpha + np.arccos(k), alpha - np.arccos(k)])
pitch = (candidates - (theta - math.pi / 2) + math.pi) % (2 * math.pi) - math.pi
pitch = np.take_along_axis(pitch, np.argmin(abs(pitch), axis=0)[None, :], axis=0)[0]
critical = [int(np.argmin(pitch)), int(np.argmax(pitch))]
app.CommandInProgress = True
try:
    assert set_axis_positions(d, 0., 0.)
    assert set_axis_positions(d, .00688, 0.)
    for index in critical:
        phi = (theta[index] - radial_shift) % (2 * math.pi)
        drive_shaft_angle(d, shaft, hold, phi, c, NULL)
        measure(math.degrees((phi - initial_phi) % (2 * math.pi)))
        row = rows[-1]
        row['predicted_Part1_1_pitch_deg'] = math.degrees(pitch[index])
        row['native_prediction_error_deg'] = row['blade_pitch_deg'][0] - row['predicted_Part1_1_pitch_deg']
        assert abs(row['native_prediction_error_deg']) < .001, row
    result['result'] = 'passed native nominal extrema; does not include tolerance/backlash/loaded variation'
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
    save(d)
    result['restored_xy_mm'] = (previous_xy * 1000).tolist()
    CHECK_PATH.write_text(json.dumps(result, indent=2))
    app.CommandInProgress = False
