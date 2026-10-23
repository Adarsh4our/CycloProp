"""Separate manufacturing candidate; never edits baseline inputs or legacy CAD."""
from pathlib import Path
import json
import math
import hashlib
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'CAD/Design_Completion/Bench_Prototype'


def section_moments(poly):
    """Area, first x moment and second moments, in mm units, using Green's theorem."""
    poly = orient(poly, sign=1)
    area = sx = ixx = iyy = 0.
    for ring in [poly.exterior, *poly.interiors]:
        points = np.array(ring.coords)
        x, y = points[:-1].T
        u, v = points[1:].T
        cross = x * v - u * y
        area += cross.sum() / 2
        sx += ((x + u) * cross).sum() / 6
        ixx += ((y*y + y*v + v*v) * cross).sum() / 12
        iyy += ((x*x + x*u + u*u) * cross).sum() / 12
    assert abs(area - poly.area) < 1e-8
    return {'area_mm2': float(area), 'centroid_x_mm': float(sx / area),
            'I_about_chord_mm4': float(ixx),
            'polar_about_quarter_chord_mm4': float(ixx + iyy - 2 * 9.5 * sx + 9.5**2 * area)}


def sections():
    x = 38 * (1 - np.cos(np.linspace(0, np.pi, 81))) / 2
    q = x / 38
    y = 5 * .12 * 38 * (.2969*np.sqrt(q) - .126*q - .3516*q*q + .2843*q**3 - .1015*q**4)
    outer = Polygon(list(zip(x, y)) + list(zip(x[::-1], -y[::-1]))[:-1])
    inner = outer.buffer(-.25, join_style='mitre')
    shell = outer.difference(inner)
    # UD caps aft of the spar avoid a cap/spar solid intersection.
    inner_band = inner.difference(inner.buffer(-.40, join_style='mitre'))
    upper_cap = inner_band.intersection(box(12, 0, 22, 3))
    lower_cap = inner_band.intersection(box(12, -3, 22, 0))
    spar_od = Point(9.5, 0).buffer(1.75, quad_segs=40)
    spar_id = Point(9.5, 0).buffer(1.25, quad_segs=40)
    spar = spar_od.difference(spar_id)
    foam = inner.difference(spar_od.buffer(.05)).difference(upper_cap).difference(lower_cap)
    # Foam machining tolerance exceeds5um; remove Boolean sliver edges that
    # otherwise fall below the native sketch kernel's curve tolerances.
    foam = foam.simplify(.005, preserve_topology=True)
    result = {'skin': shell, 'UD_upper': upper_cap, 'UD_lower': lower_cap, 'spar': spar, 'core': foam}
    assert all(p.is_valid and p.geom_type == 'Polygon' and p.area > 0 for p in result.values())
    assert inner.contains(spar_od)
    assert not upper_cap.intersects(spar_od) and not lower_cap.intersects(spar_od)
    assert abs(outer.bounds[2] - 38) < 1e-9
    return outer, result


