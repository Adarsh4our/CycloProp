from pathlib import Path
import json, math

task = Path('CAD/Design_Completion')
parts = json.loads((task / 'PART_BUILD_RECORD.json').read_text())
eccentricity = 6.88
omega = 2640 * math.pi / 30
floating_g = parts['RB_Oldham_Floating_Disk_PROTOTYPE']['mass_g']
r = {
    'scope': 'Conservative nominal geometric bounds for selected planar Oldham arrangement; not a substitute for native interference checks',
    'eccentricity_max_mm': eccentricity,
    'tongue_width_mm': 4., 'slot_width_mm': 4.1,
    'axial_face_gap_each_mm': .2, 'tongue_axial_engagement_mm': 1.8,
    'maximum_longitudinal_slide_each_interface_mm': eccentricity,
    'tongue_nominal_radial_interval_mm': [28., 38.],
    'floating_channel_radial_interval_mm': [math.sqrt(20 ** 2 - 2 ** 2), 44.],
    'minimum_longitudinal_tongue_contact_bound_mm': 44. - (28. + eccentricity),
    'minimum_central_pedestal_clearance_bound_mm': 20. - eccentricity - 11.,
    'input_bore_to_cap_head_radial_clearance_bound_mm': 12. - (8.3 + 1.9),
    'input_bridge_to_cap_head_axial_gap_mm': 51.9 - (47.8 + 2.),
    'output_underside_to_rod_mount_head_axial_gap_mm': 39.5 - 38.8,
    'floating_mass_native_g': floating_g,
    'floating_centre_peak_acceleration_m_s2': 2 * eccentricity / 1000 * omega ** 2,
    'floating_inertial_force_N': floating_g / 1000 * 2 * eccentricity / 1000 * omega ** 2,
    'angular_free_play_screen_deg': math.degrees(2 * math.atan((4.1 - 4.) / (2 * 28.))),
    'free_play_screen_assumptions': 'Each pair of opposed tongues may rock through nominal diametral side clearance over minimum28mm lever. Two stages add worst-direction play; excludes pilot, pin, bearing and guide play.',
    'release_holds': ['Native poses must demonstrate the selected branch and intended phase.',
                      '0.7mm head/plate gap requires axial tolerance and loaded deflection budget.',
                      'Slot/tongue width tolerances, edge radii and surface treatment allowances not released.',
                      'Nominal pitch margin0.009deg is less than coupling play screen; literal35deg limit remains unverified.',
                      'POM pressure/velocity, creep, wear, balance and fatigue at2640RPM require approved loads and tests.']}
assert r['minimum_longitudinal_tongue_contact_bound_mm'] > 9.
assert r['minimum_central_pedestal_clearance_bound_mm'] > 2.
(task / 'COUPLING_GEOMETRIC_BOUNDS.json').write_text(json.dumps(r, indent=2))
print(json.dumps(r, indent=2))
