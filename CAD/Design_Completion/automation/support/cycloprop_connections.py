from pathlib import Path
exec(Path(r'C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\automation\support\cycloprop_stop_mounts.py').read_text().rsplit("\nif __name__",1)[0])
ROOTOUT=ROOT/'CAD/Connections_Completion';ROOTOUT.mkdir(exist_ok=True)
ST=Path(tempfile.gettempdir())/'CycloProp_connections_completion_state.json'

def props(doc,description):
 m=doc.Extension.CustomPropertyManager('')
 for k,v in [('DESIGN_STATUS','PROVISIONAL - NOT FABRICATION RELEASED'),('DESIGN_DESCRIPTION',description)]:c(m,'Add3',k,30,v,2)
properties=props

def stateget():
 if ST.exists():return json.loads(ST.read_text())
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);backup=Path(tempfile.mkdtemp(prefix='CycloProp_connections_1_to_4_'));paths=list((ROOT/'CAD').rglob('*.SLDPRT'))+[ROOT/'CAD/Assem20.SLDASM',ROOT/'CAD/Assem3.SLDASM'];hashes={}
 for p in paths:
  if p.name.startswith('~$'):continue
  rel=p.relative_to(ROOT);dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);hashes[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
 roots={co.Name2:co for co in c(doc,'GetComponents',True)};base=roots['XY_Fixed_Base-1'];inner=next(co for co in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in co.Name2)
 off=np.array(c(inner,'GetTotalTransform',True).ArrayData[9:12])-np.array(base.Transform2.ArrayData[9:12]);s={'backup':str(backup),'before_sha256':hashes,'prior_offset_m':off[:2].tolist(),'added':{},'changed_parts':[],'completed':[]};ST.write_text(json.dumps(s,indent=2));return s

def persist(s):ST.write_text(json.dumps(s,indent=2))

def insert(doc,parent,path,key,point,spin=None):
 s=stateget()
 if key in s['added']:
  return next(co for co in c(doc,'GetComponents',True) if co.Name2==s['added'][key])
 getdoc(path);activate(doc);t=list(c(parent,'GetTotalTransform',True).ArrayData);rot=np.array(t[:9]).reshape(3,3);pos=np.array(point)/1000@rot+np.array(t[9:12]);rr=(np.eye(3) if spin is None else np.array(spin))@rot
 co=c(doc,'AddComponent5',str(path),0,'',False,'',*map(float,pos));assert co
 co.Transform2=c(c(app,'GetMathUtility'),'CreateTransform',array(rr.flatten().tolist()+pos.tolist()+[1.,0.,0.,0.]));rigid_datums(doc,parent,co,'Conn_'+key)
 s['added'][key]=co.Name2;persist(s);return co

def partdone(d):
 assert c(d,'EditRebuild3');save(d);s=stateget();p=c(d,'GetPathName')
 if p not in s['changed_parts']:s['changed_parts'].append(p)
 persist(s)

def ytab():
 s=stateget();doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);roots={co.Name2:co for co in c(doc,'GetComponents',True)};tab=roots['Y_Carriage_Drive_Tab_PROTOTYPE-1'];inner=next(co for co in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in co.Name2);td=c(tab,'GetModelDoc2');pd=c(inner,'GetModelDoc2')
 pts=[(-27.,-23.),(-27.,-17.)]
 if c(td,'FeatureByName','YTab_D2p9') is None:
  face_circles(td,2,-.002,[(x/1000,y/1000,-.002) for x,y in pts],.00145);cut(td,'YTab_D2p9',.00201)
  face_circles(td,2,-.002,[(x/1000,y/1000,-.002) for x,y in pts],.0026);cut(td,'YTab_CSK_D5p2',.00115,True);partdone(td)
 if c(pd,'FeatureByName','YTab_D2p9') is None:
  # Inner local coordinates map X -> -X, Y -> assembly Z, Z -> assembly Y.
  face_circles(pd,1,0.,[(-x/1000,0.,y/1000) for x,y in pts],.00145);cut(pd,'YTab_D2p9',.00301);partdone(pd)
 for n,(x,y) in enumerate(pts,1):
  for label,file,z,flip in [('Screw','M2p5x8_CSK_REFERENCE',-1.9,True),('Washer','M2p5_Washer_2p7x6x0p5_REFERENCE',3.,False),('Nut','M2p5_Nut_AF5_H2_REFERENCE',3.5,False)]:insert(doc,tab,ROOT/'CAD/Travel_Stop_Prototype'/(file+'.SLDPRT'),'YTab'+str(n)+label,[x,y,z],np.diag([1,-1,-1]) if flip else None)
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);s=stateget();s['completed'].append('Y tab nominal attachments');persist(s);print('Y_TAB_DONE',flush=True)

