from create_prototype_drawings import *
import pywintypes
STATE=TASK/'ASSEMBLY_BALLOON_DRAWING_STATE.json';resume='--resume-inspected-first-view' in sys.argv
assert not STATE.exists() or resume,'Inspect task state before resuming; do not duplicate sheets'
original=json.loads((TASK/'ASSEMBLY_BOM_DRAWING_STATE.json').read_text())
source=getdoc(ASSEMBLY,2);activate(source)
if c(source,'GetSaveFlag'):
 assert resume,'Preserve unexpected unsaved source work before a fresh task'
 recovery_source=TASK/'Recovery/Balloon_TextStyle_Recovery';recovery_source.mkdir(exist_ok=True)
 source_copy=recovery_source/'LIVE_SOURCE_ASSEMBLY_DURING_BALLOON_LINKING.SLDASM'
 assert not source_copy.exists()
 assert c(source.Extension,'SaveAs',str(source_copy),0,3,NULL,iref(),iref())
model_hash=hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest();assert model_hash==original['source_sha256']
folder=TASK/'Drawings_Prototype';path=folder/'CP-RB-003_BALLOONED_ASSEMBLY.SLDDRW';pdf=path.with_suffix('.pdf');assert resume or not path.exists()
original_drawing=Path(original['drawing']);original_sha=hashlib.sha256(original_drawing.read_bytes()).hexdigest()
model_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*') if p.suffix.upper() in ('.SLDPRT','.SLDASM') and not p.name.startswith('~$')}
if not resume:shutil.copy2(original_drawing,path)
s={'status':'IN PROGRESS','source':str(ASSEMBLY),'source_sha256':model_hash,'original_BOM_drawing_sha256':original_sha,'drawing':str(path),'pdf':str(pdf),'views':[],'native_models_before':model_hashes,'scope':'BOM-linked visible-component balloons on two views. Occluded items and purchase qualification are separate; source geometry unchanged.'}
if resume:
 s=json.loads(STATE.read_text());assert not s.get('complete') and not s['views'];assert s['source_sha256']==model_hash
else:STATE.write_text(json.dumps(s,indent=2))
def persist():STATE.write_text(json.dumps(s,indent=2))
doc=getdoc(path,3);activate(doc);assert Path(c(doc,'GetPathName'))==path
if resume:
 assert c(doc,'GetSheetNames')==('Sheet1','Assembly_Isometric')
 recovery=TASK/'Recovery/Balloon_TextStyle_Recovery';recovery.mkdir(exist_ok=True)
 target=recovery/'LIVE_CP_RB_003_BEFORE_VALIDATION.SLDDRW';assert not target.exists()
 assert c(doc.Extension,'SaveAs',str(target),0,3,NULL,iref(),iref())
assert c(doc,'ActivateSheet','Sheet1')
features=[];f=c(doc,'FirstFeature')
while f:
 features.append((f.Name,c(f,'GetTypeName2')))
 f=c(f,'GetNextFeature')
bom_names=[name for name,kind in features if kind=='BomFeat'];assert len(bom_names)==1,features
bom_name=bom_names[0];s['BOM_feature']=bom_name
view=c(doc,'GetFirstView')
while view:
 for n in c(view,'GetNotes') or []:
  text=c(n,'GetText')
  if text.startswith('CYCLOPROP  |  CP-RB-002'):assert c(n,'SetText','CYCLOPROP  |  CP-RB-003  |  REV B  |  BALLOONED ASSEMBLY / BOM KEY')
  if 'assembly balloons remain separate work' in text:assert c(n,'SetText',text.replace('This sheet supplements CP-RB-001; assembly balloons remain separate work.','BOM key for the ballooned views on the following sheets.'))
 view=c(view,'GetNextView')
