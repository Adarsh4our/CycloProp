from cad import *
from datetime import datetime,timezone
STATE=TASK/'ASSEMBLY_BOM_DRAWING_STATE.json';s=json.loads(STATE.read_text());source=getdoc(ASSEMBLY,2);activate(source)
s['final_assembly_save_flag']=bool(c(source,'GetSaveFlag'));assert not s['final_assembly_save_flag']
s['final_source_sha256']=hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest();assert s['final_source_sha256']==s['source_sha256']
s['saved_utc']=datetime.now(timezone.utc).isoformat()
checkpoint=json.loads((TASK/'CURRENT_IMPLEMENTATION_CHECKPOINT.json').read_text());changed=[];count=0
for name,record in checkpoint['manifest'].items():
 if Path(name).suffix.upper() not in ('.SLDPRT','.SLDASM'):continue
 count+=1
 if hashlib.sha256((TASK/name).read_bytes()).hexdigest()!=record['sha256']:changed.append(name)
assert set(changed).issubset({'RevB_Isolated\\RB_Assem20_Design_RevB.SLDASM'}),changed
# The current clean assembly differed from the older checkpoint before this task; preserve it, do not revert user/source changes.
assert s['source_sha256']==s['final_source_sha256']
s['geometry_file_preservation']={'native_model_files_compared_to_earlier_checkpoint':count,'files_already_different_before_task':changed,'source_assembly_unchanged_during_this_task':True,'parts_matching_earlier_checkpoint':count-len(changed),'scope':'BOM generation changed no source model files. A different assembly-file hash was already present at task start; its cause/geometry differences were not inferred or reviewed.'}
s['baseline_sha256']=hashlib.sha256((ROOT/'config/baseline.json').read_bytes()).hexdigest();assert s['baseline_sha256']==checkpoint['baseline_sha256']
s['working_assembly_left_open']=True;s['new_drawing_window_closed']=c(app,'GetOpenDocumentByName',s['drawing']) is None
assert s['new_drawing_window_closed']
STATE.write_text(json.dumps(s,indent=2));print('BOM_TASK_FINAL_CHECK',count,'model files compared; task source and baseline unchanged; drawing closed; assembly clean',flush=True)