def pivotparts():
 global OUT;OUT=ROOTOUT
 for name,od,id_,h,desc in [('M1p6_Washer_REFERENCE',4.,1.7,.3,'M1.6 washer envelope ID1.7 OD4 H0.3; supplier selection and load release pending')]:
  if (OUT/(name+'.SLDPRT')).exists():continue
  d,p=newpart(name,desc);sketch(d);circle(d,0,0,od/2);circle(d,0,0,id_/2);extrude(d,0,h,'Washer');finish(d,p)
 name='M1p6_Nut_REFERENCE'
 if not (OUT/(name+'.SLDPRT')).exists():
  d,p=newpart(name,'M1.6x0.35 full hex nut envelope AF3.2 H1.3; plain nut, threadlocking method pending.');sketch(d);r=3.2/math.sqrt(3);polygon(d,[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)]);circle(d,0,0,.8);extrude(d,0,1.3,'Nut');finish(d,p)
 d=getdoc(ROOT/'CAD/Servo_Actuation_Prototype/Pivot_Pin_D2_REFERENCE.SLDPRT')
 if c(d,'FeatureByName','M1p6_End_Thread_Envelope') is None:
  # Face sketch annulus removes D2 material only from final 2.3 mm, leaving a positive shoulder at 5.2 mm.
  activate(d);f=next(f for b in c(d,'GetBodies2',0,False) for f in c(b,'GetFaces') if abs(c(f,'GetBox')[2]-.0075)<1e-8 and abs(c(f,'GetBox')[5]-.0075)<1e-8)
  c(d,'ClearSelection2',True);c(f,'Select4',False,NULL);c(d.SketchManager,'InsertSketch',True);d.SketchManager.AddToDB=True;circle(d,0,0,1.01);circle(d,0,0,.8);close_sketch(d);cut(d,'M1p6_End_Thread_Envelope',.0023)
  props(d,'Custom shoulder pin: D2 smooth x5.2, M1.6x0.35 thread x2.3, head D4x1; thread envelope only. Head/smooth shank 0..5.2; nut seats on shoulder. Ground bearing fit and steel grade pending.');partdone(d)
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);activate(doc);pins=[co for co in c(doc,'GetComponents',True) if co.Name2.startswith('Pivot_Pin_D2_REFERENCE-')]
 for n,pin in enumerate(sorted(pins,key=lambda co:co.Name2),1):
  insert(doc,pin,ROOTOUT/'M1p6_Washer_REFERENCE.SLDPRT','Pivot'+str(n)+'Washer',[0,0,5.2]);insert(doc,pin,ROOTOUT/'M1p6_Nut_REFERENCE.SLDPRT','Pivot'+str(n)+'Nut',[0,0,5.5])
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);s=stateget();s['completed'].append('Four positive-shoulder pivot retainers');persist(s);print('PIVOT_RETENTION_DONE',flush=True)

def new_screw(name,dia,length,head_d,head_h,desc):
 global OUT;OUT=ROOTOUT;path=OUT/(name+'.SLDPRT')
 if path.exists():return path
 d,p=newpart(name,desc);sketch(d);circle(d,0,0,dia/2);extrude(d,-length,0,'Thread_Envelope');sketch(d);circle(d,0,0,head_d/2);extrude(d,0,head_h,'Head_Envelope');finish(d,p);return p