def generate():
    OUT.mkdir(exist_ok=True)
    # Analytic tests are independent of airfoil construction.
    test = section_moments(box(0, -1, 2, 1))
    assert abs(test['area_mm2'] - 4) < 1e-12
    assert abs(test['centroid_x_mm'] - 1) < 1e-12
    assert abs(test['I_about_chord_mm4'] - 4/3) < 1e-12
    outer, profiles = sections()
    density = {'skin': 1550, 'UD_upper': 1550, 'UD_lower': 1550, 'spar': 1550, 'core': 52}
    rows = {}
    total = first = inertia = bending_EI = 0.
    for name, poly in profiles.items():
        moment = section_moments(poly)
        mass = poly.area * 220 * density[name] * 1e-9
        j = moment['polar_about_quarter_chord_mm4'] * 220 * density[name] * 1e-15
        e = 100e9 if name.startswith('UD') else (40e9 if name != 'core' else 0)
        ei = e * moment['I_about_chord_mm4'] * 1e-12
        rows[name] = {**moment, 'density_kg_m3': density[name], 'mass_kg': mass,
                      'pitch_inertia_about_pivot_kgm2': j, 'span_mm': 220,
                      'bending_E_assumption_Pa': e, 'EI_Nm2': ei,
                      'exterior_mm': list(poly.exterior.coords),
                      'interiors_mm': [list(r.coords) for r in poly.interiors]}
        total += mass
        first += mass * (moment['centroid_x_mm'] - 9.5) / 1000
        inertia += j
        bending_EI += ei
    # Two steel end fittings: D3x12 journal and D2.4x30 bond stem.
    # Full cylinders conservatively retain material omitted by the flat/crosshole.
    end_mass = 2 * (math.pi/4 * 3**2 * 12 + math.pi/4 * 2.4**2 * 30) * 7850e-9
    end_j = 2 * 7850e-15 * math.pi/32 * (3**4 * 12 + 2.4**4 * 30)
    # Controlled process allowance, not a hidden CAD density or mass override.
    adhesive_mass = .0005
    total += end_mass + adhesive_mass
    first += adhesive_mass * .010  # Conservative aft location of seam/secondary adhesive.
    inertia += end_j + adhesive_mass * .010**2
    omega = 2640 * np.pi / 30
    centrifugal = total * .095 * omega**2
    aero = .5 * 1.225 * 45**2 * .220 * .038 * 2
    transverse = centrifugal + aero
    # Simply supported uniform transverse load. No laminate certification implied.
    deflection = 5 * transverse * .220**3 / (384 * bending_EI)
    state = {'status': 'DEFINED MANUFACTURING CANDIDATE; NOT INTEGRATED OR FABRICATION RELEASED',
             'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'aerodynamic_profile': 'NACA0012 standard finite-TE polynomial, chord38mm; 80 cosine intervals per surface',
             'span_mm': 220, 'pivot_mm': [9.5, 0], 'skin_thickness_nominal_mm': .25,
             'skin_process': 'Two90gsm woven carbon plies, span/chord balanced; matched mould, vacuum consolidated. Qualify0.20..0.30mm cured skin on coupons.',
             'cap_process': '0.40mm cured UD carbon reinforcements along span; x12..22mm each inner face; qualify layup/thickness/resin fraction.',
             'spar_definition': 'CFRP tube OD3.5 ID2.5 L220, quarter-chord axis; fiber architecture and torsional modulus require supplier evidence.',
             'trunnion_definition': '4340 normalized proposal: D3 journal12mm outboard, D2.4 stem30mm bonded into ID2.5 spar. Lower external flat/crosshole must match retained arm datum; drawing pending.',
             'bond_process': '0.05mm radial stem gap;30mm engagement. Isolate steel/carbon electrically; qualify surface treatment, epoxy, cure, gap, voids and pullout/torsion coupons.',
             'profiles': rows, 'two_metal_fittings_mass_kg': end_mass,
             'adhesive_process_allowance_kg': adhesive_mass,
             'assembled_mass_estimate_kg': total, 'aft_COM_offset_m': first / total,
             'first_mass_moment_kgm': first, 'pitch_inertia_kgm2': inertia,
             'bending_screen': {'EI_Nm2': bending_EI, 'load_N': transverse,
                                'blade_midspan_deflection_mm': deflection * 1000,
                                'assumptions': 'Perfect skin/cap/spar bonding, E40GPa balanced skins/spar, E100GPa UD; foam stiffness ignored; ends simple supports. Actual orthotropic bending/torsion, buckling, local shell and root transfer unverified.',
                                'status': 'Study only; not a laminate strength or loaded-clearance pass'},
             'manufacturing_holds': ['Supplier laminate, spar and adhesive properties/process approval',
                                     'Airfoil deviation from native proxy and production profile gauge',
                                     'Trunnion fatigue with actual flat/crosshole and root bending',
                                     'Bearing/journal fits, measured endfloat, arm retention and bond test',
                                     'Skin/core separation, beam torsion, balance and temperature qualification'],
             'self_checks': 'Polygon moments agree with rectangle identities; valid disjoint profiles; spar inside skin; chord preserved.'}
    (OUT / 'BLADE_CONSTRUCTION.json').write_text(json.dumps(state, indent=2))
    # 2D source profile for independent manufacture/mould checking.
    with (OUT / 'NACA0012_PROFILE.csv').open('w') as f:
        f.write('x_mm,y_mm\n')
        for x, y in outer.exterior.coords:
            f.write(f'{x:.9f},{y:.9f}\n')
    print(json.dumps({k: v for k, v in state.items() if k not in ['profiles', 'manufacturing_holds']}, indent=2))


if __name__ == '__main__':
    generate()
