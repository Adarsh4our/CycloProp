from cad import *
from datetime import datetime,timezone
STATE=TASK/'SECONDARY_MATERIAL_ASSIGNMENTS.json';assert not STATE.exists()
record=json.loads((TASK/'REVISED_NATIVE_MATERIAL_BOM.json').read_text())
d=getdoc(ASSEMBLY,2)
backup=TASK/'Recovery/Before_Secondary_Materials';backup.mkdir()
items=[]
aluminum=['Inner_Race_Retainer','Outer_Race_Retainer','Servo_X_Mount','Servo_Y_Mount','Carriage_Drive_Tab','Slider_Drive_Tab','Servo_Horn_R12','XY_Stop_Fixed_Bracket','XY_Stop_Moving_Arm','Servo_Link_L40','Upper_MainBearing_Retainer']
steel=['RB_M1','RB_M2','RB_M3','RB_M4','RB_Custom_M2','RB_Pivot_Pin','RB_XY_Stop_Follower','RB_Inner_Retainer_Spacer','RB_Savox_Output_Spline','RB_686ZZ','RB_DSH6','RB_DIN1481','RB_Pivot_Thrust_Spacer','RB_Ball_Mount_Spacer','6806 Ball^','6806 Outer ring^','6806 Inner ring^']
for row in record['rows']:
 if row['assigned_material'] or row['body_materials'] or row['mass_override']:continue
 name=row['part'];path=Path(row['path'])
 if path.parent!=OUT:continue # Virtual purchased bearing internals remain supplier holds; do not externalize or rewrite source.
 if any(token in name for token in aluminum):
  material='7075-T6 (SN)';basis='Selected provisional machined7075-T6 for bench prototype. Supplied alloy/temper, strength and fatigue remain unverified.'
 elif any(name.startswith(token) for token in steel):
  material='AISI 4340 Steel, normalized';basis='7850kg/m3 steel DENSITY PROXY for fastener, spacer or purchased/custom reference envelope. Not a selected/supplied4340 grade and NOT library strength approval. Supplier grade, heat treatment, finish and real geometry remain release holds.'
 else:continue
 items.append((row,material,basis))
s={'status':'IN PROGRESS','parts':{},'backup':str(backup),'limits':['Nominal14g servo override retained as explicitly manufacturer-based proxy, not hardware measurement','Unspecified blade composite, mixed-material guide blocks/rails and virtual6806 internals remain unassigned','Steel library is used as a density proxy only; do not use its strength for purchased-reference parts']};STATE.write_text(json.dumps(s,indent=2))
app.CommandInProgress=True
try:
 for row,material,basis in items:
  path=Path(row['path']);part=getdoc(path);assert row['configuration']=='Default'
  shutil.copy2(path,backup/path.name)
  if c(part,'GetSaveFlag'):assert c(part.Extension,'SaveAs',str(backup/('LIVE_BEFORE_'+path.name)),0,3,NULL,iref(),iref())
  before={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'material':row['assigned_material'],'mass_g':row['CAD_mass_each_g']}
  s.setdefault('attempts',{})[path.name]=before;STATE.write_text(json.dumps(s,indent=2))
  c(part,'SetMaterialPropertyName2','Default',MAT_DB,material)
  db=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'');assert c(part,'GetMaterialPropertyName2','Default',db)==material
  mp=c(part.Extension,'CreateMassProperty2');assert not c(mp,'GetOverrideOptions').OverrideMass
  expected=2810 if material.startswith('7075') else 7850
  assert abs(mp.Mass/mp.Volume-expected)<.01
  c(part.Extension.CustomPropertyManager(''),'Add3','MATERIAL_BASIS',30,basis,2)
  save(part)
  s['parts'][path.name]={'before':before,'material':material,'basis':basis,'mass_g':mp.Mass*1000,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};STATE.write_text(json.dumps(s,indent=2))
  print('SECONDARY_MATERIAL',path.name,round(mp.Mass*1000,3),flush=True)
 activate(d);assert c(d,'ForceRebuild3',False);save(d)
 s.update({'complete':True,'status':'Listed secondary material/density assumptions assigned and read back; not supplier/strength certification','assembly_sha256':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()});STATE.write_text(json.dumps(s,indent=2))
finally:app.CommandInProgress=False

