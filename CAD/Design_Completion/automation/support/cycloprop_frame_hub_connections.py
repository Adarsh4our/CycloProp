from pathlib import Path
exec(Path(r'C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\automation\support\cycloprop_connections.py').read_text().rsplit("\nif __name__",1)[0])
OUT=ROOTOUT

# Rigid attachment mates are appropriate for the frame/hub hardware: only mate dimensions drive the mechanism.
def insert_fast(doc,parent,path,key,point,spin=None):
 st=stateget()
 if key in st['added']:
  return next(co for co in c(doc,'GetComponents',True) if co.Name2==st['added'][key])
 getdoc(path);activate(doc);t=list(c(parent,'GetTotalTransform',True).ArrayData);rot=np.array(t[:9]).reshape(3,3);pos=np.array(point)/1000@rot+np.array(t[9:12]);rr=(np.eye(3) if spin is None else np.array(spin))@rot
 co=c(doc,'AddComponent5',str(path),0,'',False,'',*map(float,pos));assert co;co.Transform2=c(c(app,'GetMathUtility'),'CreateTransform',array(rr.flatten().tolist()+pos.tolist()+[1.,0.,0.,0.]))
 c(doc,'ClearSelection2',True);compselect(doc,parent);compselect(doc,co);fd=c(doc,'CreateMateData',16);fd.EntitiesToMate=array([parent,co],pythoncom.VT_DISPATCH);f=c(doc,'CreateMate',fd);assert f;f.Name='Conn_'+key+'_Rigid'
 st['added'][key]=co.Name2;persist(st);print('RIGID',key,flush=True);return co

def ringpart(name,od,id_,z0,z1,description):
 path=OUT/(name+'.SLDPRT')
 if path.exists():return path
 d,p=newpart(name,description);sketch(d);circle(d,0,0,od/2);circle(d,0,0,id_/2);extrude(d,z0,z1,'Ring_Envelope');finish(d,p);return p

