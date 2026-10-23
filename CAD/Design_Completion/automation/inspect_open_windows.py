from cad import *
doc=c(app,'GetFirstDocument');rows=[]
while doc:
 try: visible=bool(doc.Visible)
 except Exception as exc: visible=str(exc)
 rows.append({'title':c(doc,'GetTitle'),'path':c(doc,'GetPathName'),'visible':visible,'dirty':bool(c(doc,'GetSaveFlag'))});doc=c(doc,'GetNext')
(TASK/'OPEN_WINDOW_INSPECTION.json').write_text(json.dumps(rows,indent=2))
print(json.dumps([x for x in rows if x['visible'] is not False],indent=2),flush=True)
