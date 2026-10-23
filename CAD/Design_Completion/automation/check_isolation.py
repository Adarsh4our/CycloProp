from pathlib import Path
import tempfile
exec((Path(tempfile.gettempdir())/'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__',1)[0])
def c(o,name,*args):
 if name not in o._olerepr_.mapFuncs:o._FlagAsMethod(name)
 return getattr(o,name)(*args)
O=ROOT/'CAD/Design_Completion';m=json.loads((O/'ISOLATION_MANIFEST.json').read_text());d=getdoc(Path(m['working_assembly']),2);activate(d);allco=c(d,'GetComponents',False);unresolved=[];outside=[];extra={};rootnames={}
for co in allco:
 if c(co,'GetSuppression')==0:continue
 p=c(co,'GetModelDoc2');path=c(co,'GetPathName');name=co.Name2
 if p is None:unresolved.append(name)
 if path and not path.lower().startswith(str(O/'RevB_Isolated').lower()):outside.append({'name':name,'path':path,'virtual':co.IsVirtual})
 if any(v in name for v in ['Inner_Race_Retainer','Outer_Race_Retainer','Inner_Carriage','Outer_Control','Frame_Mounting','Fixed_Base','Intermediate_X']):
  t=list(c(co,'GetTotalTransform',True).ArrayData);item={'path':path,'transform':t,'boxes':[list(c(b,'GetBodyBox')) for b in c(p,'GetBodies2',0,False) or []]};extra[name]=item
for co in c(d,'GetComponents',True):rootnames[co.Name2.removeprefix('RB_')]=co.Name2
r={'assembly':c(d,'GetPathName'),'dirty':c(d,'GetSaveFlag'),'root_names':rootnames,'unresolved_active':unresolved,'references_outside_isolation':outside,'selected_geometry':extra};(O/'ISOLATED_REFERENCE_CHECK.json').write_text(json.dumps(r,indent=2));print('ISOLATED_ROOTS',len(rootnames),'UNRESOLVED',unresolved,'OUTSIDE_REFERENCES',outside,flush=True);assert len(rootnames)==276 and not unresolved;assert all(x['virtual'] for x in outside),outside
