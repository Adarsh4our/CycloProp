from pathlib import Path
import tempfile
exec((Path(tempfile.gettempdir())/'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__',1)[0])
def c(o,name,*args):
 if name not in o._olerepr_.mapFuncs:o._FlagAsMethod(name)
 return getattr(o,name)(*args)
O=ROOT/'CAD/Design_Completion';snap=json.loads((O/'RESUME_NATIVE_STATE.json').read_text());state=json.loads((O/'REV_B_STATE.json').read_text());active=app.ActiveDoc;print('LIVE_ACTIVE',c(active,'GetPathName') if active else None,flush=True);d=getdoc(Path(state['assembly']),2);print('TARGET_DIRTY',c(d,'GetSaveFlag'),flush=True);roots={co.Name2:co for co in c(d,'GetComponents',True)};changed={};selected={}
for name in ['XY_Fixed_Base-1','3-Drive_Shaft-1','Part1-1','Part1-2','Part1-3','Part1-4','Assem3-1','Frame_Mounting_RevA-1']:
 co=roots[name];t=list(c(co,'GetTotalTransform',True).ArrayData);old=snap['components'].get(name,{}).get('transform');delta=float(np.max(np.abs(np.array(t)-old))) if old else None;selected[name]={'transform':t,'path':c(co,'GetPathName'),'suppression':c(co,'GetSuppression')}
 if delta is not None and delta>1e-8:changed[name]=delta
for co in c(roots['Assem3-1'],'GetChildren'):
 if '/4-' in co.Name2:
  t=list(c(co,'GetTotalTransform',True).ArrayData);old=snap['components'].get(co.Name2,{}).get('transform');selected[co.Name2]={'transform':t,'path':c(co,'GetPathName')}
  if old and np.max(np.abs(np.array(t)-old))>1e-8:changed[co.Name2]=float(np.max(np.abs(np.array(t)-old)))
links={}
for n,mp in state['maps'].items():
 links[n]={key:{'name':mp[key],'exists':mp[key] in roots,'path':c(roots[mp[key]],'GetPathName') if mp[key] in roots else None} for key in ['Tube','ArmBall','RingBall','ArmSocket','RingSocket']}
print('LIVE_ROOTS',len(roots),'CHANGED_TRANSFORMS',changed,flush=True)
constraints={}
for name in ['RevB_SETUP_Rotor_Angle','RevB_SETUP_Ring_Angle','LimitDistance3','LimitDistance1']:
 f=c(d,'FeatureByName',name);constraints[name]={'exists':f is not None,'suppressed':c(f,'IsSuppressed') if f else None}
 if f and name.startswith('Limit'):constraints[name]['advanced']=c(f,'GetDefinition').IsAdvancedMate
r={'date':'2026-10-21','assembly':c(d,'GetPathName'),'dirty':c(d,'GetSaveFlag'),'root_count':len(roots),'changed_transforms_from_handoff':changed,'selected_components':selected,'links':links,'constraints':constraints,'baseline_hash':hashlib.sha256((ROOT/'config/baseline.json').read_bytes()).hexdigest()};(O/'LIVE_RESUME_CONFIRMATION.json').write_text(json.dumps(r,indent=2));print('LIVE_CONFIRMATION_SAVED',flush=True)
