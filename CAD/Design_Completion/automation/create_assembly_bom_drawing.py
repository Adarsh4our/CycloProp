from create_prototype_drawings import *
import csv
from collections import Counter
STATE=TASK/'ASSEMBLY_BOM_DRAWING_STATE.json'
assert not STATE.exists(),'Inspect previous task state before resuming'
source=getdoc(ASSEMBLY,2);activate(source)
assert not c(source,'GetSaveFlag'),'Assembly has unsaved work; preserve and inspect before generating a source-identified BOM'
model_hash=hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()
config=source.ConfigurationManager.ActiveConfiguration.Name
folder=TASK/'Drawings_Prototype';path=folder/'CP-RB-002_ASSEMBLY_BOM.SLDDRW';pdf=path.with_suffix('.pdf');csvpath=path.with_suffix('.csv')
assert not path.exists() and not pdf.exists()
s={'status':'IN PROGRESS','source':str(ASSEMBLY),'source_sha256':model_hash,'configuration':config,'drawing':str(path),'pdf':str(pdf),'csv':str(csvpath),'geometry_changes':False}
STATE.write_text(json.dumps(s,indent=2))
template=c(app,'GetUserPreferenceStringValue',10)
doc=c(app,'NewDocument',template,10,.841,.594);assert doc
assert c(c(doc,'GetCurrentSheet'),'SetSize',10,.841,.594)
view=c(doc,'CreateDrawViewFromModelView3',str(ASSEMBLY),'*Isometric',.665,.340,0.);assert view
view.UseSheetScale=0;view.ScaleDecimal=.65
bounds=list(c(view,'GetOutline'));view.ScaleDecimal*=min(1.,.300/(bounds[2]-bounds[0]),.310/(bounds[3]-bounds[1]))
print('ASSEMBLY_VIEW_CREATED',flush=True)
bom=c(view,'InsertBomTable4',False,.015,.548,1,1,config,r'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\bom-standard.sldbomtbt',False,0,False)
assert bom,'Native parts-only BOM creation failed'
# Query the native table interface; the BOM interface and table interface are distinct COM interfaces.
table=win32com.client.dynamic.Dispatch(bom._oleobj_.QueryInterface(pythoncom.MakeIID('{C108723C-AC56-4C08-9591-7980B0A5AAB2}'),pythoncom.IID_IDispatch))
rows,columns=table.RowCount,table.ColumnCount
print('NATIVE_BOM_TABLE',rows,columns,flush=True)
assert rows>1 and columns>=3
fmt=c(table,'GetTextFormat');fmt.CharHeight=.0027;fmt.TypeFaceName='Arial';assert c(table,'SetTextFormat',False,fmt)
for k in range(columns):c(table,'SetColumnWidth',k,[.020,.285,.165,.025][k] if columns==4 else .495/columns,0)
# Fit all rows on one A1 sheet; use >=2.7mm type, not tiny text to hide overflow.
for r in range(rows):c(table,'SetRowHeight',r,.0053,0)
assert c(table,'SaveAsText2',str(csvpath),',',False)
raw=csvpath.read_bytes();text=raw.decode('utf-16' if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else 'utf-8-sig')
lines=list(csv.reader(text.splitlines()));s['table_text_rows']=lines;s['native_row_count']=rows;s['native_column_count']=columns
native=[]
for r in range(rows):
 number=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'');partnumber=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
 paths=c(bom,'GetModelPathNames',r,number,partnumber) or []
 if paths:
  quantity=c(bom,'GetComponentsCount2',r,config,number,partnumber)
  native.append({'row':r,'item_number':number.value,'part_number':partnumber.value,'paths':list(paths),'quantity':quantity})
s['native_items']=native
STATE.write_text(json.dumps(s,indent=2))
print('NATIVE_BOM_ITEMS_CAPTURED',len(native),flush=True)
note(doc,'CYCLOPROP  |  CP-RB-002  |  REV B  |  ASSEMBLY BILL OF MATERIALS',.015,.579,.004)
note(doc,'PROTOTYPE / NOT RELEASED FOR FABRICATION  -  PARTS-ONLY NATIVE BOM  -  '+config,.015,.565,.003)
note(doc,'ASSEMBLY SHA256: '+model_hash,.520,.545,.0023)
note(doc,'DO NOT SCALE. This BOM lists native CAD references and quantities.\nPurchased envelopes and custom reference fasteners are not procurement approval.\nMaterials, fits, grade, supplier selection and physical qualification remain open.\nUse REVISED_NATIVE_MATERIAL_BOM.csv for material/mass assumptions;\nCAD mass is not measured hardware mass.\n\nLinked native BOM: update after approved assembly changes.\nThis sheet supplements CP-RB-001; assembly balloons remain separate work.',.560,.135,.003)
assert c(doc,'ForceRebuild3',False)
save(doc,path);activate(doc);save(doc,pdf)
s.update({'complete':True,'status':'Native parts-only BOM drawing/PDF saved; text/layout and quantity reconciliation pending','drawing_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'source_sha256_after':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()})
assert s['source_sha256_after']==model_hash
STATE.write_text(json.dumps(s,indent=2))
c(app,'CloseDoc',c(doc,'GetTitle'));activate(source)
print('NATIVE_ASSEMBLY_BOM_SAVED',len(native),'items',flush=True)