def modelplane_circles(d,plane,points,radius):
 activate(d);c(d,'ClearSelection2',True);assert c(d.Extension,'SelectByID2',plane,'PLANE',0.,0.,0.,False,0,NULL,0);c(d.SketchManager,'InsertSketch',True);d.SketchManager.AddToDB=True;t=list(d.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
 for pt in points:
  v=np.array(pt)@np.array(t[:9]).reshape(3,3)+np.array(t[9:12]);assert abs(v[2])<1e-7;c(d.SketchManager,'CreateCircleByRadius',float(v[0]),float(v[1]),0.,radius)
 close_sketch(d)

def cut_both(d,name):
 f=c(d.FeatureManager,'FeatureCut3',False,False,False,1,1,.1,.1,False,False,False,False,0.,0.,False,False,False,False,False,True,True,False,False,False,0,0.,False);assert f;f.Name=name;assert c(d,'EditRebuild3');return f

def copy_part(source,name):
 path=OUT/(name+'.SLDPRT')
 if not path.exists():shutil.copy2(source,path)
 return getdoc(path),path

def frame_parts():
 stateget();d,path=copy_part(ROOT/'CAD/6-Mounting_Chassis_Frame.SLDPRT','Frame_Mounting_RevA')
 if c(d,'FeatureByName','Upper_Bearing_Housing_Extension') is None:
  # Lower bearing centre=-2; upper centre=251.2: separation253.2 matches actual shaft groove-seat centres.
  sketch(d);circle(d,0,0,10.);circle(d,0,0,6.5);extrude(d,248.7,252.6,'Upper_Bearing_Housing_Extension')
  for a,b,label in [(.5,3.,'Lower_Bearing_Outer_Race_Shoulder'),(253.7,262.5,'Upper_Bearing_Outer_Race_Shoulder')]:
   sketch(d);circle(d,0,0,6.51);circle(d,0,0,5.7);extrude(d,a,b,label)
  posts=[(x,y,.003) for x in [-.024,.024] for y in [-.052,.052]]
  face_circles(d,2,.003,posts,.0017);cut(d,'Four_Stage_Support_D3p4',.01701)
  # Cap screws are blind tapped from the two bearing-retainer mounting faces.
  lower=[(8.3*math.cos(math.pi/6+i*2*math.pi/3)/1000,8.3*math.sin(math.pi/6+i*2*math.pi/3)/1000,-.008) for i in range(3)]
  upper=[(p[0],p[1],.2487) for p in lower]
  face_circles(d,2,-.008,lower,.001);cut(d,'Lower_Retainer_M2_Envelope',.0032)
  face_circles(d,2,.2487,upper,.001);cut(d,'Upper_Retainer_M2_Envelope',.0032)
  props(d,'Revised frame copied from original: stage support holes at(+/-24,+/-52), lower seat686ZZ centreZ-2, upper centre251.2, spacing253.2mm; upper housing extended3.8mm inward. Bearings6x13x5 selected by envelope, loading/fit unverified. Frame origin44mm above fixed-base underside. M2 cap holes CAD major-diameter envelopes; tap M2x0.4 pilot1.6 depth3.7 usable3mm. Plate material, preload, tolerances, rotor and motor clearance pending.');partdone(d)
 ringpart('686ZZ_6x13x5_ENVELOPE',13.,6.,0,5,'Commercial 686ZZ envelope6x13x5, SMB catalogue. Simplified solid annulus, no bearing internal geometry or mass accuracy. Fit, axial clearance and loading release pending.')
 ringpart('Lower_MainBearing_OuterSpacer_L3p5',12.9,11.4,0,3.5,'Custom OD12.9 ID11.4 x3.5 sleeve retains lower bearing outer race only; face contact land must be checked against selected bearing drawing.')
 for name,length in [('Stage_Support_L27',27.),('Stage_Support_L33',33.)]:ringpart(name,6.,3.4,0,length,'Custom stage standoff OD6 ID3.4 length'+str(length)+' mm; 7075/steel choice, column and fastener loads unverified.')
 for name in ['Lower_MainBearing_Retainer','Upper_MainBearing_Retainer']:
  if not (OUT/(name+'.SLDPRT')).exists():
   d,p=newpart(name,'Custom outer-race cap OD22 ID11.4 x1; three D2.2 atPCD16.6. M2 blind fastening; no contact with shaft clips. Face-contact land and stiffness unverified.')
   sketch(d);circle(d,0,0,11.);circle(d,0,0,5.7)
   for i in range(3):circle(d,8.3*math.cos(math.pi/6+i*2*math.pi/3),8.3*math.sin(math.pi/6+i*2*math.pi/3),1.1)
   extrude(d,0,1,'Bearing_Cap');finish(d,p)
 new_screw('M3x55_Frame_Screw_REFERENCE',3.,55.,5.5,3.,'M3x0.5x55 cap screw envelope headD5.5 H3; base3 plus33/27mm spacer plus11/17mm frame pluswasher0.5/nut2.4. Supplier grade, full thread extent, stiffness and preload unverified.')
 ringpart('M3_Washer_REFERENCE',7.,3.2,0,.5,'M3 washer reference ID3.2 OD7 H0.5, DIN125A nominal envelope.')
 if not (OUT/'M3_Nut_REFERENCE.SLDPRT').exists():
  d,p=newpart('M3_Nut_REFERENCE','M3x0.5 plain nut reference AF5.5 H2.4. Anti-loosening method unselected.');sketch(d);r=5.5/math.sqrt(3);polygon(d,[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)]);circle(d,0,0,1.5);extrude(d,0,2.4,'Nut');finish(d,p)
 # Installed retaining-ring reference, with deliberately conservative round exterior.
 if not (OUT/'DSH6_INSTALLED_CLEARANCE_REFERENCE.SLDPRT').exists():
  d,p=newpart('DSH6_INSTALLED_CLEARANCE_REFERENCE','DIN471/DSH6 installed clearance envelope: groove5.7 width0.8, ring thickness0.7. Outer diameter10.4 conservatively reserved, split opening1.6. Not an exact spring-ring manufacturing model; use supplier DSH6. Verify installed envelope, ring elasticity and strength.');sketch(d);circle(d,0,0,5.2);circle(d,0,0,2.85);extrude(d,0,.7,'Installed_Ring_Envelope')
  activate(d);f=next(f for b in c(d,'GetBodies2',0,False) for f in c(b,'GetFaces') if abs(c(f,'GetBox')[2]-.0007)<1e-8 and abs(c(f,'GetBox')[5]-.0007)<1e-8);c(d,'ClearSelection2',True);c(f,'Select4',False,NULL);c(d.SketchManager,'InsertSketch',True);d.SketchManager.AddToDB=True;rect(d,0,-.8,6.,.8);close_sketch(d);cut(d,'Split_Opening_Envelope',.00071);finish(d,p)
 print('FRAME_PARTS_DONE',flush=True)

