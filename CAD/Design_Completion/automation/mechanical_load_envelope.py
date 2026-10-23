"""Sampled rigid-body design study; all nonbaseline limits remain proposals."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT / 'CAD/Design_Completion'


def mechanism(e_xy, count=1440):
    design = json.loads((TASK / 'SELECTED_LINKAGE.json').read_text())
    phi = np.arange(count) * 2 * np.pi / count
    t = phi[:, None] + np.arange(4) * np.pi / 2
    radial = np.stack((np.cos(t), np.sin(t)), axis=-1)
    tangent = np.stack((-np.sin(t), np.cos(t)), axis=-1)
    delta = math.radians(design['neutral_ring_hole_phase_deg'])
    rt = t + delta
    ring_r = .040 * np.stack((np.cos(rt), np.sin(rt)), axis=-1)
    p = .095 * radial
    b = np.array(e_xy) + ring_r
    v = b - p
    distance = np.linalg.norm(v, axis=-1)
    length = design['rod_ball_centre_mm'] / 1000
    k = (.012**2 + distance**2 - length**2) / (.024 * distance)
    assert np.max(abs(k)) < 1, 'No linkage closure / singular branch'
    alpha0 = np.arctan2(v[..., 1], v[..., 0])
    candidates = np.stack((alpha0 + np.arccos(k), alpha0 - np.arccos(k)))
    pitch = (candidates - (t - np.pi / 2) + np.pi) % (2 * np.pi) - np.pi
    pitch = np.take_along_axis(pitch, np.argmin(abs(pitch), axis=0)[None, ...], axis=0)[0]
    alpha = t - np.pi / 2 + pitch
    arm_dir = np.stack((np.cos(alpha), np.sin(alpha)), axis=-1)
    arm_tan = np.stack((-np.sin(alpha), np.cos(alpha)), axis=-1)
    a = p + .012 * arm_dir
    rod = b - a
    # Differentiate closure twice with respect to rotor azimuth, not time.
    v_prime = .040 * np.stack((-np.sin(rt), np.cos(rt)), axis=-1) - .095 * tangent
    denom = .012 * np.sum(rod * arm_tan, axis=-1)
    assert np.min(abs(denom)) > 1e-6
    alpha_prime = np.sum(rod * v_prime, axis=-1) / denom
    rod_prime = v_prime - .012 * arm_tan * alpha_prime[..., None]
    v_second = -ring_r + .095 * radial
    alpha_second = (np.sum(rod_prime**2, axis=-1) + np.sum(
        rod * (v_second + .012 * arm_dir * alpha_prime[..., None]**2), axis=-1)) / denom
    unit = rod / length
    lever = .012 * (arm_dir[..., 0] * unit[..., 1] - arm_dir[..., 1] * unit[..., 0])
    assert np.max(abs(np.linalg.norm(rod, axis=-1) - length)) < 1e-12
    assert np.max(abs(np.roll(pitch, -1, axis=0) - pitch)) < .02
    return dict(pitch=pitch, second=alpha_second, unit=unit, lever=lever,
                ring_r=ring_r, min_lever=float(np.min(abs(lever))),
                phase=phi, alpha_prime=alpha_prime,
                timing_gain=np.sum(rod * (.040 * np.stack((-np.sin(rt), np.cos(rt)), axis=-1)), axis=-1) / denom)


def evaluate(e_xy, mass, offset, inertia, count=1440, rpm=2640):
    g = mechanism(e_xy, count)
    omega = rpm * np.pi / 30
    # Native +X chord opposes arm direction. Moment balance about accelerating
    # quarter-chord pivot: M = Jp*beta_ddot + (m*r_com) cross a_pivot.
    inertial = inertia * omega**2 * g['second']
    orbital = mass * offset * .095 * omega**2 * np.cos(g['pitch'])
    moment = inertial + orbital
    independent_moment_bound = abs(inertial) + abs(orbital)
    rod_force = moment / g['lever']
    ring_force = -rod_force[..., None] * g['unit']
    net = ring_force.sum(axis=1)
    ring_torque = np.sum(g['ring_r'][..., 0] * ring_force[..., 1]
                         - g['ring_r'][..., 1] * ring_force[..., 0], axis=1)
    absolute_rod_bound = independent_moment_bound / abs(g['lever'])
    independent_axis = np.max(np.sum(absolute_rod_bound[..., None] * abs(g['unit']), axis=1), axis=0)
    torque_transfer = (g['ring_r'][..., 0] * g['unit'][..., 1]
                       - g['ring_r'][..., 1] * g['unit'][..., 0]) / g['lever']
    # Independent unknown hinge moments may align adversely: sum absolute
    # transfer coefficients, never assume aerodynamic cancellation between blades.
    transfer_force = np.max(np.sum(abs(g['unit'] / g['lever'][..., None]), axis=1), axis=0)
    transfer_torque = np.max(np.sum(abs((g['ring_r'][..., 0] * g['unit'][..., 1]
                                       - g['ring_r'][..., 1] * g['unit'][..., 0]) / g['lever']), axis=1))
    return {
        'peak_abs_pitch_acceleration_torque_Nm': float(np.max(abs(inertial))),
        'peak_abs_orbital_COM_torque_Nm': float(np.max(abs(orbital))),
        'peak_abs_combined_hinge_torque_Nm': float(np.max(abs(moment))),
        'peak_abs_rod_force_N': float(np.max(abs(rod_force))),
        'independent_blade_inertia_rod_bound_N': float(np.max(absolute_rod_bound)),
        'independent_blade_inertia_axis_bound_N': independent_axis.tolist(),
        'independent_blade_inertia_ring_torque_bound_Nm': float(np.max(np.sum(abs(torque_transfer) * independent_moment_bound, axis=1))),
        'peak_abs_ring_force_xy_N': np.max(abs(net), axis=0).tolist(),
        'peak_abs_ring_torque_Nm': float(np.max(abs(ring_torque))),
        'minimum_rod_moment_arm_mm': 1000 * g['min_lever'],
        'unknown_hinge_to_axis_force_N_per_Nm': transfer_force.tolist(),
        'unknown_hinge_to_ring_torque_Nm_per_Nm': float(transfer_torque),
        'pitch_extrema_deg': np.degrees([g['pitch'].min(), g['pitch'].max()]).tolist(),
        'peak_absolute_pitch_speed_rad_s': float(np.max(abs(g['alpha_prime'] - 1))) * omega,
        'maximum_abs_ring_phase_to_blade_pitch_gain': float(np.max(abs(g['timing_gain']))),
    }


def self_check():
    g = mechanism((.00688, 0), 36000)
    pitch = g['pitch']
    step = 2 * np.pi / len(pitch)
    finite = (np.roll(pitch, -1, axis=0) - 2 * pitch + np.roll(pitch, 1, axis=0)) / step**2
    assert np.max(abs(finite - g['second'])) < 2e-6
    # At centred XY, pitch is constant and the orbital COM term persists.
    centred = evaluate((0, 0), .0125, .0095, 2.632291666666667e-6)
    expected = .0125 * .0095 * .095 * (2640 * np.pi / 30)**2
    assert centred['peak_abs_pitch_acceleration_torque_Nm'] < 1e-12
    assert abs(centred['peak_abs_combined_hinge_torque_Nm'] - expected) < 1e-10
    assert max(centred['peak_abs_ring_force_xy_N']) < 1e-10
    # Retain comparison to the old J-only screen; do not rewrite old evidence.
    old = evaluate((.00688, 0), .0125, 0, 2.632291666666667e-6, 36000)
    assert abs(old['peak_abs_rod_force_N'] - 15.95949617279804) < .0001
    slower = evaluate((.00688, 0), .0125, .0095, 2.632291666666667e-6, 36000, 1320)
    full = evaluate((.00688, 0), .0125, .0095, 2.632291666666667e-6, 36000)
    assert abs(full['peak_abs_rod_force_N'] / slower['peak_abs_rod_force_N'] - 4) < 1e-12
    assert full['independent_blade_inertia_rod_bound_N'] >= full['peak_abs_rod_force_N']
    fine = evaluate((.00688, 0), .0125, .0095, 2.632291666666667e-6, 72000)
    return {'analytic_vs_periodic_second_derivative_max_error': float(np.max(abs(finite - g['second']))),
            'centred_orbital_torque_Nm': expected, 'old_J_only_rod_force_reproduced_N': old['peak_abs_rod_force_N'],
            'rpm_squared_scaling': 'passed', 'closure_and_branch_sampling': 'passed',
            '36000_to_72000_rod_peak_difference_N': abs(full['peak_abs_rod_force_N'] - fine['peak_abs_rod_force_N'])}


def generate():
    checks = self_check()
    baseline = json.loads((ROOT / 'config/baseline.json').read_text())
    omega = baseline['operating']['rpm'] * np.pi / 30
    scenarios = {
        'historical_uniform_chord_corrected': (.0125, .0095, 2.632291666666667e-6),
        'proposed_bench_design_bound': (.020, .010, 5e-6),
        'low_mass_forward_COM_sensitivity': (.010, .003, 1e-6),
    }
    results = {}
    for name, (mass, offset, inertia) in scenarios.items():
        rows = []
        for radius_mm in [0, 1.72, 3.44, 5.16, 6.88]:
            for angle_deg in ([0] if radius_mm == 0 else range(0, 360, 15)):
                angle = math.radians(angle_deg)
                e = [radius_mm / 1000 * math.cos(angle), radius_mm / 1000 * math.sin(angle)]
                rows.append(dict(eccentricity_mm=radius_mm, direction_deg=angle_deg,
                                 **evaluate(e, mass, offset, inertia)))
        results[name] = {'mass_kg': mass, 'aft_COM_offset_from_pivot_m': offset, 'pitch_inertia_about_pivot_kgm2': inertia,
                         'peak_abs_rod_force_N': max(r['peak_abs_rod_force_N'] for r in rows),
                         'independent_blade_inertia_rod_bound_N': max(r['independent_blade_inertia_rod_bound_N'] for r in rows),
                         'independent_blade_inertia_axis_bound_N': [max(r['independent_blade_inertia_axis_bound_N'][i] for r in rows) for i in range(2)],
                         'independent_blade_inertia_ring_torque_bound_Nm': max(r['independent_blade_inertia_ring_torque_bound_Nm'] for r in rows),
                         'peak_abs_combined_hinge_torque_Nm': max(r['peak_abs_combined_hinge_torque_Nm'] for r in rows),
                         'peak_abs_ring_force_xy_N': [max(r['peak_abs_ring_force_xy_N'][i] for r in rows) for i in range(2)],
                         'peak_abs_ring_torque_Nm': max(r['peak_abs_ring_torque_Nm'] for r in rows),
                         'minimum_rod_moment_arm_mm': min(r['minimum_rod_moment_arm_mm'] for r in rows),
                         'unknown_hinge_to_axis_force_N_per_Nm': [max(r['unknown_hinge_to_axis_force_N_per_Nm'][i] for r in rows) for i in range(2)],
                         'unknown_hinge_to_ring_torque_Nm_per_Nm': max(r['unknown_hinge_to_ring_torque_Nm_per_Nm'] for r in rows),
                         'maximum_abs_ring_phase_to_blade_pitch_gain': max(r['maximum_abs_ring_phase_to_blade_pitch_gain'] for r in rows),
                         'poses': rows}
    bound = results['proposed_bench_design_bound']
    q = .5 * 1.225 * 45**2
    hinge_aero = q * .220 * .038**2 * .3
    blade_aero = q * .220 * .038 * 2
    unknown_hinge = hinge_aero + .002  # Assumed oscillatory bearing drag per blade.
    ring_torque = bound['independent_blade_inertia_ring_torque_bound_Nm'] + bound['unknown_hinge_to_ring_torque_Nm_per_Nm'] * unknown_hinge
    floating = json.loads((TASK / 'COUPLING_GEOMETRIC_BOUNDS.json').read_text())
    oldham_inertia = floating['floating_inertial_force_N']
    contact = ring_torque / .028
    oldham_friction = .15 * contact * 2  # Two interfaces; conservative additive bound.
    axis = [f + c * unknown_hinge + oldham_inertia + oldham_friction + 5
            for f, c in zip(bound['independent_blade_inertia_axis_bound_N'], bound['unknown_hinge_to_axis_force_N_per_Nm'])]
    final = {
        'status': 'PROVISIONAL NUMERICAL REQUIREMENTS STUDY; NO FABRICATION OR POWERED RELEASE',
        'baseline_sha256': hashlib.sha256((ROOT / 'config/baseline.json').read_bytes()).hexdigest(),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [ROOT / 'config/baseline.json', TASK / 'SELECTED_LINKAGE.json',
                                  TASK / 'COUPLING_GEOMETRIC_BOUNDS.json']},
        'self_checks': checks, 'rpm': 2640,
        'sampling': {'azimuth_step_deg': .25, 'radial_samples_mm': [0, 1.72, 3.44, 5.16, 6.88],
                     'XY_direction_step_deg': 15, 'blades': 4,
                     'limits': 'Sampled study, not continuous extrema or collision proof; command acceleration excluded.'},
        'moment_equation': 'M_required=J_p*beta_ddot+(m*r_COM)x a_pivot; native chord is arm direction+pi. Aerodynamic/bearing terms added by absolute bounds.',
        'scenarios': results,
        'provisional_external_bounds': {'relative_air_speed_m_s': 45, 'aero_resultant_coefficient_abs': 2,
                                        'hinge_moment_coefficient_abs': .3, 'bearing_drag_each_blade_Nm': .002,
                                        'guide_breakaway_force_each_axis_N': 5, 'Oldham_friction_coefficient': .15},
        'combined_proposed_bound': {
            'aero_force_each_blade_N': blade_aero, 'aero_hinge_torque_each_blade_Nm': hinge_aero,
            'rod_force_N': bound['independent_blade_inertia_rod_bound_N'] + unknown_hinge / (bound['minimum_rod_moment_arm_mm'] / 1000),
            'hinge_torque_Nm': max(r['peak_abs_pitch_acceleration_torque_Nm'] for r in bound['poses']) + .020 * .010 * .095 * omega**2 + unknown_hinge,
            'ring_torque_Nm': ring_torque, 'Oldham_contact_normal_sum_scale_N': contact,
            'Oldham_two_interface_friction_scale_N': oldham_friction,
            'Oldham_disk_inertia_force_N': oldham_inertia,
            'axis_force_xy_N': axis,
            'existing_R12_servo_torque_upper_bound_xy_Nm': [f * .0121 for f in axis],
            'limits': 'Triangle bounds allow each blade mass moment/inertia to vary independently below proposed caps. Sampled geometric coefficients and assumed friction/aero; distributed linkage inertia and command transients remain excluded.',
            'R12_jacobian_bound_basis': 'R12/L40 slider crank, +/-45deg: |dx/dtheta| <=12.1mm/rad; verify physical travel after redesign.',
            'blade_centrifugal_force_at_pivot_radius_N': .020 * .095 * omega**2,
            'residual_unbalance_5_g_mm_force_N': 5e-6 * omega**2,
        },
        'stops_and_jams': {'rotor_inertia_assumption_kgm2': .002,
                           'stored_energy_at_target_J': .5 * .002 * omega**2,
                           'mean_inertial_stop_torque_0p5s_Nm': .002 * omega / .5,
                           'mean_inertial_stop_torque_1ms_Nm': .002 * omega / .001,
                           'decision': 'Rigid jam load is not bounded by steady servo/drive torque. Measure rotor inertia and qualify containment/retention; no intentional full-speed jam test.'},
        'excluded_or_unverified': ['blade/arm/rod mass distribution and inertia measured from final construction',
                                   'arm and rod distributed rotating inertia and gravity orientation',
                                   'aerodynamic transient, induced velocity and hinge moment inputs',
                                   'Oldham Coriolis/drive transients, friction/contact/wear validation',
                                   'XY command acceleration and actuator feedback bandwidth',
                                   'bearing reaction distribution with COM offset and structural flexibility',
                                   'rotor inertia/containment evidence and physical tests'],
    }
    assert all(f > 0 for f in axis)
    assert final['baseline_sha256'] == '2445c7153775b1930e21b65a5d95e5b26c7632c273e1867abcc6c3a6d830fa7f'
    (TASK / 'MECHANICAL_LOAD_ENVELOPE.json').write_text(json.dumps(final, indent=2))
    print(json.dumps({'self_checks': checks, 'scenarios': {k: {a: b for a, b in v.items() if a != 'poses'} for k, v in results.items()},
                      'combined_proposed_bound': final['combined_proposed_bound']}, indent=2))


if __name__ == '__main__':
    generate()