def guide_mounts():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);s=stateget();roots={co.Name2:co for co in c(doc,'GetComponents',True)};inner=next(co for co in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in co.Name2)
 # Manufacturer MGN5C pattern M2x1.5 deep, 8 mm across, rail pitch15/end5.
 rail_screw=new_screw('Custom_M2x9_Rail_LowHead_REFERENCE',2.,9.,3.4,.7,'Custom M2x0.4 x9 rail screw, head D3.4 x0.7 to fit the imported D3.6 x0.8 pocket. Not a standard ISO4762 screw; procurement and drive form must be finalized; steel grade and torque pending.')
 block_screw=new_screw('M2x2_Socket_Cap_REFERENCE',2.,2.,3.8,2.,'M2x0.4 x2 custom short socket cap screw envelope; head D3.8 H2 recessed into plate. Remaining web0.95 gives nominal1.05 mm engagement into MGN5C M2x1.5. Supplier screw length tolerance and thread engagement must be released.')
 for n,plate_name in [(1,'Intermediate_X_Slider-1'),(2,'XY_Fixed_Base-1')]:
  rail=roots['MGNR05R-'+str(n)];plate=roots[plate_name];pd=c(plate,'GetModelDoc2');rt=list(rail.Transform2.ArrayData);pr=list(plate.Transform2.ArrayData);rr=np.array(rt[:9]).reshape(3,3);rp=np.array(pr[:9]).reshape(3,3)
  pts=[]
  for y in [.005,.020,.035]:pts.append(((np.array([0.,y,0.])@rr+np.array(rt[9:12])-np.array(pr[9:12]))@rp.T))
  if c(pd,'FeatureByName','GuideRail'+str(n)+'_D2p4') is None:
   face_circles(pd,2,.003,pts,.0012);cut(pd,'GuideRail'+str(n)+'_D2p4',.00301);partdone(pd)
  for i,y in enumerate([5.,20.,35.],1):
   insert(doc,rail,rail_screw,'Rail'+str(n)+'Screw'+str(i),[0.,y,2.8])
   # Bottom washer/nut attached to plate, in the same rail-local XY position but Z -3 relative rail bottom.
   insert(doc,rail,ROOT/'CAD/Servo_Mounting_Prototype/M2_Washer_2p2x5x0p3_REFERENCE.SLDPRT','Rail'+str(n)+'Washer'+str(i),[0.,y,-3.3])
   insert(doc,rail,ROOT/'CAD/Servo_Mounting_Prototype/M2_Nut_AF4_H1p6_REFERENCE.SLDPRT','Rail'+str(n)+'Nut'+str(i),[0.,y,-4.9])
 for n,parent in [(1,inner),(2,roots['Intermediate_X_Slider-1'])]:
  block=roots['MGN5C-'+str(n)];pd=c(parent,'GetModelDoc2');bt=list(c(block,'GetTotalTransform',True).ArrayData);pt=list(c(parent,'GetTotalTransform',True).ArrayData);br=np.array(bt[:9]).reshape(3,3);pr=np.array(pt[:9]).reshape(3,3);positions=[]
  for x in [-.004,.004]:positions.append((np.array([x,.008001,.006])@br+np.array(bt[9:12])-np.array(pt[9:12]))@pr.T)
  isinner=n==1;axis=1 if isinner else 2;level=.003
  if c(pd,'FeatureByName','GuideBlock'+str(n)+'_D2p4') is None:
   # Preserve the supplier block; only the mating plate is drilled.
   if isinner:
    for p in positions:p[1]=.003
   else:
    for p in positions:p[2]=.003
   face_circles(pd,axis,level,positions,.0012);cut(pd,'GuideBlock'+str(n)+'_D2p4',.00301)
   face_circles(pd,axis,level,positions,.0021);cut(pd,'GuideBlock'+str(n)+'_HeadCounterbore_D4p2',.00205)
   partdone(pd)
  for i,p in enumerate(positions,1):
   p=p.copy();p[1 if isinner else 2]=.00095
   spin=np.array([[1.,0.,0.],[0.,0.,-1.],[0.,1.,0.]]) if isinner else None
   insert(doc,parent,block_screw,'Block'+str(n)+'Screw'+str(i),(p*1000).tolist(),spin)
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);s=stateget();s['completed'].append('Guide rail and block nominal attachments');persist(s);print('GUIDE_ATTACHMENTS_DONE',flush=True)

