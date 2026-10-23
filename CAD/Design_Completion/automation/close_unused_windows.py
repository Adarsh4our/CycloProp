from cad import *
from datetime import datetime,timezone
assembly=getdoc(ASSEMBLY,2);activate(assembly)
recovery=TASK/'Recovery'/('Window_Cleanup_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));recovery.mkdir()
rows=[];docs=[];doc=c(app,'GetFirstDocument')
while doc:
 if doc.Visible and c(doc,'GetPathName')!=str(ASSEMBLY):docs.append(doc)
 doc=c(doc,'GetNext')
for doc in docs:
 path=Path(c(doc,'GetPathName'));title=c(doc,'GetTitle')
 assert path.parent==OUT or path==ROOT/'CAD/Rotor_Integration/Ball_Link_Prototype/Socket_Cavity_Tool_D5p05.SLDPRT',path
 row={'title':title,'source':str(path),'dirty':bool(c(doc,'GetSaveFlag')),'source_disk_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 if row['dirty']:
  target=recovery/path.name
  assert c(doc.Extension,'SaveAs',str(target),0,3,NULL,iref(),iref())
  row['live_copy']=str(target);row['live_copy_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
 c(app,'CloseDoc',title);rows.append(row)
 (TASK/'WINDOW_CLEANUP_STATE.json').write_text(json.dumps({'closed':rows,'recovery':str(recovery)},indent=2))
 print('CLOSED_UNUSED_WINDOW',title,flush=True)
activate(assembly)
print('WORKING_ASSEMBLY_LEFT_OPEN',flush=True)
