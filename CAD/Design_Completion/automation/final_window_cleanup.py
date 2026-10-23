from cad import *
from datetime import datetime,timezone
assembly=getdoc(ASSEMBLY,2);activate(assembly)
recovery=TASK/'Recovery'/('Final_Window_Cleanup_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));recovery.mkdir()
docs=[];doc=c(app,'GetFirstDocument')
while doc:
 if doc.Visible and Path(c(doc,'GetPathName'))!=ASSEMBLY:docs.append(doc)
 doc=c(doc,'GetNext')
rows=[];left=[]
for i,doc in enumerate(docs):
 path=Path(c(doc,'GetPathName'));title=c(doc,'GetTitle')
 if not path.is_relative_to(TASK) and path!=ROOT/'CAD/Rotor_Integration/Ball_Link_Prototype/Socket_Cavity_Tool_D5p05.SLDPRT':left.append(str(path));continue
 row={'source':str(path),'title':title,'dirty_before':bool(c(doc,'GetSaveFlag'))}
 if row['dirty_before']:
  target=recovery/(str(i)+'_'+path.name)
  assert c(doc.Extension,'SaveAs',str(target),0,3,NULL,iref(),iref());row['preserved_live_copy']=str(target)
 c(app,'CloseDoc',title);rows.append(row);print('CLOSED_UNUSED_WINDOW',title,flush=True)
activate(assembly)
result={'closed':rows,'unrelated_windows_left':left,'working_assembly_left_open':str(ASSEMBLY),'assembly_save_flag':bool(c(assembly,'GetSaveFlag')),'assembly_sha256':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()}
(TASK/'FINAL_WINDOW_CLEANUP.json').write_text(json.dumps(result,indent=2));print('FINAL_WINDOW_CLEANUP_COMPLETE',len(rows),'assembly_dirty',result['assembly_save_flag'],flush=True)