def horn_connection():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);roots={co.Name2:co for co in c(doc,'GetComponents',True)};horn=roots['Servo_Horn_R12_LAYOUT-1'];hd=c(horn,'GetModelDoc2');servo=roots['Savox_SH0257MG_INTERFACE_REFERENCE-1'];sd=c(servo,'GetModelDoc2')
 for axis in ['X','Y']:
  f=c(doc,'FeatureByName',axis+'_Horn_Output_Axis');assert c(f,'SetSuppression2',0,1,None)
 if c(hd,'FeatureByName','Custom_Spline_Hub') is None:
  activate(hd);sketch(hd);circle(hd,0,0,2.61);extrude(hd,-.5,2,'Replace_Clearance_Bore_With_Drive_Web')
  sketch(hd);circle(hd,0,0,4.);extrude(hd,-3.2,.3,'Custom_Spline_Hub')
  face_circles(hd,2,.002,[(0.,0.,.002)],.0011);cut(hd,'M2_Retaining_Screw_Clearance',.00521)
  face_circles(hd,2,.002,[(0.,0.,.002)],.0022);cut(hd,'Screw_Head_Pocket_D4p4',.0015)
  # Derive a mating spline cavity from the actual native output body, not a circular clearance bore.
  source=c(c(sd,'GetBodies2',0,False)[1],'Copy');assert source
  scale=1.01;cx,cy,tip=.1235,-.04715,.028280025
  t=[1.,0.,0.,0.,1.,0.,0.,0.,1.,-cx*scale,-cy*scale,-tip*scale-.0005,scale,0.,0.,0.]
  assert c(source,'ApplyTransform',c(c(app,'GetMathUtility'),'CreateTransform',array(t)))
  activate(hd);imp=c(hd,'CreateFeatureFromBody3',source,False,1);assert imp is not None;imp.Name='Native_Savox_Output_Spline_Tool_1p01scale'
  bodies=c(hd,'GetBodies2',0,False);assert len(bodies)==2,len(bodies)
  tool=next(b for b in bodies if c(b,'GetBodyBox')[3]<.003);main=next(b for b in bodies if c(b,'GetBodyBox')[3]>.01)
  combine=c(hd.FeatureManager,'InsertCombineFeature',15902,main,array([tool],pythoncom.VT_DISPATCH));assert combine is not None;combine.Name='Female_Spline_Derived_From_Actual_Servo_CAD'
  assert len(c(hd,'GetBodies2',0,False))==1
  c(hd,'ClearSelection2',True)
  for name in ['Right Plane','Top Plane']:assert c(hd.Extension,'SelectByID2',name,'PLANE',0.,0.,0.,True,0,NULL,0)
  assert c(hd,'InsertAxis2',True)
  f=c(hd,'FirstFeature');last=None
  while f:
   if c(f,'GetTypeName2')=='RefAxis':last=f
   f=c(f,'GetNextFeature')
  assert last;last.Name='Custom_Horn_Output_Axis'
  props(hd,'Custom R12 spline-drive horn: hub OD8 x3.2 below arm; female geometry derived from actual Savox CAD output at scale1.01 (~25 um radial allowance), nominal2.7 mm axial overlap. M2x3 screw seats0.5 above arm base giving nominal2 mm thread engagement. This is custom geometry, NOT a verified commercial SH11M horn; material, spline fit, finish and fatigue release pending.')
  partdone(hd)
 activate(doc)
 for axis in ['X','Y']:
  se=roots['Savox_SH0257MG_INTERFACE_REFERENCE-'+('1' if axis=='X' else '2')];ho=roots['Servo_Horn_R12_LAYOUT-'+('1' if axis=='X' else '2')]
  if c(doc,'FeatureByName',axis+'_Custom_Horn_Spline_Axis') is None:
   entities=[c(se,'GetCorresponding',c(sd,'FeatureByName','Measured_CAD_Output_Axis')),cyl(ho,0.,0.,.0011)];c(doc,'ClearSelection2',True)
   for ent in entities:entityselect(doc,ent)
   result=c(doc,'AddMate5',1,2,False,0.,0.,0.,0.,0.,0.,0.,0.,False,False,0,iref());assert result;result.Name=axis+'_Custom_Horn_Spline_Axis'
 screw=new_screw('M2x3_Horn_Retaining_Screw_REFERENCE',2.,3.,3.8,2.,'M2x0.4 x3 retaining screw envelope, head D3.8x2. SH11M manufacturer lists screw2x3mm, but head drive and delivered servo threaded-depth must be checked. Custom horn seat atZ0.5, shaft tipZ-0.5 gives nominal2 mm engagement; thread envelopes only.')
 for axis,n in [('X',1),('Y',2)]:insert(doc,roots['Servo_Horn_R12_LAYOUT-'+str(n)],screw,'Horn'+axis+'RetainingScrew',[0,0,.5])
 assert c(doc,'ForceRebuild3',False);me=errors(active_mates(doc));assert not me,me;save(doc);s=stateget();s['completed'].append('Custom spline-drive horn geometry and retaining screws');persist(s);print('CUSTOM_SPLINE_HORNS_DONE',flush=True)

