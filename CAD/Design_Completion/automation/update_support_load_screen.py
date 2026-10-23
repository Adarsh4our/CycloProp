from pathlib import Path
import json, math
task = Path('CAD/Design_Completion')
old = json.loads((task / 'PACKAGING_CALCULATIONS.json').read_text())['central_support']
inertia = json.loads((task / 'INERTIA_LOAD_SCREEN.json').read_text())
coupling = json.loads((task / 'COUPLING_GEOMETRIC_BOUNDS.json').read_text())
force = 50.
compliance = old['elastic_tip_deflection_mm'] / old['assumed_transverse_force_N']
budget = dict(old['adverse_radial_budget_mm'])
budget['deflection_allowance'] = .20
gap = old['nominal_radial_gap_mm'] - sum(budget.values())
stress = force * 44. / (math.pi * 5.5 ** 3 / 32)
r = {'status': 'PROVISIONAL INERTIA-INFORMED SUPPORT SCREEN; NOT APPROVED OPERATING LOADS',
     'supersedes': '20N support-load study in PACKAGING_CALCULATIONS.json; nominal geometry unchanged',
     'reason': 'Subsequent blade pitch inertia and relieved floating-member mass give larger reaction scale than original20N assumption.',
     'ring_pitch_inertia_peak_N': inertia['peak_ring_force_norm_N'],
     'floating_inertia_peak_N': coupling['floating_inertial_force_N'],
     'triangle_sum_reaction_scale_N': inertia['peak_ring_force_norm_N'] + coupling['floating_inertial_force_N'],
     'study_force_N': force, 'force_height_mm': 44., 'post_diameter_mm': 5.5,
     'elastic_tip_deflection_mm': force * compliance, 'nominal_gap_mm': old['nominal_radial_gap_mm'],
     'adverse_budget_mm': budget, 'remaining_gap_mm': gap,
     'root_nominal_bending_stress_MPa': stress, 'assumed_Kt': 2., 'library_static_yield_factor': 710 / (2 * stress),
     'limits': ['Reaction scale is a conservative triangle sum, not a complete coupled bearing-load solution.',
                'Aero, imbalance, jams, fatigue and cage modes require approved load cases and physical validation.',
                'The deflection allowance changed explicitly from0.15 to0.20mm; residual rigid clearance reduced from0.32 to0.27mm.',
                'Library normalized4340 properties are provisional; supplied condition, post root fillet and machining tolerances require release.']}
assert r['elastic_tip_deflection_mm'] < budget['deflection_allowance']
assert gap > .25
(task / 'FRAME_SUPPORT_LOAD_UPDATE.json').write_text(json.dumps(r, indent=2))
print(json.dumps(r, indent=2))