def frame_assembly():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);roots={co.Name2:co for co in c(doc,'GetComponents',True)};base=roots['XY_Fixed_Base-1'];bd=c(base,'GetModelDoc2');shaft=roots['3-Drive_Shaft-1'];sd=c(shaft,'GetModelDoc2')
 if c(bd,'FeatureByName','Frame_Support_Ear_1') is None:
  i=0
  for x in [-24.,24.]:
   for y in [-52.,52.]:
    i+=1;box(bd,x-4,min(y-4,24 if y>0 else -24),x+4,max(y+4,24 if y>0 else -24),0,3,'Frame_Support_Ear_'+str(i))
  face_circles(bd,2,.003,[(x/1000,y/1000,.003) for x in [-24.,24.] for y in [-52.,52.]],.0017);cut(bd,'Frame_Support_Four_D3p4',.00301);partdone(bd)
 # Correct the groove root to the selected nominal6 circlip, keeping shaft length unchanged.
 if c(sd,'FeatureByName','Retaining_Grooves_D5p7_1') is None:
  for i,(a,b) in enumerate([(7.05,7.85),(13.,13.8),(260.25,261.05),(266.2,267.)],1):
   sketch(sd);circle(sd,0,0,2.85);circle(sd,0,0,2.49);extrude(sd,a,b,'Retaining_Grooves_D5p7_'+str(i))
  props(sd,'Existing6x275 steel shaft retained. Four groove roots corrected from5.0 to5.7mm forDIN4716/DSH6; width0.8 unchanged. Nominal bearing journal spans7.85..13 and261.05..266.2. CAD mass changed; calculation baseline260mm not changed. Fits, strength and balance unverified.');partdone(sd)
 frame=insert(doc,base,OUT/'Frame_Mounting_RevA.SLDPRT','RevisedFrame',[0,0,44.])
 # Axial shaft position aligns actual bearing groove-seat centres with revised frame seats.
 t=list(shaft.Transform2.ArrayData);t[11]=base.Transform2.ArrayData[11]+.031575;shaft.Transform2=c(c(app,'GetMathUtility'),'CreateTransform',array(t))
 if c(doc,'FeatureByName','Shaft_Axial_Location_For_Frame_Bearings') is None:
  c(doc,'ClearSelection2',True)
  for ent in [mappedplane(base),mappedplane(shaft)]:entityselect(doc,ent)
  f=c(doc,'AddDistanceMate',0,False,.031575,.031575,.031575,0,0,iref());assert f;f.Name='Shaft_Axial_Location_For_Frame_Bearings';fd=c(f,'GetDefinition');fd.FlipDimension=False;assert c(f,'ModifyDefinition',fd,doc,NULL)
 for i,(x,y) in enumerate([(x,y) for x in [-24.,24.] for y in [-52.,52.]],1):
  length=27. if y>0 else 33.;insert(doc,base,OUT/('Stage_Support_L'+str(int(length))+'.SLDPRT'),'FramePost'+str(i),[x,y,3.])
  insert(doc,base,OUT/'M3x55_Frame_Screw_REFERENCE.SLDPRT','FrameBolt'+str(i),[x,y,0],np.diag([1,-1,-1]));insert(doc,base,OUT/'M3_Washer_REFERENCE.SLDPRT','FrameWasher'+str(i),[x,y,47.]);insert(doc,base,OUT/'M3_Nut_REFERENCE.SLDPRT','FrameNut'+str(i),[x,y,47.5])
 for n,z in [(1,-4.5),(2,248.7)]:
  insert(doc,frame,OUT/'686ZZ_6x13x5_ENVELOPE.SLDPRT','MainBearing'+str(n),[0,0,z])
 insert(doc,frame,OUT/'Lower_MainBearing_OuterSpacer_L3p5.SLDPRT','LowerMainOuterSpacer',[0,0,-8.])
 cap1=insert(doc,frame,OUT/'Lower_MainBearing_Retainer.SLDPRT','LowerMainCap',[0,0,-9.]);cap2=insert(doc,frame,OUT/'Upper_MainBearing_Retainer.SLDPRT','UpperMainCap',[0,0,247.7])
 screw=new_screw('M2x4_MainCap_Screw_REFERENCE',2.,4.,3.8,2.,'M2x0.4x4 cap screw envelope; 1mm cap plus0.3 washer gives2.7mm nominal blind thread engagement. Torque and grade unverified.')
 for n,cap in [(1,cap1),(2,cap2)]:
  for i in range(3):
   x,y=8.3*math.cos(math.pi/6+i*2*math.pi/3),8.3*math.sin(math.pi/6+i*2*math.pi/3);insert(doc,cap,ROOT/'CAD/Servo_Mounting_Prototype/M2_Washer_2p2x5x0p3_REFERENCE.SLDPRT','MainCap'+str(n)+'Washer'+str(i),[x,y,-.3]);insert(doc,cap,screw,'MainCap'+str(n)+'Screw'+str(i),[x,y,-.3],np.diag([1,-1,-1]))
 for i,z in enumerate([7.1,13.05,260.30,266.25],1):insert(doc,shaft,OUT/'DSH6_INSTALLED_CLEARANCE_REFERENCE.SLDPRT','ShaftClip'+str(i),[0,0,z])
 assert c(doc,'ForceRebuild3',False);me=errors(active_mates(doc));assert not me,me;save(doc);s=stateget();s['completed'].append('Revised frame, stage supports, main bearings, caps and shaft axial retention');persist(s);print('FRAME_MOUNTING_DONE',flush=True)