def retainer_mounts():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);allco=c(doc,'GetComponents',False);retainers={key:next(co for co in allco if co.Name2.endswith('/'+name+'-1')) for key,name in [('Inner','Inner_Race_Retainer'),('Outer','Outer_Race_Retainer')]}
 inner=next(co for co in allco if '4-Inner_Carriage_Plate' in co.Name2);outer=next(co for co in allco if '4-Outer_Control_Ring' in co.Name2)
 screw6=new_screw('M2x6_Retainer_Screw_REFERENCE',2.,6.,3.8,2.,'M2x0.4x6 cap-screw envelope headD3.8 H2; inner bearing retainer through1mm cap, washer0.3 and spacer1 gives3.7mm nominal tapped engagement. Threads only nominal envelopes.')
 screw4=new_screw('Custom_M2x4_Retainer_LowHead_REFERENCE',2.,4.,3.4,.7,'Custom M2x0.4x4 screw envelope headD3.4 H0.7; outer retainer engagement3.2mm. Nonstandard low head, drive/grade/procurement must be finalized. Threads only nominal envelopes.')
 global OUT;OUT=ROOTOUT
 if not (OUT/'Inner_Retainer_Spacer_H1_REFERENCE.SLDPRT').exists():
  d,p=newpart('Inner_Retainer_Spacer_H1_REFERENCE','Custom spacer OD4 ID2.2 height1, bridges gap between inner bearing-seat end and retainer. Spacer prevents bolt load clamping the rotating bearing outer ring. Stack tolerance must be released.');sketch(d);circle(d,0,0,2);circle(d,0,0,1.1);extrude(d,0,1,'Spacer');finish(d,p)
 # Ring-attached heads sweep across the carriage. Provide an annular clearance recess.
 ip=c(inner,'GetModelDoc2')
 if c(ip,'FeatureByName','Rotating_Retainer_Head_Clearance_Annulus') is None:
  activate(ip);face=next(f for b in c(ip,'GetBodies2',0,False) for f in c(b,'GetFaces') if abs(c(f,'GetBox')[1]-.003)<1e-8 and abs(c(f,'GetBox')[4]-.003)<1e-8 and c(f,'GetArea')>.001)
  c(ip,'ClearSelection2',True);assert c(face,'Select4',False,NULL);c(ip.SketchManager,'InsertSketch',True);ip.SketchManager.AddToDB=True;circle(ip,0,0,25.5);circle(ip,0,0,20.);close_sketch(ip);cut(ip,'Rotating_Retainer_Head_Clearance_Annulus',.0007);partdone(ip)
 lowblock=new_screw('Custom_M2x2p5_UpperBlock_LowHead_REFERENCE',2.,2.5,3.4,.7,'Custom short M2x0.4 x2.5, headD3.4 H0.7. Upper-block screw seats1.5mm above plate underside;1mm nominal thread engagement. Head top2.2 below carriage, clears retainer-head sweep. Grade, drive, length tolerances and procurement unverified.')
 f=c(ip,'FeatureByName','GuideBlock1_HeadCounterbore_D4p2');fd=c(f,'GetDefinition');assert c(fd,'AccessSelections',ip,NULL);c(fd,'SetDepth',True,.0015);assert c(f,'ModifyDefinition',fd,ip,NULL);partdone(ip)
 state=stateget()
 for n in [1,2]:
  key='Block1Screw'+str(n)
  oldname=state['added'].get(key)
  if oldname:
   old=next(co for co in c(doc,'GetComponents',True) if co.Name2==oldname);c(old,'SetSuppression2',0);assert c(old,'GetSuppression')==0
   for plane in ['Right_Plane','Top_Plane','Front_Plane']:
    ff=c(doc,'FeatureByName','Conn_'+key+'_'+plane)
    if ff:c(ff,'SetSuppression2',0,1,None)
  # Native upper-block coordinates: localX mapping is reversed, localZ follows assemblyY.
  block=next(co for co in c(doc,'GetComponents',True) if co.Name2=='MGN5C-1');bt=list(c(block,'GetTotalTransform',True).ArrayData);it=list(c(inner,'GetTotalTransform',True).ArrayData)
  bx=-.004 if n==1 else .004;world=np.array([bx,.008001,.006])@np.array(bt[:9]).reshape(3,3)+np.array(bt[9:12]);pos=(world-np.array(it[9:12]))@np.array(it[:9]).reshape(3,3).T;pos[1]=.0015
  insert(doc,inner,lowblock,'UpperBlockLowHead'+str(n),(pos*1000).tolist(),[[1,0,0],[0,0,-1],[0,1,0]])
 for which,parent,rad in [('Inner',inner,12.5),('Outer',outer,22.5)]:
  ret=retainers[which];rd=c(ret,'GetModelDoc2');pd=c(parent,'GetModelDoc2');rt=list(c(ret,'GetTotalTransform',True).ArrayData);pt=list(c(parent,'GetTotalTransform',True).ArrayData);rr=np.array(rt[:9]).reshape(3,3);pr=np.array(pt[:9]).reshape(3,3);pts=[(rad*math.cos(i*math.pi*2/3),rad*math.sin(i*math.pi*2/3)) for i in range(3)]
  if c(rd,'FeatureByName','Retainer_Three_D2p2') is None:
   face_circles(rd,2,0.,[(x/1000,y/1000,0.) for x,y in pts],.0011);cut(rd,'Retainer_Three_D2p2',.00101 if which=='Inner' else .00051);partdone(rd)
  parentpts=[]
  for x,y in pts:
   v=(np.array([x/1000,y/1000,0.])@rr+np.array(rt[9:12])-np.array(pt[9:12]))@pr.T;v[1]=.01 if which=='Inner' else .0085;parentpts.append(v)
  if c(pd,'FeatureByName',which+'_Retainer_M2_Tapped_Envelope') is None:
   face_circles(pd,1,.01 if which=='Inner' else .0085,parentpts,.001);cut(pd,which+'_Retainer_M2_Tapped_Envelope',.0043)
   c(pd.Extension.CustomPropertyManager(''),'Add3',which.upper()+'_RETAINER_THREAD_CALLOUT',30,'3 x M2x0.4 blind tapped holes, 4mm usable thread; pilot D1.6 depth4.8. CAD shows major-diameter envelope D2x4.3, not tap-drill diameter. Verify material and minimum walls.',2);partdone(pd)
  for n,(x,y) in enumerate(pts,1):
   if which=='Inner':
    insert(doc,ret,ROOTOUT/'Inner_Retainer_Spacer_H1_REFERENCE.SLDPRT','InnerRetSpacer'+str(n),[x,y,1.])
    insert(doc,ret,ROOT/'CAD/Servo_Mounting_Prototype/M2_Washer_2p2x5x0p3_REFERENCE.SLDPRT','InnerRetWasher'+str(n),[x,y,-.3])
    insert(doc,ret,screw6,'InnerRetScrew'+str(n),[x,y,-.3],np.diag([1,-1,-1]))
   else:
    insert(doc,ret,ROOT/'CAD/Servo_Mounting_Prototype/M2_Washer_2p2x5x0p3_REFERENCE.SLDPRT','OuterRetWasher'+str(n),[x,y,.5])
    insert(doc,ret,screw4,'OuterRetScrew'+str(n),[x,y,.8])
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);s=stateget();s['completed'].append('Inner and outer bearing retainer attachments with tapped-hole definitions');persist(s);print('BEARING_RETAINERS_DONE',flush=True)

