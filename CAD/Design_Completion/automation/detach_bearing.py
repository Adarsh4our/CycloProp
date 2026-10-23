from pathlib import Path
import tempfile
exec((Path(tempfile.gettempdir())/'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__',1)[0])
def c(o,name,*args):
 if name not in o._olerepr_.mapFuncs:o._FlagAsMethod(name)
 return getattr(o,name)(*args)
O=ROOT/'CAD/Design_Completion';p=O/'RevB_Isolated/RB_6806.SLDASM';backup=O/'Recovery/Before_Bearing_Detach';backup.mkdir(parents=True,exist_ok=True);assert (backup/p.name).exists();d=getdoc(p,2);activate(d);f=c(d,'FeatureByName','NSK_6806.stp-1');assert f and f.Is3DInterconnectFeature;app.CommandInProgress=True
try:
 result=c(f,'BreakLink',True,True);print('BEARING_BREAK_LINK',result,flush=True);save(d)
 children=[]
 for co in c(d,'GetComponents',False):children.append({'name':co.Name2,'path':c(co,'GetPathName'),'virtual':co.IsVirtual,'resolved':c(co,'GetModelDoc2') is not None})
 (O/'BEARING_DETACH_RESULT.json').write_text(json.dumps({'result':result,'children':children,'backup':str(backup)},indent=2));print('DETACHED_CHILDREN',children,flush=True)
finally:app.CommandInProgress=False
