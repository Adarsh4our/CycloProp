from cad import *
import re,textwrap
folder=TASK/'Drawings_Prototype';INDEX=folder/'DRAWING_INDEX.json';index=json.loads(INDEX.read_text())
recovery=TASK/'Recovery/Before_Drawing_QA_Corrections';recovery.mkdir(exist_ok=True)
for number,row in index['drawings'].items():
 for key in ['drawing','pdf']:
  src=Path(row[key]);dest=recovery/src.name
  if not dest.exists():shutil.copy2(src,dest)
 doc=getdoc(Path(row['drawing']),3);activate(doc)
 source_hash=hashlib.sha256(Path(row['model']).read_bytes()).hexdigest()
 view=c(doc,'GetFirstView');footers=hashes=0
 while view:
  for n in c(view,'GetNotes') or []:
   text=c(n,'GetText')
   if text.startswith('View scale '):
    assert c(n,'SetText','DO NOT SCALE. Individual model-view scales may differ. Nominal dimensions in mm.\nRelease holds apply: fits, loaded clearances, locking, fatigue and supplied material.\nThread solids show major envelopes; DO NOT use as tap-drill sizes.');footers+=1
   if text.startswith('MODEL SHA256: '):assert c(n,'SetText','MODEL SHA256: '+source_hash);hashes+=1
   if number=='CP-RB-001' and text.startswith('DIMENSION / INTERFACE DEFINITION'):
    normalized=' '.join(text.split())
    old='Current rotor setup angle remains a construction drive; XY setup distances retain saved pose. Usable travel/constraints require final consolidation.'
    assert old in normalized or 'axis and radial travel limits restored' in normalized
    normalized=normalized.replace(old,'Rotor/ring setup holds suppressed; axis and radial travel limits restored. Saved nominal pose preserved. Further free-motion verification remains a release hold.')
    assert c(n,'SetText',textwrap.fill(normalized,69))
  view=c(view,'GetNextView')
 assert footers==1 and hashes==1,(number,footers,hashes)
 assert c(doc,'ForceRebuild3',False);save(doc);activate(doc);save(doc,Path(row['pdf']))
 row.update({'model_sha256':source_hash,'drawing_sha256':hashlib.sha256(Path(row['drawing']).read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(Path(row['pdf']).read_bytes()).hexdigest(),'scope':'Native prototype inspection views and dimensional/interface notes. Scales explicitly marked DO NOT SCALE. Undimensioned fabrication details and release holds remain.','qa_corrected':True})
 INDEX.write_text(json.dumps(index,indent=2));c(app,'CloseDoc',c(doc,'GetTitle'));print('DRAWING_QA_CORRECTED',number,flush=True)
activate(getdoc(ASSEMBLY,2))