expected={row['item_number']:{Path(p).name for p in row['paths']} for row in original['native_items']}
for sheet_name,orientation in [('Assembly_Isometric','*Isometric'),('Assembly_Side','*Right')]:
 if resume and sheet_name=='Assembly_Isometric':
  assert c(doc,'ActivateSheet',sheet_name)
  view=c(c(doc,'GetFirstView'),'GetNextView');assert c(view,'GetKeepLinkedToBOMName')==bom_name
  name=c(view,'GetName2');balloons=c(view,'GetNotes') or [];assert len(balloons)==47
 else:
  assert c(doc,'NewSheet3',sheet_name,10,13,1.,1.,False,'',.841,.594,'Default')
  assert c(doc,'ActivateSheet',sheet_name)
  view=c(doc,'CreateDrawViewFromModelView3',str(ASSEMBLY),orientation,.420,.300,0.);assert view
  view.UseSheetScale=0;view.ScaleDecimal=1.15
  bounds=list(c(view,'GetOutline'));view.ScaleDecimal*=min(1.,.470/(bounds[2]-bounds[0]),.340/(bounds[3]-bounds[1]))
  assert c(view,'SetKeepLinkedToBOM',True,bom_name)
  assert c(view,'GetKeepLinkedToBOM') and c(view,'GetKeepLinkedToBOMName')==bom_name
  name=c(view,'GetName2');assert c(doc,'ActivateView',name)
  c(doc,'ClearSelection2',True);assert c(doc.Extension,'SelectByID2',name,'DRAWINGVIEW',0.,0.,0.,False,0,NULL,0)
  options=c(doc,'CreateAutoBalloonOptions');options.Layout=1;options.IgnoreMultiple=True;options.LeaderAttachmentToFaces=True
  options.Style=1;options.Size=2;options.UpperTextContent=1;options.ItemOrder=1;options.InsertMagneticLine=True;options.EditBalloons=False
  balloons=c(doc,'AutoBalloon5',options) or [];assert balloons,('No native balloons',sheet_name)
 rows=[]
 for balloon in balloons:
  number=c(balloon,'GetBomBalloonText',True).strip();assert number in expected,('Unlinked/invalid item',number)
  assert c(balloon,'GetBomBalloonTextStyle',True)==2 # swDetailingNoteTextItemNumber; differs from AutoBalloon option enum1
  annotation=c(balloon,'GetAnnotation');fmt=c(annotation,'GetTextFormat',0);fmt.CharHeight=.0035;fmt.TypeFaceName='Arial';assert c(annotation,'SetTextFormat',0,False,fmt)
  attachments=[]
  for attached in c(annotation,'GetAttachedEntities3') or []:
   ent=win32com.client.dynamic.Dispatch(attached._oleobj_.QueryInterface(pywintypes.IID('{83A33D65-27C5-11CE-BFD4-00400513BB57}'),pythoncom.IID_IDispatch))
   component=c(ent,'GetComponent')
   if component:
    attached_path=c(component,'GetPathName');assert Path(attached_path).name in expected[number],(number,attached_path,expected[number])
    attachments.append({'component':component.Name2,'path':attached_path})
  assert attachments,('Balloon lacks verified component attachment',number)
  rows.append({'item_number':number,'position_m':list(c(annotation,'GetPosition')),'attachments':attachments})
 s['views'].append({'sheet':sheet_name,'orientation':orientation,'native_view':name,'BOM_link':bom_name,'balloons':rows});persist()
 c(doc,'ActivateView','')
 note(doc,'CYCLOPROP  |  CP-RB-003  |  '+sheet_name.replace('_',' ').upper(),.015,.575,.004)
 note(doc,'PROTOTYPE / NOT RELEASED FOR FABRICATION  -  NATIVE BOM ITEM NUMBERS  -  DO NOT SCALE',.015,.562,.003)
 note(doc,'ASSEMBLY SHA256: '+model_hash,.015,.548,.0023)
 note(doc,'Balloons identify visible CAD components and reference the BOM key on sheet1.\nRepeated occurrences share an item number; hidden/internal items may be unlabelled.\nReference models and bearing internals are not a procurement release. Materials, fits and qualification remain open.',.020,.040,.003)
 assert c(doc,'ForceRebuild3',False)
 print('BALLOON_VIEW_CREATED',sheet_name,len(rows),flush=True)
 save(doc,path)
save(doc,path);activate(doc);save(doc,pdf)
s.update({'complete':True,'status':'Native BOM-linked balloons created with every returned label/component mapping verified; PDF visual QA pending','drawing_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'original_drawing_unchanged':hashlib.sha256(original_drawing.read_bytes()).hexdigest()==original_sha,'changed_source_model_files':[p for p,h in model_hashes.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]})
assert s['original_drawing_unchanged'] and not s['changed_source_model_files'];persist()
c(app,'CloseDoc',c(doc,'GetTitle'));activate(source)
print('BALLOONED_ASSEMBLY_SAVED',sum(len(x['balloons']) for x in s['views']),flush=True)