def ytab_blind_revision():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);allco=c(doc,'GetComponents',False);inner=next(co for co in allco if '4-Inner_Carriage_Plate' in co.Name2);pd=c(inner,'GetModelDoc2');roots={co.Name2:co for co in c(doc,'GetComponents',True)};tab=roots['Y_Carriage_Drive_Tab_PROTOTYPE-1'];pts=[(.027,0.,-.023),(.027,0.,-.017)]
 if c(pd,'FeatureByName','YTab_Blind_M2p5_Thread_Envelopes') is None:
  face_circles(pd,1,0.,pts,.00146)
  f=c(pd.FeatureManager,'FeatureExtrusion2',True,False,True,0,0,.003,0.,False,False,False,False,0.,0.,False,False,False,False,True,True,True,0,0.,False);assert f;f.Name='YTab_Through_Hole_Backing_Restoration'
  face_circles(pd,1,0.,pts,.00125);cut(pd,'YTab_Blind_M2p5_Thread_Envelopes',.0026)
  c(pd.Extension.CustomPropertyManager(''),'Add3','YTAB_THREAD_CALLOUT',30,'2xM2.5x0.45 BLIND from underside. Tap drillD2.05 depth2.7, usable full thread2.3. CAD shows major diameter2.5 depth2.6. M2.5x4 screw gives nominal2.1mm engagement; stripping strength and tolerances unverified. No hardware above plate.',2);partdone(pd)
 global OUT;OUT=ROOTOUT
 if not (OUT/'M2p5x4_CSK_REFERENCE.SLDPRT').exists():
  d,p=newpart('M2p5x4_CSK_REFERENCE','M2.5x0.45x4 countersunk envelope, headD5 90deg. Screw head plane recessed0.1 in2mm tab; nominal2.1 thread engagement into3mm carriage. Blind tap and stripping load unverified.')
  sketch(d);circle(d,0,0,2.5);close_sketch(d);f=c(d.FeatureManager,'FeatureExtrusion2',True,False,True,0,0,.00125,0.,True,False,False,False,math.pi/4,0.,False,False,False,False,True,True,True,0,0.,False);assert f;f.Name='Countersunk_Head_D5';sketch(d);circle(d,0,0,1.25);extrude(d,-4,-1.25,'M2p5_Thread_Envelope');finish(d,p)
 state=stateget()
 for n in [1,2]:
  for label in ['Screw','Washer','Nut']:
   key='YTab'+str(n)+label;old=next(co for co in c(doc,'GetComponents',True) if co.Name2==state['added'][key]);c(old,'SetSuppression2',0)
   for plane in ['Right_Plane','Top_Plane','Front_Plane']:
    f=c(doc,'FeatureByName','Conn_'+key+'_'+plane)
    if f:c(f,'SetSuppression2',0,1,None)
  insert(doc,tab,OUT/'M2p5x4_CSK_REFERENCE.SLDPRT','YTabBlindScrew'+str(n),[-27.,-23. if n==1 else -17.,-1.9],np.diag([1,-1,-1]))
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);state=stateget();state['completed'].append('Y tab revised to blind tapped fastening below ring sweep');persist(state);print('Y_TAB_BLIND_REVISION_DONE',flush=True)

