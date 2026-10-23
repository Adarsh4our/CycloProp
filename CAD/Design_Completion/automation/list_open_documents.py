from cad import *
doc=c(app,'GetFirstDocument');rows=[]
while doc:
 p=c(doc,'GetPathName');rows.append({'title':c(doc,'GetTitle'),'path':p,'dirty':bool(c(doc,'GetSaveFlag')),'type':c(doc,'GetType')});doc=c(doc,'GetNext')
(TASK/'OPEN_DOCUMENTS_BEFORE_CLEANUP.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2),flush=True)
