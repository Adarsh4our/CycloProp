from cad import *
STATE=TASK/'ARM_RETENTION_INTEGRATION_STATE.json'
resume = '--resume-before-first-cut' in sys.argv
assert not STATE.exists() or resume, 'Inspect partial state before resuming; never duplicate pins'
d=getdoc(ASSEMBLY,2);activate(d)
assert not c(d,'GetSaveFlag'), 'Unexpected unsaved assembly changes'
ro=roots(d)
inspection=json.loads((TASK/'ARM_RETENTION_INTERFACE_INSPECTION.json').read_text())
assert len(inspection['candidates'])==4
for row in inspection['candidates']:
    assert np.max(abs(np.array(row['blade_candidate_local_m'])-[.0095,0.,-.00775]))<1e-8
    assert np.max(abs(np.array(row['blade_axis'])-[0.,1.,0.]))<1e-8
recovery=TASK/'Recovery/Before_Arm_Crosspins';recovery.mkdir(parents=True,exist_ok=True)
if resume:
    s=json.loads(STATE.read_text())
    assert not s['added'] and not s['changed_parts'], 'Only untouched pre-cut state can use this resume'
    assert (recovery/ASSEMBLY.name).exists()
    for name,old in s['before_transforms'].items():assert np.max(abs(np.array(tf(ro[name]))-old))<1e-6,name
else:
    assert not (recovery/ASSEMBLY.name).exists()
    assert c(d.Extension,'SaveAs',str(recovery/ASSEMBLY.name),0,3,NULL,iref(),iref())
    s={'status':'IN PROGRESS','backup':str(recovery),'added':{},'before_transforms':{name:tf(co) for name,co in ro.items()},'changed_parts':{}}
    STATE.write_text(json.dumps(s,indent=2))
def persist():STATE.write_text(json.dumps(s,indent=2))
def bore(part,centre,axis,length,name):
    path=Path(c(part,'GetPathName'));assert path.parent==OUT
    assert not (recovery/path.name).exists(),path
    shutil.copy2(path,recovery/path.name)
    if c(part,'GetSaveFlag'):
        live=recovery/('LIVE_BEFORE_'+path.name)
        assert c(part.Extension,'SaveAs',str(live),0,3,NULL,iref(),iref())
        s.setdefault('preserved_live_dirty_parts',[]).append(str(live))
    s['changed_parts'][path.name]={'before_sha256':hashlib.sha256(path.read_bytes()).hexdigest()};persist()
    body=c(part,'GetBodies2',0,False)[0]
    start=np.array(centre)-np.array(axis)*length/2
    tool=c(c(app,'GetModeler'),'CreateBodyFromCyl',array(start.tolist()+list(axis)+[.0005,length]))
    overlap=c(c(body,'Copy'),'Operations2',15901,c(tool,'Copy'),iref()) or []
    removed=sum(c(b,'GetMassProperties',1.)[3] for b in overlap)
    assert removed>1e-10,(name,removed)
    activate(part);f=c(part,'CreateFeatureFromBody3',tool,False,1);assert f;f.Name=name+'_Tool'
    bodies=list(c(part,'GetBodies2',0,False));assert len(bodies)==2
    # Imported tool is identified by its known cylinder volume, not body ordering.
    expected=math.pi*.0005**2*length
    tools=[b for b in bodies if abs(c(b,'GetMassProperties',1.)[3]-expected)<1e-14];assert len(tools)==1
    main=next(b for b in bodies if abs(c(b,'GetMassProperties',1.)[3]-expected)>=1e-14)
    f=c(part.FeatureManager,'InsertCombineFeature',15902,main,array(tools,pythoncom.VT_DISPATCH));assert f;f.Name=name
    assert c(part,'EditRebuild3');check=inspect_part(part)
    c(part.Extension.CustomPropertyManager(''),'Add3','ARM_CROSSPIN_INTERFACE',30,'NominalD1 crosshole; line-ream arm and METAL trunnion together to1.00..1.02mm. ISO8750 standard-duty1x8 coiled pin installed envelope. Trunnion material/core attachment, press force/retention and fatigue not released. Do not drill an unspecified composite journal.',2)
    save(part);s['changed_parts'][path.name].update({'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'removed_mm3':removed*1e9,'body_check':check});persist()
app.CommandInProgress=True
try:
    def pin(part):ring(part,1.,0.,-4.,4.,'Installed_D1x8_Coiled_Pin_Envelope')
    path=make_part('RB_ISO8750_D1x8_INSTALLED_REFERENCE','SPIROL standard-duty metric ISO8750 coiled pin1x8 installed envelope D1x8. Free OD1.05..1.15 and recommended hole1.00..1.04 from manufacturer guide p17. Proposed line-ream1.00..1.02. Coils/chamfers omitted; steel density proxy only, no supplied grade, fit retention, fatigue or physical proof inferred. For METAL trunnion only. Supplier/application approval required.','AISI 4340 Steel, normalized',pin)
    bore(c(ro['Blade_Pitch_Arm_Offset22p075_PROTOTYPE-1'],'GetModelDoc2'),[0.,0.,.00175],[1.,0.,0.],.010,'RevB_D1_Arm_Positive_Retention_Crosshole')
    bore(c(ro['Part1-1'],'GetModelDoc2'),[.0095,0.,-.00775],[0.,1.,0.],.006,'RevB_D1_Metal_Trunnion_Retention_Crosshole')
    getdoc(path)
    for row in inspection['candidates']:
        arm=c(d,'GetComponentByName',row['arm']);t=tf(arm);R=np.array(t[:9]).reshape(3,3)
        position=world(arm,[0.,0.,.00175]);rotation=np.array([-R[2],R[1],R[0]])
        assert abs(np.linalg.det(rotation)-1)<1e-6
        activate(d);co=c(d,'AddComponent5',str(path),0,'',False,'',*position.tolist());assert co
        set_transform(co,position,rotation);s['added'][row['link']]=co.Name2;persist()
        lock(d,arm,co,'RevB_Blade_Arm_'+row['link']+'_Positive_Crosspin')
    assert c(d,'ForceRebuild3',False)
    s['mate_errors']=errors(active_mates(d));persist();assert not s['mate_errors'],s['mate_errors']
    for name,old in s['before_transforms'].items():assert np.max(abs(np.array(tf(ro[name]))-old))<1e-6,name
    save(d)
    s.update({'complete':True,'status':'Four arm crosspins installed; native nominal geometry and mates checked, not physical retention/strength release','assembly_sha256':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest(),'source':'https://www.spirol.com/assets/files/cldp-coiled-spring-pins-design-guide-us.pdf','source_page_printed':17,'proposed_hole_mm':[1.,1.02],'manufacturer_hole_range_mm':[1.,1.04],'manufacturer_pin_free_od_mm':[1.05,1.15],'pin_length_mm':8,'pin_length_tolerance_mm':.25,'material_basis':'Installed solid envelope uses4340 density proxy; procure supplier-defined coiled spring steel, not a machined4340 dowel','release_holds':['Blade remains a monolithic geometry proxy: metal trunnion construction and attachment to composite blade not established','Manufacturer/application approval for press fit in thin7075 boss and D3 metal trunnion','Pin press retention, host bearing/ligament, fretting and cyclic torque/fatigue','Tool access and repeated assembly/removal validation'],'preserved':['D-flat torque-drive geometry','Arm and blade axial stations','All linkage ball centres and rod lengths']});persist()
    print('FOUR_POSITIVE_ARM_CROSSPINS_INSTALLED',flush=True)
finally:app.CommandInProgress=False