def separate_servo_output():
 global OUT;OUT=ROOTOUT;doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);roots={co.Name2:co for co in c(doc,'GetComponents',True)};sd=c(roots['Savox_SH0257MG_INTERFACE_REFERENCE-1'],'GetModelDoc2');path=OUT/'Savox_Output_Spline_NATIVE_REFERENCE.SLDPRT'
 if not path.exists():
  source=c(c(sd,'GetBodies2',0,False)[1],'Copy');assert c(source,'ApplyTransform',transform(0.,-.1235,.04715,-.028280025));d,p=newpart('Savox_Output_Spline_NATIVE_REFERENCE','Exact native output-shaft body split from copied Savox interface part. Origin atshafttip; positiveZ outputaxis. Rotates rigidly with custom female horn, leavingcasefixed. Body derives from existingCAD, commercial identity and delivered spline fit not verified.')
  activate(d);f=c(d,'CreateFeatureFromBody3',source,False,1);assert f;f.Name='Native_Servo_Output_Spline';finish(d,p)
 if c(sd,'FeatureByName','Output_Body_Separated_For_Rotation') is None:
  activate(sd);body=c(sd,'GetBodies2',0,False)[1];c(sd,'ClearSelection2',True);assert c(body,'Select2',False,NULL);f=c(sd.FeatureManager,'InsertDeleteBody2',False);assert f;f.Name='Output_Body_Separated_For_Rotation';props(sd,'Copy of originalSavoxcase; output-shaftbody removed only fromthisinterfacecopy and separately instanced as rotating native output component. OriginalSavoxfileunchanged; measured outputaxis retained from3Dreference sketch.');partdone(sd)
 for n,axis in [(1,'X'),(2,'Y')]:insert(doc,roots['Servo_Horn_R12_LAYOUT-'+str(n)],path,'RotatingServoOutput'+axis,[0,0,-.5])
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);print('OUTPUT_SHAFT_ROTATION_MODELLED',flush=True)

if __name__=='__main__':
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);v=doc.ActiveView;app.CommandInProgress=True;v.EnableGraphicsUpdate=False;doc.EnableAssemblyRebuild=True;doc.FeatureManager.EnableFeatureTree=False;doc.FeatureManager.EnableFeatureTreeWindow=False
 try:
  stateget()
  if sys.argv[1]=='ytab':ytab()
  if sys.argv[1]=='pivots':pivotparts()
  if sys.argv[1]=='guides':guide_mounts()
  if sys.argv[1]=='horns':horn_connection()
  if sys.argv[1]=='retainers':retainer_mounts()
  if sys.argv[1]=='ytabblind':ytab_blind_revision()
  if sys.argv[1]=='servooutput':separate_servo_output()
 finally:doc.EnableAssemblyRebuild=False;doc.FeatureManager.EnableFeatureTree=True;doc.FeatureManager.EnableFeatureTreeWindow=True;activate(doc);v.EnableGraphicsUpdate=True;app.CommandInProgress=False;c(doc,'GraphicsRedraw2')
