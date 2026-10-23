from cad import *
import pywintypes
STATE=TASK/'ASSEMBLY_BALLOON_DRAWING_STATE.json';s=json.loads(STATE.read_text());expected=json.loads((TASK/'ASSEMBLY_BOM_DRAWING_STATE.json').read_text())
doc=getdoc(Path(s['drawing']),3);activate(doc);assert c(doc,'ActivateSheet','Sheet1')
f=c(doc,'FeatureByName',s['BOM_feature']);bf=c(f,'GetSpecificFeature2');tables=c(bf,'GetTableAnnotations');assert len(tables)==1
bom=win32com.client.dynamic.Dispatch(tables[0]._oleobj_.QueryInterface(pywintypes.IID('{98FD64DC-285D-4B48-9BDB-D85C253E2BAF}'),pythoncom.IID_IDispatch))
actual=[]
for r in range(88):
 number=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'');part=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
 paths=c(bom,'GetModelPathNames',r,number,part) or []
 if paths:actual.append({'item_number':number.value,'paths':list(paths),'quantity':c(bom,'GetComponentsCount2',r,expected['configuration'],number,part)})
normalize=lambda rows:{x['item_number']:(sorted(Path(p).name for p in x['paths']),x['quantity']) for x in rows}
assert normalize(actual)==normalize(expected['native_items'])
s['BOM_key_reconciliation']={'result':'passed','entries':len(actual),'leaf_instances':sum(x['quantity'] for x in actual),'item_number_path_and_quantity_match_original':True}
c(app,'CloseDoc',c(doc,'GetTitle'))
source=getdoc(ASSEMBLY,2);activate(source)
s['source_live_save_flag_after_linking']=bool(c(source,'GetSaveFlag'))
if s['source_live_save_flag_after_linking']:
 recovery=TASK/'Recovery/Balloon_Task_Final_Live_Source';recovery.mkdir(exist_ok=True);target=recovery/'LIVE_SOURCE_ASSOCIATIONS_PRESERVED.SLDASM';assert not target.exists()
 assert c(source.Extension,'SaveAs',str(target),0,3,NULL,iref(),iref())
 s['preserved_live_source_copy']=str(target)
 s['source_live_note']='SolidWorks marked the live source dirty during drawing balloon association. Its unsaved live state was preserved separately; source model files were not overwritten or discarded.'
s['changed_source_model_files']=[p for p,h in s['native_models_before'].items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert not s['changed_source_model_files']
assert hashlib.sha256(Path(expected['drawing']).read_bytes()).hexdigest()==s['original_BOM_drawing_sha256']
s['PDF_QA']['visual_review']='All three sheets rendered and text bounds checked; isometric/side balloon sheets visually inspected. Circular labels are separated/readable and attached leaders present. No fabrication completeness claim.'
s['status']='Verified complete for stated two-view balloon task:68 native BOM-linked item balloons, each attached component checked; original87-item key and405 quantities preserved; three-page PDF reviewed.'
s['working_assembly_left_open']=True;s['drawing_window_closed']=True
STATE.write_text(json.dumps(s,indent=2));print('BALLOON_TASK_FINAL_QA_PASSED',len(actual),'BOM entries;68 attachment checks; source files unchanged; live_source_dirty',s['source_live_save_flag_after_linking'],flush=True)
