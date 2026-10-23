"""Feedback the defined blade and distributed linkage into development requirements."""
from pathlib import Path
import json
import math
import hashlib
import numpy as np
from mechanical_load_envelope import mechanism, evaluate
from define_bench_blade import sections

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT / 'CAD/Design_Completion'
FOLDER = TASK / 'Bench_Prototype'


def generate():
    blade = json.loads((FOLDER / 'BLADE_ROTOR_INTEGRATION.json').read_text())
    mass, d, jp = [blade[k] for k in ['mass_for_loads_kg', 'aft_COM_offset_for_loads_m', 'Jp_for_loads_kgm2']]
    omega = 2640 * np.pi / 30
    native_bom = json.loads((TASK / 'REVISED_NATIVE_MATERIAL_BOM.json').read_text())['rows']
    by_name = {r['part']: r['CAD_mass_each_g']/1000 for r in native_bom}
    rod_mass = by_name['RB_Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE.SLDPRT'] + 2 * (
        by_name['RB_Socket_Eye_D7_Sphere5p05_PROTOTYPE.SLDPRT'] + by_name['RB_Ball_Socket_Threaded_Retaining_Cap_PROTOTYPE.SLDPRT'])
    arm_mass = by_name['RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE.SLDPRT']
    arm_export = json.loads((FOLDER / 'ROTATING_ARM_MASS_PROPERTIES.json').read_text())
    arm = next(iter(arm_export['stations'].values()))
    total_rotating_mass = mass + arm['mass_kg']
    total_first = mass*d + arm['first_chord_mass_moment_kgm']
    total_j = jp + arm['Jp_kgm2']
    assert total_first > 0
    positions = [(0., 0.)] + [(radius*math.cos(a), radius*math.sin(a))
                              for radius in [.00344, .00688] for a in np.arange(16)*np.pi/8]
    rows = []
    for e in positions:
        g = mechanism(e, 1440)
        rigid = evaluate(e, total_rotating_mass, total_first/total_rotating_mass, total_j, 1440)
        phi = g['phase'][:, None] + np.arange(4)*np.pi/2
        a = phi - np.pi/2 + g['pitch']
        ar = np.stack([np.cos(a), np.sin(a)], axis=-1)
        at = np.stack([-np.sin(a), np.cos(a)], axis=-1)
        radial = np.stack([np.cos(phi), np.sin(phi)], axis=-1)
        a2 = -.095*radial + .012*(-ar*g['alpha_prime'][..., None]**2 + at*g['second'][..., None])
        b2 = -g['ring_r']
        cg2 = (a2+b2)/2
        rod_acc = float(np.max(np.linalg.norm(cg2, axis=-1))) * omega**2
        # Rod transverse inertia plus couple: Icg<=mL²/4 includes end-heavy sockets.
        L = .05652665325007647
        t = phi + math.radians(-15.825385589180533)
        b1 = .04*np.stack([-np.sin(t), np.cos(t)], axis=-1)
        a1 = .095*np.stack([-np.sin(phi), np.cos(phi)], axis=-1) + .012*at*g['alpha_prime'][..., None]
        u2 = (b2-a2)/L
        gamma2 = g['unit'][..., 0]*u2[..., 1] - g['unit'][..., 1]*u2[..., 0]
        rod_couple = rod_mass*L**2/4 * float(np.max(abs(gamma2))) * omega**2
        transverse_reaction = rod_mass*rod_acc + rod_couple/L
        correction_rod_force = transverse_reaction*(1+.012/g['min_lever'])
        # Require each manufactured blade's first moment to match nominal+/-5%,
        # and pitch inertia+/-10%. Do not replace this with perfect cancellation.
        variation = .05*(mass*d+abs(arm['first_chord_mass_moment_kgm']))*.095*omega**2 + .10*total_j*omega**2*float(np.max(abs(g['second'])))
        aero = .5*1.225*45**2*.220*.038**2*.30
        unknown = variation + abs(arm['first_normal_mass_moment_kgm'])*.095*omega**2 + aero + .002
        axis_force = np.array(rigid['peak_abs_ring_force_xy_N']) + np.array(rigid['unknown_hinge_to_axis_force_N_per_Nm'])*unknown
        axis_force += 4*transverse_reaction
        timing_torque = rigid['peak_abs_ring_torque_Nm'] + rigid['unknown_hinge_to_ring_torque_Nm_per_Nm']*unknown
        oldham_drag = 2*.15*timing_torque/.028
        axis_force += oldham_drag + 7.305 + 5
        rod_force = rigid['peak_abs_rod_force_N'] + unknown/g['min_lever'] + correction_rod_force
        rows.append({'XY_mm': [e[0]*1000, e[1]*1000], 'rod_force_N': float(rod_force),
                     'ring_torque_Nm': timing_torque, 'axis_force_xy_N': axis_force.tolist(),
                     'blade_and_arm_variation_hinge_bound_Nm': variation,
                     'rod_mass_kg': rod_mass, 'rod_acceleration_m_s2': rod_acc,
                     'rod_transverse_end_reaction_bound_N': transverse_reaction,
                     'rigid_blade_only': rigid})
    force = max(r['rod_force_N'] for r in rows)
    torque = max(r['ring_torque_Nm'] for r in rows)
    axis = max(max(r['axis_force_xy_N']) for r in rows)
    # The frame bound uses the permitted loaded pitch, not unrestricted90deg.
    outer, _ = sections()
    maximum_radius = 0.
    for x, y in outer.exterior.coords:
        dx = x - 9.5
        critical = math.atan2(dx, y)
        angles = [-math.radians(37.5), math.radians(37.5)]
        if -math.radians(37.5) <= critical <= math.radians(37.5):
            angles.append(critical)
        maximum_radius = max(maximum_radius, max(math.sqrt(95**2+dx**2+y**2+2*95*(dx*math.sin(p)+y*math.cos(p))) for p in angles))
    construction = json.loads((FOLDER / 'BLADE_CONSTRUCTION.json').read_text())
    flex = construction['bending_screen']['blade_midspan_deflection_mm']
    residual = math.hypot(105,85)-4 - maximum_radius - flex - 1.
    assert residual > 3.5
    # Post check deliberately retains a failed result when the revised loads
    # exceed the old 50N calculation; no unsupported release factor is applied.
    E = 205000.
    def compliance(root_d, root_h):
        H, stem = 44., 32.8
        I = math.pi*5.5**4/64
        Iroot = math.pi*root_d**4/64
        Ihead = math.pi*(20**4-13**4)/64
        return ((H**3-(H-root_h)**3)/Iroot + ((H-root_h)**3-(H-stem)**3)/I + (H-stem)**3/Ihead)/(3*E)
    original_post = axis*compliance(5.5,0)
    stepped_post = axis*compliance(12,8.5)
    post_residual = .620 - .090 - stepped_post
    cap_thread_area = math.pi*5.8*1.4/2
    bond_area = math.pi*2*2.5
    tube_i = math.pi/64*(2**4-1**4)
    euler = math.pi**2*70000*tube_i/46.52665325007647**2
    results = {
        'status': 'DEVELOPMENT SCREEN; NOT APPROVED LOADS OR PHYSICAL CAPACITY',
        'sources_sha256': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            FOLDER/'BLADE_ROTOR_INTEGRATION.json', TASK/'REVISED_NATIVE_MATERIAL_BOM.json', Path(__file__)]},
        'blade_mass_kg': mass, 'blade_aft_COM_m': d, 'blade_Jp_kgm2': jp,
        'sampling': '4blades,0.25deg azimuth; centre and e3.44/e6.88 at16directions; sampled study only',
        'peaks': {'rod_force_N':force,'ring_torque_Nm':torque,'axis_force_N':axis,
                  'static_joint_proof_proposal_N':1.5*force},
        'arm_and_rod': {'arm_and_clamped_hardware_mass_kg':arm['mass_kg'],
                       'arm_chord_first_mass_moment_kgm':arm['first_chord_mass_moment_kgm'],
                       'combined_pitch_inertia_kgm2':total_j,
                       'rod_mass_native_estimate_kg':rod_mass,'notes':'Exported arm/ball/spacers/fasteners partly counterbalance the blade aft mass moment; it is included with its actual sign. Explicit distributed rod acceleration/couple bounds. No structural flexibility or commanded XY acceleration included.'},
        'manufacturing_match_requirements': {'blade_first_mass_moment_relative':.05,'blade_Jp_relative':.10},
        'frame_bound': {'permitted_loaded_pitch_abs_deg':37.5,'maximum_undeformed_blade_radius_mm':maximum_radius,
                        'beam_deflection_screen_mm':flex,'additional_adverse_allowance_mm':1.,
                        'remaining_frame_gap_mm':residual,'required_mm':3.5,
                        'result':'passes conditional geometric bound if stiffness/pitch assumptions are met'},
        'post': {'original_deflection_mm':original_post,'D12_root_to8p5_candidate_deflection_mm':stepped_post,
                 'nominal_radial_gap_mm':.620,'other_tolerance_budget_mm':.090,'candidate_residual_mm':post_residual,
                 'proposed_minimum_mm':.25,'result':'passes study' if post_residual>=.25 else 'FAILS: reduce/narrow loads or redesign support before release'},
        'joint_screens': {'tube_E_assumption_GPa':70,'ideal_pinned_Euler_force_N':euler,
                          'Euler_over_operating_force':euler/force,'bond_average_shear_MPa':force/bond_area,
                          'proof_bond_average_shear_MPa':1.5*force/bond_area,
                          'cap_thread_average_shear_MPa':force/cap_thread_area,
                          'limits':'No CFRP modulus, adhesive allowables, thread root/peel/fatigue or host pin proof qualified.'},
        'actuator_selection': {'candidate':'ZaberNA23C60-T4A + X-MCC2 at48V',
                               'continuous_thrust_N':700,'travel_mm':60,'command_speed_proposed_mm_s':.25,
                               'thrust_curve_review':'Supplier chart reviewed: continuous thrust decays rapidly with speed; operate only in low-speed region and verify actual current/temperature/duty.',
                               'sizing_status':'force screen passes' if axis<700 else 'force screen fails',
                               'backlash_um':30,'accuracy_um':36,
                               'additional_requirements':'Calibrated actual XY position; native coupling/mounts and 44Hz disturbance holding/thermal proof remain required. Supplier700N does not qualify existing rails/post/threads.'},
        'pitch_tolerance_proposal': {'loaded_peak_target_deg':35,'loaded_error_allowance_deg':2.5,
                                   'budget_deg':{'timing':.25,'two_socket_joints':.65,'rod_length':.2,'actuator_and_guides':.5,'elastic':.6,'thermal_wear':.2,'nominal_calibration':.05,'measurement':.05},
                                   'notes':'Replaces the earlier unapproved+/-1deg draft for this candidate only. Requires approval; not an aerodynamic performance equivalence or a37.5deg command. Nominal35deg preserved.'},
        'poses': rows,
        'release_holds': ['Support load screen must pass, including dynamic amplification and actual arm inertia.',
                          'Actuator/coupling/guide mounting, loaded pitch and deflection must be verified.',
                          'Approve aero bounds, matched-blade tolerances, life/proof/temperatures and loaded pitch definition before release.',
                          'Supplier/process material allowables and physical joint/retention tests remain required.']}
    assert abs(sum(results['pitch_tolerance_proposal']['budget_deg'].values())-2.5)<1e-10
    (FOLDER/'BENCH_LOAD_TOLERANCE_STUDY.json').write_text(json.dumps(results,indent=2))
    print(json.dumps({k:v for k,v in results.items() if k not in ['poses','release_holds']},indent=2))


if __name__ == '__main__':
    generate()
