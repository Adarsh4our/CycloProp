from cad import *
STATE=TASK/'ARM_SCREW_LENGTH_CORRECTION.json';assert not STATE.exists()
d=getdoc(ASSEMBLY,2);activate(d)
ro=roots(d);maps=json.loads((TASK/'REV_B_STATE.json').read_text())['maps']
old={k:ro[v['ArmScrew']] for k,v in maps.items()}
new_path=OUT/'RB_M2x12_Socket_Cap_REFERENCE.SLDPRT'
inspection=json.loads((TASK/'ARM_FASTENER_REPLACEMENT_INSPECTION.json').read_text());before=inspection['RB_M2x10_Ball_Compact_Screw_REFERENCE'];after=inspection['RB_M2x12_Socket_Cap_REFERENCE']
assert abs((after['volume_mm3']-before['volume_mm3'])-math.pi*2)<1e-5
recovery=TASK/'Recovery/Before_Arm_M2x12';recovery.mkdir()
assert c(d.Extension,'SaveAs',str(recovery/ASSEMBLY.name),0,3,NULL,iref(),iref())
s={'status':'IN PROGRESS','backup':str(recovery),'replacements':{},'before_transforms':{name:tf(co) for name,co in ro.items()}}
STATE.write_text(json.dumps(s,indent=2))
app.CommandInProgress=True
try:
 for k,co in old.items():
  old_name=co.Name2;old_t=tf(co);names=set(roots(d))
  c(d,'ClearSelection2',True);assert c(co,'Select4',False,NULL,False)
  assert c(d,'ReplaceComponents2',str(new_path),'Default',False,1,True),(k,'replace failed')
  assert c(d,'ForceRebuild3',False)
  current=roots(d);added=set(current)-names
  assert len(added)==1,(k,added)
  key=next(iter(added));replacement=current[key]
  assert Path(c(replacement,'GetPathName'))==new_path
  assert np.max(abs(np.array(tf(replacement))-old_t))<1e-6,(k,'pose changed')
  s['replacements'][k]={'old':old_name,'new':replacement.Name2,'transform':tf(replacement)}
  STATE.write_text(json.dumps(s,indent=2));print('ARM_SCREW_REPLACED',k,replacement.Name2,flush=True)
 current=roots(d)
 replaced_logical={logical(v['old']) for v in s['replacements'].values()}
 for name,t in s['before_transforms'].items():
  if name not in replaced_logical:assert np.max(abs(np.array(tf(current[name]))-t))<1e-6,name
 s['mate_errors']=errors(active_mates(d));STATE.write_text(json.dumps(s,indent=2));assert not s['mate_errors'],s['mate_errors']
 save(d);s.update({'complete':True,'status':'Four arm-side M2x10 replaced by existingM2x12 reference; ring-side blind screws unchanged. Native poses/rebuild/mates checked; collision check pending.','nominal_nut_protrusion_before_mm':.3,'nominal_nut_protrusion_after_mm':2.3,'assembly_sha256':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest(),'holds':['Actual bolt/nut tolerances, end lead-in, grade, torque/locking and tool access still require release']});STATE.write_text(json.dumps(s,indent=2))
finally:app.CommandInProgress=False
