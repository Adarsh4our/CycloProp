from pathlib import Path
import json,csv,hashlib,datetime,shutil
p=Path('CAD/Design_Completion');updates=json.loads((p/'SECONDARY_MATERIAL_ASSIGNMENTS.json').read_text());assert updates['complete']
s=json.loads((p/'REVISED_NATIVE_MATERIAL_BOM.json').read_text())
for suffix in ['json','csv']:
 src=p/('REVISED_NATIVE_MATERIAL_BOM.'+suffix);dst=Path(updates['backup'])/src.name
 assert not dst.exists();shutil.copy2(src,dst)
for row in s['rows']:
 if row['part'] not in updates['parts']:continue
 u=updates['parts'][row['part']];assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==u['sha256']
 row.update({'assigned_material':u['material'],'database':'SOLIDWORKS Materials','CAD_mass_each_g':u['mass_g'],'CAD_mass_quantity_g':u['mass_g']*row['quantity'],'effective_density_kg_m3':u['mass_g']/row['volume_mm3']*1e6,'status':u['basis'],'mass_override':False})
for row in s['rows']:
 if row['part']=='RB_Savox_SH0257MG_INTERFACE_REFERENCE.SLDPRT':row['status']='Retained14g manufacturer nominal mass override for SH0257MG+ reference; older modeled case envelope and delivered hardware remain unverified. SOURCE: https://www.teamsavox.com/product/sh-0257mgp/'
s['sum_native_leaf_masses_g']=sum(row['CAD_mass_quantity_g'] for row in s['rows'])
s['unassigned_parts']=[row['part'] for row in s['rows'] if not row['assigned_material'] and not row['body_materials']]
s['secondary_material_reconciliation']='Same native part/configuration quantities/volumes, updated from per-part read-back and saved hashes in SECONDARY_MATERIAL_ASSIGNMENTS.json; geometry/configuration counts unchanged.'
s['secondary_capture_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s['assembly_sha256']=hashlib.sha256(Path(s['assembly']).read_bytes()).hexdigest()
(p/'REVISED_NATIVE_MATERIAL_BOM.json').write_text(json.dumps(s,indent=2))
with (p/'REVISED_NATIVE_MATERIAL_BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=list(s['rows'][0]));writer.writeheader();writer.writerows(s['rows'])
print('RECONCILED_NATIVE_LEAF_SUM_G',s['sum_native_leaf_masses_g'],'UNASSIGNED',s['unassigned_parts'])
