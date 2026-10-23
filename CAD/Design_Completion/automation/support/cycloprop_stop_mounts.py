from pathlib import Path
exec(Path(r'C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\automation\support\cycloprop_travel_stop.py').read_text().rsplit("\nif __name__",1)[0])
MOUNTSTATE=Path(tempfile.gettempdir())/'CycloProp_stop_mount_state.json'
HOLES=[(24.,21.),(27.,27.)]

def close_sketch(doc):
 doc.SketchManager.AddToDB=False;c(doc.SketchManager,'InsertSketch',True);c(doc,'ClearSelection2',True)
 f=c(doc,'FirstFeature');last=None
 while f:
  if c(f,'GetTypeName2')=='ProfileFeature':last=f
  f=c(f,'GetNextFeature')
 assert last is not None and c(last,'Select2',False,0)
 return last

def face_circles(doc,axis,level,points,radius):
 activate(doc);c(doc,'ClearSelection2',True)
 face=next(f for b in c(doc,'GetBodies2',0,False) for f in c(b,'GetFaces') if c(c(f,'GetSurface'),'IsPlane') and abs(c(f,'GetBox')[axis]-level)<1e-8 and abs(c(f,'GetBox')[axis+3]-level)<1e-8)
 assert c(face,'Select4',False,NULL);c(doc.SketchManager,'InsertSketch',True);doc.SketchManager.AddToDB=True
 t=list(doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData);rot=np.array(t[:9]).reshape(3,3)
 for point in points:
  p=np.array(point)@rot+np.array(t[9:12]);assert abs(p[2])<1e-7
  c(doc.SketchManager,'CreateCircleByRadius',float(p[0]),float(p[1]),0.,radius)
 close_sketch(doc)

def cut(doc,name,depth,draft=False):
 feat=c(doc.FeatureManager,'FeatureCut3',True,False,False,0,0,depth,0.,draft,False,False,False,math.pi/4 if draft else 0.,0.,False,False,False,False,False,True,True,False,False,False,0,0.,False)
 assert feat is not None,('cut failed',name)
 feat.Name=name;assert c(doc,'EditRebuild3');assert not errors([feat]),errors([feat]);return feat

def totalvol(doc):return sum(c(b,'GetMassProperties',1.)[3]*1e9 for b in c(doc,'GetBodies2',0,False))

def cut_mounts():
 doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);roots={x.Name2:x for x in c(doc,'GetComponents',True)}
 inner=next(x for x in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in x.Name2)
 parts=[('FixedBracket',c(roots['XY_Stop_Fixed_Bracket_PROTOTYPE-1'],'GetModelDoc2'),2,-.003,[(x/1000,y/1000,-.003) for x,y in HOLES],.003,True),
 ('FixedBase',c(roots['XY_Fixed_Base-1'],'GetModelDoc2'),2,0.,[(x/1000,y/1000,0.) for x,y in HOLES],.003,False),
 ('MovingArm',c(roots['XY_Stop_Moving_Arm_PROTOTYPE-1'],'GetModelDoc2'),2,.002,[(x/1000,y/1000,.002) for x,y in HOLES],.002,False),
 ('Carriage',c(inner,'GetModelDoc2'),1,.003,[(-x/1000,.003,y/1000) for x,y in HOLES],.003,True)]
 if MOUNTSTATE.exists():state=json.loads(MOUNTSTATE.read_text())
 else:
  backup=Path(tempfile.mkdtemp(prefix='CycloProp_before_stop_mounts_'));source={}
  for name,p,*_ in parts:
   path=Path(c(p,'GetPathName'));shutil.copy2(path,backup/path.name);source[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
  ap=ROOT/'CAD/Assem20.SLDASM';shutil.copy2(ap,backup/ap.name)
  state={'date':'2026-10-21','backup':str(backup),'pre_change_sources_sha256':source,'hole_centres_plate_frame_mm':HOLES,'added_components':{},'part_checks':[]}
  MOUNTSTATE.write_text(json.dumps(state,indent=2))
 for name,p,axis,level,points,thick,csk in parts:
  if any(row['part']==str(Path(c(p,'GetPathName')).relative_to(ROOT)) for row in state['part_checks']):continue
  expected=2*math.pi*1.45**2*thick*1000
  if c(p,'FeatureByName','Stop_Mount_D2p9_Through') is None:
   before=totalvol(p);face_circles(p,axis,level,points,.00145);cut(p,'Stop_Mount_D2p9_Through',thick+.00001);after=totalvol(p)
  else:
   after=totalvol(p);before=after+expected
  assert abs((before-after)-expected)<.001,(name,before-after,expected)
  cskremoved=None
  if csk:
   pre=after;face_circles(p,axis,level,points,.0026);cut(p,'Stop_Mount_CSK_D5p2_90deg',.00115,True)
   cskremoved=pre-totalvol(p)
   expected=2*(math.pi*1.15/3*(2.6**2+2.6*1.45+1.45**2)-math.pi*1.45**2*1.15)
   assert abs(cskremoved-expected)<.001,('cskvolume',name,cskremoved,expected)
  save(p);state['part_checks'].append({'part':str(Path(c(p,'GetPathName')).relative_to(ROOT)),'through_hole_volume_removed_mm3':before-after,'countersink_extra_volume_removed_mm3':cskremoved})
  MOUNTSTATE.write_text(json.dumps(state,indent=2));print('MOUNT_HOLES',name,flush=True)
 activate(doc);assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc));save(doc)

