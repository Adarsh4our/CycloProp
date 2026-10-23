from pathlib import Path
import sys, json, math, tempfile, shutil, hashlib
import numpy as np

exec(Path(r'C:\Users\Adarsh Singh\CycloProp\CAD\Design_Completion\automation\support\cycloprop_servo_layout.py').read_text().split("if __name__")[0])

OUT=ROOT/'CAD'/'Travel_Stop_Prototype'
OUT.mkdir(exist_ok=True)
STATE=Path(tempfile.gettempdir())/'CycloProp_travel_stop_state.json'

def properties(doc,description):
    mgr=doc.Extension.CustomPropertyManager('')
    for k,v in [('DESIGN_STATUS','PROVISIONAL TRAVEL STOP - NOT RELEASED FOR FABRICATION'),
                ('DESIGN_DESCRIPTION',description),('E_MAX_NOMINAL_MM','6.88'),
                ('RELEASE_LIMITATIONS','Mount attachment fasteners, tolerances, materials and stop-load capacity not verified')]:
        c(mgr,'Add3',k,30,v,2)

def polygon(doc,points):
    for a,b in zip(points,points[1:]+points[:1]):
        c(doc.SketchManager,'CreateLine',a[0]/1000,a[1]/1000,0.,b[0]/1000,b[1]/1000,0.)

def bridge(doc,start,end,width,z0,z1,name):
    dx,dy=end[0]-start[0],end[1]-start[1];length=math.hypot(dx,dy)
    nx,ny=-dy/length*width/2,dx/length*width/2
    sketch(doc)
    polygon(doc,[(start[0]+nx,start[1]+ny),(end[0]+nx,end[1]+ny),(end[0]-nx,end[1]-ny),(start[0]-nx,start[1]-ny)])
    extrude(doc,z0,z1,name)

def make_stop_parts():
    doc,path=newpart('XY_Stop_Fixed_Bracket_PROTOTYPE','Nominal stop bore 19.76 mm; outer ring 32 mm; 3 mm thick. Bore centre 50,50 mm from fixed-base centre. Attachment holes deferred.')
    sketch(doc);circle(doc,50,50,16);circle(doc,50,50,9.88);extrude(doc,-3,0,'Stop_Ring_D19p76_OD32')
    bridge(doc,(24,24),(40.5,40.5),8,-3,0,'Outboard_Bridge')
    box(doc,18,18,30,30,-3,0,'Base_Attachment_Pad')
    finish(doc,path)
    doc,path=newpart('XY_Stop_Moving_Arm_PROTOTYPE','2 mm arm below bearing carriage; follower seat at 50,50 mm; M4 clearance hole 4.5 mm. Arm attaches to carriage, mounting holes deferred.')
    sketch(doc);circle(doc,50,50,6);circle(doc,50,50,2.25);extrude(doc,0,2,'Follower_Seat_D4p5')
    bridge(doc,(24,24),(47,47),8,0,2,'Carriage_To_Follower_Bridge')
    box(doc,16,18,30,30,0,2,'Carriage_Attachment_Pad')
    finish(doc,path)
    doc,path=newpart('XY_Stop_Follower_D6_M4_PROTOTYPE','Custom follower: smooth D6 x 24 mm below shoulder; upper M4x0.7 thread x 10 mm. Thread shown as major-diameter envelope. Material, hardness and fillet/chamfer release pending.')
    sketch(doc);circle(doc,0,0,3);extrude(doc,-24,0,'Smooth_Stop_Shank_D6_L24')
    sketch(doc);circle(doc,0,0,2);extrude(doc,0,10,'M4x0p7_Thread_Envelope_L10')
    finish(doc,path)
    doc,path=newpart('M4_Washer_4p3x9x0p8_REFERENCE','Reference envelope: M4 washer, ID4.3 OD9 thickness0.8 mm. Dimensions from WDS 876-M4-303 / DIN125A. No procurement or material certification.')
    sketch(doc);circle(doc,0,0,4.5);circle(doc,0,0,2.15);extrude(doc,0,.8,'Washer_Envelope')
    finish(doc,path)
    doc,path=newpart('M4_Locknut_AF7_H5_REFERENCE','Reference envelope: M4x0.7 prevailing-torque nut, AF7 height5 mm. DIN985 / Verpas 0000400 envelope. Thread and nylon insert not modelled; full hex is a conservative exterior envelope.')
    sketch(doc);r=7/math.sqrt(3)
    polygon(doc,[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)])
    circle(doc,0,0,2);extrude(doc,0,5,'Locknut_Conservative_Envelope')
    finish(doc,path)