def hub_parts():
 d,path=copy_part(ROOT/'CAD/aluminum hub.SLDPRT','Shaft_Drive_Hub_RevA')
 if c(d,'FeatureByName','Shaft_Hub_Collar_L11') is None:
  sketch(d);circle(d,0,0,7.);circle(d,0,0,3.);extrude(d,-11,0,'Shaft_Hub_Collar_L11')
  points=[(11*math.cos(math.pi/4+i*math.pi/2)/1000,11*math.sin(math.pi/4+i*math.pi/2)/1000,0.) for i in range(4)];face_circles(d,2,0.,points,.0014);cut(d,'Flange_Four_D2p8_PCD22',.00301)
  modelplane_circles(d,'Right Plane',[(0.,0.,-.006)],.001);cut_both(d,'DIN1481_D2_Cross_Pin_Hole')
  props(d,'Separate aluminum hub: flange28x3, pilot13.9x1.5, bore6, added collar14OD x11 behind flange; four D2.8 PCD22 at45deg, crossholeD2 atlocalZ-6 forDIN1481installed2x14 pin. Through bolts/nuts selected instead of thin3mm flange tapped holes. Material, fit, pin shear, fatigue and balance unverified.');partdone(d)
 d,path=copy_part(ROOT/'CAD/2-Endplate_Hub.SLDPRT','Endplate_Hub_Interface_RevA')
 if c(d,'FeatureByName','Centre_Bore_Correction_D14') is None:
  # Original currently measures15, conflicting with the documented14. Correct only this revised copy.
  sketch(d);circle(d,0,0,7.51);circle(d,0,0,7.);extrude(d,0,1.5,'Centre_Bore_Correction_D14')
  props(d,'Revised copy of current206x1.5 endplate: centrebore corrected fromactual15 to documented14 for13.9 pilot, fourexistingD2.8 PCD22 retained. Original source preserved. Blade bushings and rotor integration outside this mounting step.');partdone(d)
 new_screw('M2p5x8_Hub_Screw_REFERENCE',2.5,8.,4.5,2.5,'ISO4762 M2.5x0.45x8 cap screw envelope head4.5x2.5; flange3, G10plate1.5, two washers0.5 each andnut2 give0.5mm nominal protrusion.')
 if not (OUT/'DIN1481_D2x14_INSTALLED_REFERENCE.SLDPRT').exists():
  d,p=newpart('DIN1481_D2x14_INSTALLED_REFERENCE','Nominal installed slotted springpin2x14 envelope OD2 ID1.2; actual freeOD and spring-slot geometry depend on supplier. Hole2H12, steel grade, force and shear capacity unverified. Not a press-fit simulation.');sketch(d);circle(d,0,0,1.);circle(d,0,0,.6);extrude(d,-7,7,'Installed_Spring_Pin');finish(d,p)
 print('HUB_PARTS_DONE',flush=True)

