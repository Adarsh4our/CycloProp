from cad import *
import csv
from collections import Counter
from datetime import datetime,timezone
assert json.loads((TASK/'MATERIAL_CORRECTION_STATE.json').read_text())['complete']
d=getdoc(ASSEMBLY,2);activate(d)
counts=Counter();documents={};unresolved=[]
for co in c(d,'GetComponents',False):
 if c(co,'GetSuppression')==0:continue
 part=c(co,'GetModelDoc2')
 if part is None:
  unresolved.append(co.Name2);continue
 if c(part,'GetType')!=1:continue
 key=(c(co,'GetPathName'),co.ReferencedConfiguration)
 counts[key]+=1;documents[key]=part
rows=[]
for (path,config),quantity in counts.items():
 part=documents[(path,config)];previous=part.ConfigurationManager.ActiveConfiguration.Name
 if previous!=config:assert c(part,'ShowConfiguration2',config)
 try:
  db=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
  material=c(part,'GetMaterialPropertyName2',config,db)
  mp=c(part.Extension,'CreateMassProperty2');override=bool(c(mp,'GetOverrideOptions').OverrideMass)
  volume=mp.Volume*1e9;mass=mp.Mass*1000
  name=Path(path).name
  bodies=[]
  for body in c(part,'GetBodies2',0,False) or []:
   bd=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
   bodies.append(c(body,'GetMaterialPropertyName',config,bd))
  status='Unassigned: default/proxy mass not hardware evidence' if not material and not any(bodies) else 'Assigned density/geometry CAD estimate; not measured or certified'
  if override:status='Mass override present: requires individual basis'
  if 'Part1.' in name:status='Blade monolithic geometry proxy; composite and metal trunnion construction/mass unverified'
  if any(x in name for x in ['REFERENCE','ENVELOPE','LAYOUT','6806','MGN5','MGNR']):status+='; purchased/custom reference-envelope properties need supplier reconciliation'
  rows.append({'part':name,'path':path,'configuration':config,'quantity':quantity,'assigned_material':material or '', 'database':db.value,'body_materials':';'.join(str(x) for x in bodies),'mass_override':override,'volume_mm3':volume,'CAD_mass_each_g':mass,'CAD_mass_quantity_g':quantity*mass,'effective_density_kg_m3':mass/volume*1e6 if volume else None,'status':status})
 finally:
  if previous!=config:assert c(part,'ShowConfiguration2',previous)
 if len(rows)%15==0:print('MATERIAL_REGISTER_ROWS',len(rows),flush=True)
result={'status':'Native part/configuration inventory; includes unresolved material/reference proxies, NOT a measured or fabrication-released assembly mass','captured_utc':datetime.now(timezone.utc).isoformat(),'assembly':str(ASSEMBLY),'assembly_sha256':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest(),'rows':rows,'unresolved_components':unresolved,'leaf_instance_count':sum(counts.values()),'sum_native_leaf_masses_g':sum(x['CAD_mass_quantity_g'] for x in rows),'mass_overrides':[x['part'] for x in rows if x['mass_override']],'unassigned_parts':[x['part'] for x in rows if not x['assigned_material'] and not x['body_materials']],'limits':['Loaded active leaf configurations only; suppressed configurations not certified','Solid reference envelopes may overstate real purchased geometry, while unassigned density may understate hardware mass','Parent assembly mass overrides/excluded component settings not used to hide or correct leaf results','No measured hardware mass, certified grade or actual composite construction inferred']}
(TASK/'REVISED_NATIVE_MATERIAL_BOM.json').write_text(json.dumps(result,indent=2))
with (TASK/'REVISED_NATIVE_MATERIAL_BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('REGISTER_SUMMARY',len(rows),sum(counts.values()),'native_leaf_sum_g',result['sum_native_leaf_masses_g'],'overrides',result['mass_overrides'],'unassigned',result['unassigned_parts'],flush=True)