def set_axis_positions(doc,x,y,restore_limits=False):
    radial=c(doc,'FeatureByName','Combined_XY_Radial_Limit_6p88mm')
    assert c(radial,'SetSuppression2',0,1,None)
    for n,gap in [('LimitDistance3',.012+x),('LimitDistance1',.012+y)]:
        f=c(doc,'FeatureByName',n);fd=c(f,'GetDefinition');fd.IsAdvancedMate=False;fd.Distance=gap
        assert c(f,'ModifyDefinition',fd,doc,NULL)
    assert c(doc,'ForceRebuild3',False)
    if restore_limits:
        for n,gap in [('LimitDistance3',.012+x),('LimitDistance1',.012+y)]:
            f=c(doc,'FeatureByName',n);fd=c(f,'GetDefinition');fd.IsAdvancedMate=True;fd.Distance=gap;fd.MinimumDistance=.00512;fd.MaximumDistance=.01888
            assert c(f,'ModifyDefinition',fd,doc,NULL)
    assert c(radial,'SetSuppression2',1,1,None)
    return c(doc,'ForceRebuild3',False)

def rigid_datums(doc,parent,child,prefix):
    # Match native cardinal planes at the intended pose. Set the signed offset explicitly:
    # the closed mechanism can prevent a wrong-side distance mate from moving its component.
    pt=list(parent.Transform2.ArrayData);ct=list(child.Transform2.ArrayData)
    pr=np.array(pt[:9]).reshape(3,3);cr=np.array(ct[:9]).reshape(3,3)
    delta=np.array(ct[9:12])-np.array(pt[9:12])
    axes=[('Right Plane',0),('Top Plane',1),('Front Plane',2)]
    for cn,ci in axes:
        dots=pr@cr[ci];pi=int(np.argmax(np.abs(dots)));pn=axes[pi][0]
        align=0 if dots[pi]>0 else 1;signed=float(delta@pr[pi]);gap=abs(signed)
        entities=[mappedplane(parent,pn),mappedplane(child,cn)]
        label=prefix+'_'+cn.replace(' ','_')
        if gap<1e-8:mate(doc,0,label,entities,align)
        else:
            c(doc,'ClearSelection2',True)
            for ent in entities:entityselect(doc,ent)
            result=c(doc,'AddDistanceMate',align,signed<0,gap,gap,gap,0,0,iref())
            assert result is not None,('datum distance failed',label)
            result.Name=label
            fd=c(result,'GetDefinition');fd.FlipDimension=signed<0
            assert c(result,'ModifyDefinition',fd,doc,NULL)
            print('DATUM',label,flush=True)

def active_mates(doc):
    results=[];f=c(doc,'FirstFeature')
    while f:
        if c(f,'GetTypeName2')=='MateGroup':
            sub=c(f,'GetFirstSubFeature')
            while sub:
                if not c(sub,'IsSuppressed'):results.append(sub)
                sub=c(sub,'GetNextSubFeature')
        f=c(f,'GetNextFeature')
    return results

def errors(features):
    found=[]
    for f in features:
        warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
        code=c(f,'GetErrorCode2',warning)
        if code:found.append({'feature':f.Name,'code':code,'warning':warning.value})
    return found