def hub_assembly():
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);roots={co.Name2:co for co in c(doc,'GetComponents',True)};shaft=roots['3-Drive_Shaft-1'];sd=c(shaft,'GetModelDoc2')
 if c(sd,'FeatureByName','Two_Hub_Cross_Pin_D2') is None:
  modelplane_circles(sd,'Right Plane',[(0.,0.,.0415),(0.,0.,.2435)],.001);cut_both(sd,'Two_Hub_Cross_Pin_D2');partdone(sd)
 for end,z,flip in [('Mech',35.5,True),('Drive',249.5,False)]:
  spin=np.diag([1,-1,-1]) if flip else None;hub=insert(doc,shaft,OUT/'Shaft_Drive_Hub_RevA.SLDPRT',end+'Hub',[0,0,z],spin)
  insert(doc,hub,OUT/'Endplate_Hub_Interface_RevA.SLDPRT',end+'Endplate',[0,0,3.])
  # Pin localZ follows hubX, with its centre at hub-localZ-6.
  insert(doc,hub,OUT/'DIN1481_D2x14_INSTALLED_REFERENCE.SLDPRT',end+'HubPin',[0,0,-6.],[[0,0,-1],[0,1,0],[1,0,0]])
  for i in range(4):
   x,y=11*math.cos(math.pi/4+i*math.pi/2),11*math.sin(math.pi/4+i*math.pi/2);key=end+'Hub'+str(i)
   insert(doc,hub,ROOT/'CAD/Travel_Stop_Prototype/M2p5_Washer_2p7x6x0p5_REFERENCE.SLDPRT',key+'TopWasher',[x,y,4.5]);insert(doc,hub,OUT/'M2p5x8_Hub_Screw_REFERENCE.SLDPRT',key+'Bolt',[x,y,5.])
   insert(doc,hub,ROOT/'CAD/Travel_Stop_Prototype/M2p5_Washer_2p7x6x0p5_REFERENCE.SLDPRT',key+'BottomWasher',[x,y,-.5]);insert(doc,hub,ROOT/'CAD/Travel_Stop_Prototype/M2p5_Nut_AF5_H2_REFERENCE.SLDPRT',key+'Nut',[x,y,-2.5])
 assert c(doc,'ForceRebuild3',False);me=errors(active_mates(doc));assert not me,me;save(doc);s=stateget();s['completed'].append('Separate hubs, endplate attachment bolts and positive shaft crosspins');persist(s);print('HUB_ATTACHMENTS_DONE',flush=True)

def pivot_thrust_washers():
 path=ringpart('Pivot_Thrust_Spacer_H0p5',4.,2.1,0,.5,'Custom thrust spacer OD4 ID2.1 H0.5. One beneath first member and one between members on eachD2 shoulder pin. Fills two0.5mm gaps, leaving0.2mm nominal axial play before5.2mm shoulder. Finish/material/tolerances unverified.')
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);pins=sorted([co for co in c(doc,'GetComponents',True) if co.Name2.startswith('Pivot_Pin_D2_REFERENCE-')],key=lambda co:co.Name2)
 for n,pin in enumerate(pins,1):
  insert_fast(doc,pin,path,'Pivot'+str(n)+'LowerThrust',[0,0,0.]);insert_fast(doc,pin,path,'Pivot'+str(n)+'MiddleThrust',[0,0,2.5])
 assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc)),errors(active_mates(doc));save(doc);print('PIVOT_THRUST_SPACERS_DONE',flush=True)

if __name__=='__main__':
 doc=getdoc(ROOT/'CAD/Assem20.SLDASM',2);v=doc.ActiveView;app.CommandInProgress=True;v.EnableGraphicsUpdate=False;doc.EnableAssemblyRebuild=True;doc.FeatureManager.EnableFeatureTree=False;doc.FeatureManager.EnableFeatureTreeWindow=False
 try:
  stateget()
  if sys.argv[1]=='frameparts':frame_parts()
  elif sys.argv[1]=='frame':frame_assembly()
  elif sys.argv[1]=='hubparts':hub_parts()
  elif sys.argv[1]=='hubs':
   insert=insert_fast;hub_assembly()
  elif sys.argv[1]=='thrust':pivot_thrust_washers()
 finally:doc.EnableAssemblyRebuild=False;doc.FeatureManager.EnableFeatureTree=True;doc.FeatureManager.EnableFeatureTreeWindow=True;activate(doc);v.EnableGraphicsUpdate=True;app.CommandInProgress=False;c(doc,'GraphicsRedraw2')