def make_hardware():
 for length in (8,10):
  d,p=newpart('M2p5x'+str(length)+'_CSK_REFERENCE','Provisional M2.5x0.45 countersunk screw; full length '+str(length)+' mm; head OD5, 90 degree envelope; neck included by shank. No actual threads or drive recess. Selected supplier envelope, not universal ISO10642 head maximum.')
  sketch(d);circle(d,0,0,2.5);close_sketch(d)
  feat=c(d.FeatureManager,'FeatureExtrusion2',True,False,True,0,0,.00125,0.,True,False,False,False,math.pi/4,0.,False,False,False,False,True,True,True,0,0.,False)
  assert feat is not None;feat.Name='Head_D5_90deg'
  sketch(d);circle(d,0,0,1.25);extrude(d,-length,-1.25,'M2p5x0p45_Thread_Envelope')
  finish(d,p)
 d,p=newpart('M2p5_Washer_2p7x6x0p5_REFERENCE','Provisional DIN125A/ISO7089 washer: ID2.7 OD6 thickness0.5 mm; manufacturer catalogue envelope.')
 sketch(d);circle(d,0,0,3);circle(d,0,0,1.35);extrude(d,0,.5,'Washer_Envelope');finish(d,p)
 d,p=newpart('M2p5_Nut_AF5_H2_REFERENCE','Provisional M2.5x0.45 DIN934 nut: AF5 height2 mm; full hex conservative envelope, plain nut. No threads, chamfers or approved anti-loosening method.')
 sketch(d);r=5/math.sqrt(3);polygon(d,[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)]);circle(d,0,0,1.25);extrude(d,0,2,'Nut_Envelope');finish(d,p)

def assemble_hardware():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);activate(doc);state=json.loads(MOUNTSTATE.read_text())
 roots={x.Name2:x for x in c(doc,'GetComponents',True)};fixed=roots['XY_Stop_Fixed_Bracket_PROTOTYPE-1'];arm=roots['XY_Stop_Moving_Arm_PROTOTYPE-1']
 base=roots['XY_Fixed_Base-1'];bp=np.array(base.Transform2.ArrayData[9:12]);inner=next(x for x in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in x.Name2);ip=np.array(c(inner,'GetTotalTransform',True).ArrayData[9:12])
 state['restored_prior_offset_m']=(ip[:2]-bp[:2]).tolist()
 def insert(key,file,parent,x,y,z,flip=False):
  assert key not in state['added_components']
  path=OUT/(file+'.SLDPRT');getdoc(path);activate(doc)
  co=c(doc,'AddComponent5',str(path),0,'',False,'',x,y,z);assert co
  t=[1.,0.,0.,0.,-1. if flip else 1.,0.,0.,0.,-1. if flip else 1.,x,y,z,1.,0.,0.,0.]
  co.Transform2=c(c(app,'GetMathUtility'),'CreateTransform',array(t));c(doc,'EditRebuild3');rigid_datums(doc,parent,co,'StopMount_'+key)
  state['added_components'][key]=co.Name2;MOUNTSTATE.write_text(json.dumps(state,indent=2));return co
 for which,parent in [('Fixed',fixed),('Moving',arm)]:
  origin=np.array(parent.Transform2.ArrayData[9:12])
  for n,(hx,hy) in enumerate(HOLES,1):
   x,y=origin[0]+hx/1000,origin[1]+hy/1000
   if which=='Fixed':screwz,washerz,nutz=origin[2]-.0029,origin[2]+.003,origin[2]+.0035;length=10
   else:screwz,washerz,nutz=origin[2]+.0049,origin[2]-.0005,origin[2]-.0025;length=8
   insert(which+'_Screw'+str(n),'M2p5x'+str(length)+'_CSK_REFERENCE',parent,x,y,screwz,which=='Fixed')
   insert(which+'_Washer'+str(n),'M2p5_Washer_2p7x6x0p5_REFERENCE',parent,x,y,washerz)
   insert(which+'_Nut'+str(n),'M2p5_Nut_AF5_H2_REFERENCE',parent,x,y,nutz)
 assert c(doc,'ForceRebuild3',False);me=errors(active_mates(doc));assert not me,me;save(doc)
 print('MOUNT_HARDWARE_ADDED',len(state['added_components']),'ACTIVE_MATES',len(active_mates(doc)),flush=True)

if __name__=='__main__':
 doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);view=doc.ActiveView;app.CommandInProgress=True;view.EnableGraphicsUpdate=False
 try:
  if sys.argv[1]=='holes':cut_mounts()
  elif sys.argv[1]=='hardware':make_hardware()
  elif sys.argv[1]=='assemble':assemble_hardware()
 finally:
  activate(doc);view.EnableGraphicsUpdate=True;app.CommandInProgress=False;c(doc,'GraphicsRedraw2')
