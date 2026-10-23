from cad import *

folder = TASK / 'Bench_Prototype'
d = getdoc(Path(json.loads((folder / 'ROTOR_ISOLATION.json').read_text())['assembly']), 2)
normalize = lambda name: '/'.join(p.removeprefix('BD_').removeprefix('RB_') for p in name.split('/'))
ro = {normalize(co.Name2): co for co in c(d, 'GetComponents', True)}
mapping = json.loads((TASK / 'REV_B_STATE.json').read_text())['maps']
replacements = json.loads((TASK / 'ARM_SCREW_LENGTH_CORRECTION.json').read_text())['replacements']
roles = ['OffsetArm','ArmBall','ArmMountSpacer','ArmOuterSpacer','ArmHeadWasher','ArmScrew','ArmNutWasher','ArmNut']
stations = {}
cache = {}
arms = [co for name, co in ro.items() if name.startswith('Blade_Pitch_Arm_Offset22p075_PROTOTYPE-')]
for key, values in mapping.items():
    ball = ro[values['ArmBall']]
    arm = min(arms, key=lambda co: np.linalg.norm(world(co,[0.,0.,0.])-world(ball,[0.,0.,0.])))
    arm_position = world(arm, [0.,0.,0.])
    candidates = [(float(np.linalg.norm(world(co,[.0095,0.,0.])-arm_position)), co)
                  for name, co in ro.items() if name.startswith('Part1-')]
    blade = min(candidates, key=lambda item:item[0])[1]
    bt = tf(blade)
    blade_rotation = np.array(bt[:9]).reshape(3,3)
    pivot = world(blade,[.0095,0.,0.])
    rows = []
    for role in roles:
        name = normalize(arm.Name2) if role == 'OffsetArm' else (normalize(replacements[key]['new']) if role == 'ArmScrew' else values[role])
        co = ro[name]
        path = c(co,'GetPathName')
        if path not in cache:
            part = c(co,'GetModelDoc2')
            mp = c(part.Extension,'CreateMassProperty2')
            assert not c(mp,'GetOverrideOptions').OverrideMass
            density = mp.Mass/mp.Volume
            assert 2000 < density < 8200, (name,density)
            cache[path] = (density,[list(c(body,'GetMassProperties',density)) for body in c(part,'GetBodies2',0,False)])
        density, properties = cache[path]
        t = tf(co)
        rotation = np.array(t[:9]).reshape(3,3)
        for p in properties:
            m = p[5]
            cg = np.array(p[:3]) @ rotation + np.array(t[9:12])
            rel = (cg-pivot) @ blade_rotation.T
            q = rotation[:,2]
            # All included axes are Cartesian relative to global shaftZ.
            assert abs(max(abs(q))-1) < 1e-6, (name,q)
            intrinsic = p[6+int(np.argmax(abs(q)))]
            jp = intrinsic+m*(rel[0]**2+rel[1]**2)
            rows.append({'role':role,'component':co.Name2,'mass_kg':m,
                         'COM_in_blade_coordinates_m':rel.tolist(),'Jp_kgm2':jp,
                         'source':path,'density_kg_m3':density})
    stations[key] = {'blade':blade.Name2,'parts':rows,'mass_kg':sum(r['mass_kg'] for r in rows),
                     'first_chord_mass_moment_kgm':sum(r['mass_kg']*r['COM_in_blade_coordinates_m'][0] for r in rows),
                     'first_normal_mass_moment_kgm':sum(r['mass_kg']*r['COM_in_blade_coordinates_m'][1] for r in rows),
                     'Jp_kgm2':sum(r['Jp_kgm2'] for r in rows)}
result={'status':'NATIVE GEOMETRY/DENSITY ESTIMATE; NOT MEASURED HARDWARE', 'stations':stations,
        'basis':'Pitch arm plus clamped arm-end ball/spacers/bolt/washers/nut. Positions mapped into the blade chord frame. Socket/tube mass belongs to the distributed rod calculation.'}
(folder/'ROTATING_ARM_MASS_PROPERTIES.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:{a:b for a,b in v.items() if a!='parts'} for k,v in stations.items()},indent=2),flush=True)