def assemble_stop():
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    components={x.Name2:x for x in c(doc,'GetComponents',True)}
    assert not any('XY_Stop_' in n for n in components),'Stop already inserted'
    c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc))
    base=components['XY_Fixed_Base-1'];inner=next(x for x in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in x.Name2)
    bp=list(base.Transform2.ArrayData[9:12]);cp=list(inner.Transform2.ArrayData[9:12]);previous=[cp[0]-bp[0],cp[1]-bp[1]]
    save(doc)
    backup=Path(tempfile.mkdtemp(prefix='CycloProp_before_physical_stop_'))
    assembly_path=ROOT/'CAD'/'Assem20.SLDASM';shutil.copy2(assembly_path,backup/assembly_path.name)
    oldhash=hashlib.sha256(assembly_path.read_bytes()).hexdigest()
    assert set_axis_positions(doc,0.,0.)
    cp=list(inner.Transform2.ArrayData[9:12]);assert max(abs(cp[i]-bp[i]) for i in (0,1))<1e-6
    added={}
    def insert(key,file,x,y,z,parent):
        path=OUT/(file+'.SLDPRT');getdoc(path);activate(doc)
        comp=c(doc,'AddComponent5',str(path),0,'',False,'',x,y,z);assert comp is not None
        comp.Transform2=transform(0.,x,y,z)
        c(doc,'EditRebuild3')
        rigid_datums(doc,parent,comp,'Stop_'+key)
        added[key]=comp
        return comp
    fixed=insert('Fixed','XY_Stop_Fixed_Bracket_PROTOTYPE',*bp,base)
    arm=insert('Arm','XY_Stop_Moving_Arm_PROTOTYPE',cp[0],cp[1],cp[2]-.002,inner)
    pin=insert('Follower','XY_Stop_Follower_D6_M4_PROTOTYPE',cp[0]+.050,cp[1]+.050,cp[2]-.002,arm)
    washer=insert('Washer','M4_Washer_4p3x9x0p8_REFERENCE',cp[0]+.050,cp[1]+.050,cp[2],pin)
    nut=insert('Nut','M4_Locknut_AF7_H5_REFERENCE',cp[0]+.050,cp[1]+.050,cp[2]+.0008,pin)
    assert c(doc,'ForceRebuild3',False);assert not errors(active_mates(doc))
    s={'date':'2026-10-21','assembly_backup':str(backup/assembly_path.name),'pre_change_assembly_sha256':oldhash,
       'pre_change_offset_m':previous,'base_origin_m':bp,'components':{k:v.Name2 for k,v in added.items()}}
    STATE.write_text(json.dumps(s,indent=2))
    assert set_axis_positions(doc,*previous,restore_limits=True)
    assert not errors(active_mates(doc));save(doc)
    print('STOP_COMPONENTS',s['components'],'RESTORED_OFFSET_MM',[v*1000 for v in previous],flush=True)

