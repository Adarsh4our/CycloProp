from pathlib import Path
import tempfile
exec((Path(tempfile.gettempdir())/'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__',1)[0])
def c(o,name,*args):
 if name not in o._olerepr_.mapFuncs:o._FlagAsMethod(name)
 return getattr(o,name)(*args)
O=ROOT/'CAD/Design_Completion';p=O/'RevB_Isolated/RB_6806.SLDASM';d=getdoc(p,2);f=c(d,'FirstFeature');a=[]
while f:
 try:is3=f.Is3DInterconnectFeature
 except:is3=False
 a.append({'name':f.Name,'type':c(f,'GetTypeName2'),'interconnect':is3});f=c(f,'GetNextFeature')
print(json.dumps(a,indent=2),flush=True);(O/'BEARING_IMPORT_FEATURES.json').write_text(json.dumps(a,indent=2))
