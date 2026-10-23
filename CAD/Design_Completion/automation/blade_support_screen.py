from pathlib import Path
import math, json, urllib.request, hashlib
task = Path('CAD/Design_Completion')
folder = task / 'Manufacturer_References'
folder.mkdir(exist_ok=True)
sources = {
    'F693ZZ_supplier.pdf': 'https://www.smbbearings.com/firebrick/ckeditor/plugins/upload/Uploads/Documents/bearingpdfs/F693ZZ-flanged-miniature-bearing-3x8x4mm.pdf',
    'igus_J_catalogue.pdf': 'https://www.igus.com/us/pdf/j.pdf'}
records = {}
for name, url in sources.items():
    path = folder / name
    if not path.exists():
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read()
        assert data.startswith(b'%PDF'), name
        path.write_bytes(data)
    records[name] = {'url': url, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
omega = 2640 * math.pi / 30
blade_mass = .0125
blade_R = .095
arm_mass = 897.1147819341584 * .00281 / 1000
arm_R_bound = .110
rod_force = json.loads((task / 'INERTIA_LOAD_SCREEN.json').read_text())['peak_abs_rod_force_N']
reaction = blade_mass * blade_R * omega ** 2 / 2 + arm_mass * arm_R_bound * omega ** 2 + rod_force
speed = .0015 * math.radians(35) * omega
plain_pressure = reaction / (3 * 2.25)
result = {'status': 'PRELIMINARY SELECTION SCREEN; NOT APPROVED LOAD CASES OR BEARING LIFE',
          'blade_mass_assumption_g': 12.5, 'blade_COM_radius_assumption_mm': 95.,
          'arm_geometry_volume_mm3': 897.1147819341584, 'arm_density_assumption_kg_m3': 2810.,
          'arm_mass_from_volume_g': arm_mass * 1000, 'arm_COM_radius_bound_mm': arm_R_bound * 1000,
          'assumptions': ['Uniform span blade gives half centrifugal reaction at each end.',
                          'Mechanism end additionally carries full conservative arm centrifugal load and peak pitch-rod force.',
                          'Centrifugal, arm and rod reactions are added as positive scalar bounds; correlations not credited.',
                          'Aero loads, blade COM offset, trunnion bending, impact and measured mass/inertia remain external inputs.'],
          'mechanism_end_reaction_scale_N': reaction,
          'plain_bearing_D3_L2p25_pressure_MPa': plain_pressure,
          'sinusoidal_pitch_journal_speed_peak_m_s': speed,
          'plain_bearing_peak_pv_scale_MPa_m_s': plain_pressure * speed,
          'F693ZZ': {'bore_mm': 3., 'OD_mm': 8., 'width_mm': 4., 'flange_OD_mm': 9.5, 'flange_width_mm': .9,
                      'source_static_rating_N': 18 * 9.80665, 'source_dynamic_rating_N': 55 * 9.80665,
                      'static_rating_over_reaction_scale': 18 * 9.80665 / reaction,
                      'note': 'Supplier rotation speed rating is not approval for44Hz oscillatory pitch; grease redistribution, fretting/false brinelling and full life remain validation holds.'},
          'decision': 'Evaluate positively retained F693ZZ cartridge layout instead of unreconciled JFM-0306-04 claim. No endplate holes changed by this screen.',
          'sources': records}
assert result['F693ZZ']['static_rating_over_reaction_scale'] > 2.
(task / 'BLADE_SUPPORT_SELECTION_SCREEN.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