def validate_stop():
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    state=json.loads(STATE.read_text());bp=np.array(state['base_origin_m']);names=state['components'];newnames=set(names.values())
    roots={x.Name2:x for x in c(doc,'GetComponents',True)}
    fixed=roots[names['Fixed']];pin=roots[names['Follower']]
    def cylinder(comp,r):
        matches=[]
        for body in c(c(comp,'GetModelDoc2'),'GetBodies2',0,False):
            for face in c(body,'GetFaces'):
                surface=c(face,'GetSurface')
                if c(surface,'IsCylinder') and abs(surface.CylinderParams[6]-r)<1e-8:matches.append((surface.CylinderParams,c(face,'GetBox')))
        assert matches,('Cylinder missing',comp.Name2,r)
        return matches[0]
    bore,borebox=cylinder(fixed,.00988);shaft,shaftbox=cylinder(pin,.003)
    radial_allowance=bore[6]-shaft[6]
    assert abs(radial_allowance-.00688)<1e-9
    records=[]
    for comp in c(doc,'GetComponents',False):
        part=c(comp,'GetModelDoc2')
        if part is None or c(part,'GetType')!=1:continue
        for i,body in enumerate(c(part,'GetBodies2',0,False) or []):
            b=c(body,'GetBodyBox');corners=np.array([[x,y,z] for x in (b[0],b[3]) for y in (b[1],b[4]) for z in (b[2],b[5])])
            template=c(body,'Copy');assert template is not None,('Cannot copy source body',comp.Name2,i)
            records.append({'component':comp,'name':comp.Name2,'body':template,'index':i,'corners':corners,'new':comp.Name2 in newnames})
    matefeatures=active_mates(doc);cache={};boolean_count=0;rows=[];probes=[]
    mu=c(app,'GetMathUtility')
    def tr(v):return c(mu,'CreateTransform',array(v))
    def intersect(a,at,b,bt):
        nonlocal boolean_count
        ac=c(a,'Copy');bc=c(b,'Copy');assert c(ac,'ApplyTransform',tr(at));assert c(bc,'ApplyTransform',tr(bt))
        result=c(ac,'Operations2',15901,bc,iref()) or [];boolean_count+=1
        return sum(c(body,'GetMassProperties',1.)[3]*1e9 for body in result)
    inner=next(x for x in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in x.Name2)
    samples=[(0.,0.)]+[(.00344*math.cos(i*math.pi/4),.00344*math.sin(i*math.pi/4)) for i in range(8)]+[(.00688*math.cos(i*math.pi/8),.00688*math.sin(i*math.pi/8)) for i in range(16)]
    fixedbody=next(r['body'] for r in records if r['name']==fixed.Name2);pinbody=next(r['body'] for r in records if r['name']==pin.Name2)
    try:
        for number,(dx,dy) in enumerate(samples):
            assert set_axis_positions(doc,dx,dy)
            me=errors(matefeatures);cp=inner.Transform2.ArrayData[9:12]
            actual=[cp[i]-bp[i] for i in (0,1)]
            row={'offset_mm':[dx*1000,dy*1000],'actual_offset_mm':[v*1000 for v in actual],'mate_errors':me,'interferences':[]}
            assert max(abs(actual[0]-dx),abs(actual[1]-dy))<1e-6
            transforms={};boxes=[]
            for item in records:
                name=item['name']
                if name not in transforms:transforms[name]=list(c(item['component'],'GetTotalTransform',True).ArrayData)
                v=transforms[name];corners=item['corners']@np.array(v[:9]).reshape(3,3)+np.array(v[9:12]);boxes.append((corners.min(axis=0),corners.max(axis=0)))
            for i,a in enumerate(records):
                at=transforms[a['name']];ar=np.array(at[:9]).reshape(3,3);amin,amax=boxes[i]
                for j in range(i):
                    b=records[j]
                    if a['name']==b['name'] or not(a['new'] or b['new']):continue
                    bmin,bmax=boxes[j]
                    if np.any(np.minimum(amax,bmax)-np.maximum(amin,bmin)<=1e-8):continue
                    bt=transforms[b['name']];br=np.array(bt[:9]).reshape(3,3)
                    rel=np.concatenate(((ar@br.T).flatten(),(np.array(at[9:12])-np.array(bt[9:12]))@br.T))
                    key=(i,j,tuple(np.round(rel,8)))
                    if key not in cache:cache[key]=intersect(a['body'],at,b['body'],bt)
                    volume=cache[key]
                    if volume>1e-6:row['interferences'].append({'components':[a['name'],b['name']],'volume_mm3':volume})
            ft=transforms[fixed.Name2];pt=transforms[pin.Name2]
            # Nominal stop circle and axial engagement, measured from native cylinders.
            axis=np.array([bore[0],bore[1],bore[2]])@np.array(ft[:9]).reshape(3,3)+np.array(ft[9:12])
            paxis=np.array([shaft[0],shaft[1],shaft[2]])@np.array(pt[:9]).reshape(3,3)+np.array(pt[9:12])
            separation=float(np.linalg.norm((paxis-axis)[:2]));row['stop_axis_separation_mm']=separation*1000
            assert abs(separation-math.hypot(dx,dy))<1e-6
            if number>=9:
                r=math.hypot(dx,dy);probe=list(pt);probe[9]+=.0001*dx/r;probe[10]+=.0001*dy/r
                overlap=intersect(pinbody,probe,fixedbody,ft)
                probes.append({'direction_offset_mm':[dx*1000,dy*1000],'tested_radius_mm':6.98,'overlap_mm3':overlap})
                assert overlap>1e-6,'Overtravel must be blocked geometrically'
            rows.append(row)
            print('STOP_SAMPLE',number,'OFFSET_MM',row['offset_mm'],'MATE_ERRORS',len(me),'NEW_INTERFERENCES',len(row['interferences']),flush=True)
            if row['interferences']:print(json.dumps(row['interferences']),flush=True)
        # Check the user's problematic simultaneous-axis corner using copies only.
        assert set_axis_positions(doc,0.,0.)
        pt=list(c(pin,'GetTotalTransform',True).ArrayData);ft=list(c(fixed,'GetTotalTransform',True).ArrayData)
        pt[9]+=.00688;pt[10]+=.00688
        corner_overlap=intersect(pinbody,pt,fixedbody,ft);assert corner_overlap>1e-6
    finally:
        assert set_axis_positions(doc,*state['pre_change_offset_m'],restore_limits=True)
    final_errors=errors(active_mates(doc));assert not final_errors
    checks={'native_dimensions':'passed','settled_positions':'passed' if all(not row['mate_errors'] and not row['interferences'] for row in rows) else 'failed',
            'overtravel_intersection_probes':'passed' if len(probes)==16 and all(p['overlap_mm3']>1e-6 for p in probes) else 'failed',
            'full_continuous_motion':'not performed','impact_load_capacity':'not performed','tolerance_stack':'not performed',
            'physical_mounting_fasteners':'not defined'}
    result={'date':'2026-10-21','status':'PROVISIONAL','checks':checks,'nominal_bore_diameter_mm':bore[6]*2000,
       'nominal_follower_diameter_mm':shaft[6]*2000,'nominal_radial_allowance_mm':radial_allowance*1000,
       'follower_shank_length_mm':(shaftbox[5]-shaftbox[2])*1000,'ring_axial_thickness_mm':(borebox[5]-borebox[2])*1000,
       'sample_count':len(rows),'sampled_positions':rows,'overtravel_probes':probes,'simultaneous_6p88_axes_corner_overlap_mm3':corner_overlap,
       'native_boolean_checks':boolean_count,'active_mates':len(active_mates(doc)),'final_mate_errors':final_errors,
       'restored_prior_offset_mm':[v*1000 for v in state['pre_change_offset_m']],
       'assumptions':['Rigid nominal geometry','Control ring held at saved angular position','Existing-existing component pairs excluded from new-stop checks',
                      'Threaded fasteners use envelopes, not modelled thread flanks','Coincident zero-volume contact is allowed','Mount pads use datum mates without fabrication fasteners']}
    assert checks['settled_positions']=='passed' and checks['overtravel_intersection_probes']=='passed'
    save(doc);result['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'CAD'/'Assem20.SLDASM']+list(OUT.glob('*.SLDPRT'))}
    (OUT/'STOP_VALIDATION.json').write_text(json.dumps(result,indent=2))
    print('STOP_VALIDATION_PASSED','POSITIONS',len(rows),'BOOLS',boolean_count,'CORNER_OVERLAP_MM3',corner_overlap,flush=True)

if __name__=='__main__':
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    view=doc.ActiveView;app.CommandInProgress=True;view.EnableGraphicsUpdate=False
    try:
        if sys.argv[1]=='parts':make_stop_parts()
        elif sys.argv[1]=='assemble':assemble_stop()
        elif sys.argv[1]=='validate':validate_stop()
    finally:
        view.EnableGraphicsUpdate=True;app.CommandInProgress=False;c(doc,'GraphicsRedraw2')
