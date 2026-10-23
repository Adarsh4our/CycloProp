from cad import *
d=getdoc(ASSEMBLY,2)
ro=roots(d)
maps=json.loads((TASK/'REV_B_STATE.json').read_text())['maps']
r=[]
for key,mapping in maps.items():
    arm=ro['Blade_Pitch_Arm_Offset22p075_PROTOTYPE-'+key]
    blade=ro['Part1-'+{'1':'2','2':'1','3':'4','4':'3'}[key]]
    a,b=tf(arm),tf(blade)
    ar=np.array(a[:9]).reshape(3,3); br=np.array(b[:9]).reshape(3,3)
    origin=world(arm,[0.,0.,.00175])
    origin_b=(origin-np.array(b[9:12]))@br.T
    axis_b=ar[0]@br.T
    r.append({'link':key,'arm':arm.Name2,'blade':blade.Name2,'arm_crosshole_candidate_local_m':[0.,0.,.00175], 'blade_candidate_local_m':origin_b.tolist(),'blade_axis':axis_b.tolist()})
p=c(ro[next(iter(maps.values()))['OffsetArm']],'GetModelDoc2')
faces=[]
for body in c(p,'GetBodies2',0,False):
  for f in c(body,'GetFaces'):
    surf=c(f,'GetSurface')
    if c(surf,'IsCylinder'):faces.append({'cylinder':list(surf.CylinderParams),'face_box':list(c(f,'GetBox'))})
result={'candidates':r,'arm_cylinders':faces,'arm_exact_box':exact_box(c(p,'GetBodies2',0,False)[0]),'arm_body_count':len(c(p,'GetBodies2',0,False))}
(TASK/'ARM_RETENTION_INTERFACE_INSPECTION.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
