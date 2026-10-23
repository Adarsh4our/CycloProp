from pathlib import Path
import tempfile
exec((Path(tempfile.gettempdir())/'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__',1)[0])
def c(o,name,*args):
 if name not in o._olerepr_.mapFuncs:o._FlagAsMethod(name)
 return getattr(o,name)(*args)
O=ROOT/'CAD/Design_Completion';source=O/'Assem20_Design_RevB.SLDASM';dest=O/'RevB_Isolated';report=O/'ISOLATION_MANIFEST.json';assert not report.exists(),'Isolation already recorded; inspect instead of rerunning';assert not dest.exists() or not any(dest.iterdir()),'Destination contains files';dest.mkdir(exist_ok=True);d=getdoc(source,2);assert not c(d,'GetSaveFlag'),'Preserve live edits before Pack and Go';activate(d);pg=c(d.Extension,'GetPackAndGo');pg.IncludeDrawings=False;pg.IncludeSimulationResults=False;pg.IncludeToolboxComponents=True;pg.FlattenToSingleFolder=True;pg.AddPrefix='RB_';assert c(pg,'SetSaveToName',True,str(dest));names=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_VARIANT,None);assert c(pg,'GetDocumentNames',names);sources=list(names.value);print('PACK_AND_GO_SOURCE_COUNT',len(sources),flush=True);app.CommandInProgress=True
try:
 result=c(d.Extension,'SavePackAndGo',pg);print('PACK_AND_GO_STATUS',result,flush=True);assert result is not None and all(v==0 for v in result),result
finally:app.CommandInProgress=False
r={'source_assembly':str(source),'working_directory':str(dest),'working_assembly':str(dest/'RB_Assem20_Design_RevB.SLDASM'),'source_paths':sources,'source_hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources if Path(p).is_file()},'copied_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.is_file()},'pack_and_go_status':list(result),'note':'All external filenames prefixed RB_; virtual embedded components require subsequent native resolution check.'};assert Path(r['working_assembly']).exists();report.write_text(json.dumps(r,indent=2));print('ISOLATED_COPY_SAVED',r['working_assembly'],flush=True)
