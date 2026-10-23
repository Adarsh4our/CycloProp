import math, sys, json, shutil, tempfile
from pathlib import Path
import pythoncom, win32com.client, win32com.client.dynamic

pythoncom.CoInitialize()
app = win32com.client.dynamic.Dispatch('SldWorks.Application')
ROOT = Path(r'C:\Users\Adarsh Singh\CycloProp')
OUT = ROOT / 'CAD' / 'Servo_Actuation_Prototype'
OUT.mkdir(exist_ok=True)
NULL = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)

def c(o, name, *args):
    o._FlagAsMethod(name)
    return getattr(o, name)(*args)

def iref():
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

def array(items, typ=pythoncom.VT_R8):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | typ, items)

def activate(doc):
    c(app, 'ActivateDoc2', c(doc, 'GetTitle'), False, iref())

def getdoc(path, kind=1, readonly=False):
    d = c(app, 'GetOpenDocumentByName', str(path))
    if d is None:
        e,w=iref(),iref()
        d=c(app,'OpenDoc6',str(path),kind,3 if readonly else 1,'',e,w)
        assert d is not None, (path,e.value,w.value)
    return d

def save(doc,path=None):
    e,w=iref(),iref()
    if path is None:
        ok=c(doc,'Save3',1,e,w)
    else:
        ok=c(doc.Extension,'SaveAs',str(path),0,1,NULL,e,w)
    assert ok and e.value==0, ('save',path,e.value,w.value)
    print('SAVED', path or c(doc,'GetPathName'),flush=True)

def properties(doc, description):
    mgr=doc.Extension.CustomPropertyManager('')
    for key,val in [('DESIGN_STATUS','PROVISIONAL ACTUATION LAYOUT - NOT FOR FABRICATION'),
                    ('DESIGN_DESCRIPTION',description),
                    ('HARDWARE_VERIFICATION','Actual horn, pins, mounting fasteners, fits and load capability pending')]:
        c(mgr,'Add3',key,30,val,2)

def sketch(doc):
    activate(doc)
    c(doc,'ClearSelection2',True)
    assert c(doc.Extension,'SelectByID2','Front Plane','PLANE',0.,0.,0.,False,0,NULL,0)
    c(doc.SketchManager,'InsertSketch',True)
    doc.SketchManager.AddToDB=True

def rect(doc,x0,y0,x1,y1):
    return c(doc.SketchManager,'CreateCornerRectangle',x0/1000,y0/1000,0.,x1/1000,y1/1000,0.)

def circle(doc,x,y,r):
    return c(doc.SketchManager,'CreateCircleByRadius',x/1000,y/1000,0.,r/1000)

def extrude(doc,z0,z1,name):
    sk=doc.SketchManager.ActiveSketch
    doc.SketchManager.AddToDB=False
    c(doc.SketchManager,'InsertSketch',True)
    c(doc,'ClearSelection2',True)
    sf=None; f=c(doc,'FirstFeature')
    while f:
        if c(f,'GetTypeName2')=='ProfileFeature':sf=f
        f=c(f,'GetNextFeature')
    assert sf is not None and c(sf,'Select2',False,0)
    feat=c(doc.FeatureManager,'FeatureExtrusion2',True,False,False,0,0,
           (z1-z0)/1000,0.,False,False,False,False,0.,0.,False,False,
           False,False,True,True,True,3 if z0 else 0,abs(z0)/1000,z0<0)
    assert feat is not None, ('extrude failed',name)
    feat.Name=name
    return feat

def box(doc,x0,y0,x1,y1,z0,z1,name,holes=(),opening=None):
    sketch(doc);rect(doc,x0,y0,x1,y1)
    if opening:rect(doc,*opening)
    for x,y,r in holes:circle(doc,x,y,r)
    return extrude(doc,z0,z1,name)

def newpart(name,description):
    path=OUT/(name+'.SLDPRT')
    assert not path.exists(), 'Refusing to overwrite '+str(path)
    template=c(app,'GetUserPreferenceStringValue',8)
    assert template, 'No part template configured'
    doc=c(app,'NewDocument',template,0,0.,0.)
    assert doc is not None
    properties(doc,description)
    return doc,path

def finish(doc,path):
    assert c(doc,'EditRebuild3')
    bodies=c(doc,'GetBodies2',0,False) or []
    assert len(bodies)==1, ('expected one merged body',path,len(bodies))
    print('PART',path.name,'BBOX',c(bodies[0],'GetBodyBox'),flush=True)
    save(doc,path)

def make_parts():
    d,p=newpart('Servo_Horn_R12_LAYOUT','12 mm effective radius; 5.2 mm clearance centre is an envelope, NOT a working spline. Replace with measured Savox 21T horn.')
    box(d,-4,-4,16,4,0,2,'R12_Horn_Envelope',[(0,0,2.6),(12,0,1.05)])
    finish(d,p)
    d,p=newpart('Servo_Link_L40_PROTOTYPE','40 mm pin centre distance; 2.1 mm nominal eye holes, 2 mm plate. Pin hardware and loads unverified.')
    box(d,-3,-3,43,3,0,2,'L40_Link',[(0,0,1.05),(40,0,1.05)])
    finish(d,p)
    for name,drop in [('Servo_X_Mount_PROTOTYPE',21.480025),('Servo_Y_Mount_PROTOTYPE',30.480025)]:
        d,p=newpart(name,'Mounting shelf fitted around inspected servo envelope; base attachment and servo screw holes deferred to measured hardware.')
        box(d,-70,0,-22,38,-drop-3,-drop,'Servo_Shelf',opening=(-66.5,6.65,-53.5,31.0))
        box(d,-40,14,-34,28,-drop-1,-1,'Outboard_Riser')
        box(d,-40,14,-20,28,-2,0,'Plate_Attachment_Foot')
        finish(d,p)
    d,p=newpart('X_Slider_Drive_Tab_PROTOTYPE','Attaches beneath intermediate plate; 2 mm foot clears rail by approximately 0.4 mm nominal. Fastener layout pending.')
    box(d,-26,31,-14,40,-11.5,-9.5,'Link_Eye_Shelf',[(-20,36,1.05)])
    box(d,-26,31,-14,34,-10.5,-1,'Outboard_Web')
    box(d,-26,24,-14,34,-2,0,'Intermediate_Plate_Foot')
    finish(d,p)
    d,p=newpart('Y_Carriage_Drive_Tab_PROTOTYPE','Attaches beneath bearing carriage; 2 mm foot avoids upper block and clears rail. Fastener layout pending.')
    box(d,-44,-26,-32,-14,-20.5,-18.5,'Link_Eye_Shelf',[(-36,-20,1.05)])
    box(d,-44,-26,-41,-14,-19.5,-1,'Outboard_Web')
    box(d,-44,-26,-16,-14,-2,0,'Carriage_Plate_Foot')
    finish(d,p)
    d,p=newpart('Pivot_Pin_D2_REFERENCE','2 mm smooth shank x 6 mm with 4 mm head x 1 mm. Kinematic reference; retention/thread/hardware not specified.')
    sketch(d);circle(d,0,0,2);extrude(d,-1,0,'Reference_Head')
    sketch(d);circle(d,0,0,1);extrude(d,0,6,'Reference_Shank')
    finish(d,p)

def servo_reference():
    path=OUT/'Savox_SH0257MG_INTERFACE_REFERENCE.SLDPRT'
    assert not path.exists()
    shutil.copy2(ROOT/'CAD'/'Savox_SH-0257MG.SLDPRT',path)
    d=getdoc(path);activate(d)
    properties(d,'Original Savox geometry copied unchanged. Added output axis at x=123.5 y=-47.15 mm, from symmetric output-body vertices. Actual horn and spline engagement remain unverified.')
    c(d,'ClearSelection2',True)
    c(d.SketchManager,'Insert3DSketch',True)
    line=c(d.SketchManager,'CreateLine',.1235,-.04715,.02528,.1235,-.04715,.03228)
    c(d.SketchManager,'Insert3DSketch',True)
    c(d,'ClearSelection2',True)
    sd=c(d.SelectionManager,'CreateSelectData');sd.Mark=0
    assert c(line,'Select4',False,sd)
    assert c(d,'InsertAxis2',True)
    f=c(d,'FirstFeature');axis=None
    while f:
        if c(f,'GetTypeName2')=='RefAxis':axis=f
        f=c(f,'GetNextFeature')
    assert axis is not None
    axis.Name='Measured_CAD_Output_Axis'
    save(d)

def transform(angle,x,y,z):
    cs,sn=math.cos(angle),math.sin(angle)
    return c(c(app,'GetMathUtility'),'CreateTransform',array((cs,sn,0.,-sn,cs,0.,0.,0.,1.,x,y,z,1.,0.,0.,0.)))

def sd(doc):
    s=c(doc.SelectionManager,'CreateSelectData');s.Mark=1;return s

def compselect(doc,comp):
    assert c(comp,'Select4',True,sd(doc),False),('component selection',comp.Name2)

def mappedplane(comp,name='Front Plane'):
    return c(comp,'GetCorresponding',c(c(comp,'GetModelDoc2'),'FeatureByName',name))

def cyl(comp,x,y,r):
    part=c(comp,'GetModelDoc2')
    for body in c(part,'GetBodies2',0,False):
        for face in c(body,'GetFaces'):
            surf=c(face,'GetSurface')
            if c(surf,'IsCylinder'):
                p=surf.CylinderParams
                if abs(p[0]-x)<1e-7 and abs(p[1]-y)<1e-7 and abs(p[6]-r)<1e-7:
                    return c(comp,'GetCorrespondingEntity',face)
    raise RuntimeError(('cylinder missing',comp.Name2,x,y,r))

def entityselect(doc,entity):
    try:ok=c(entity,'Select4',True,sd(doc))
    except Exception:ok=c(entity,'Select2',True,1)
    assert ok,'Entity selection failed'

def mate(doc,kind,name,entities,alignment=0):
    c(doc,'ClearSelection2',True)
    for ent in entities:entityselect(doc,ent)
    fd=c(doc,'CreateMateData',kind)
    if kind!=16:fd.MateAlignment=alignment
    result=c(doc,'CreateMate',fd)
    assert result is not None,('Mate creation failed',name)
    result.Name=name
    print('MATE',name,flush=True)
    return result

def lock(doc,a,b,name):
    c(doc,'EditRebuild3')
    c(doc,'ClearSelection2',True)
    compselect(doc,a);compselect(doc,b)
    fd=c(doc,'CreateMateData',16)
    fd.EntitiesToMate=array([a,b],pythoncom.VT_DISPATCH)
    result=c(doc,'CreateMate',fd)
    assert result is not None,('lock failed',name)
    result.Name=name;print('LOCK',name,flush=True)

def axial(doc,ref,moving,gap,name):
    target=ref.Transform2.ArrayData[11]+gap
    c(doc,'ClearSelection2',True)
    for comp in (ref,moving):entityselect(doc,mappedplane(comp))
    e=iref();result=c(doc,'AddDistanceMate',0,False,gap,gap,gap,0,0,e)
    assert result is not None,('distance failed',name,e.value)
    result.Name=name
    if abs(moving.Transform2.ArrayData[11]-target)>1e-6:
        fd=c(result,'GetDefinition');fd.FlipDimension=not fd.FlipDimension
        assert c(result,'ModifyDefinition',fd,doc,NULL)
    assert abs(moving.Transform2.ArrayData[11]-target)<1e-6,('wrong axial position',name)
    print('AXIAL',name,flush=True)

def assemble():
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    assert not any('Servo_Horn_R12' in x.Name2 for x in c(doc,'GetComponents',True)),'Already inserted'
    save(doc)
    backup=Path(tempfile.mkdtemp(prefix='CycloProp_before_servo_layout_'))/'Assem20.SLDASM'
    shutil.copy2(c(doc,'GetPathName'),backup);print('ASSEMBLY_BACKUP',backup,flush=True)
    comps={x.Name2:x for x in c(doc,'GetComponents',True)}
    base=comps['XY_Fixed_Base-1'];middle=comps['Intermediate_X_Slider-1'];carrier=comps['Assem3-1']
    inner=next(x for x in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in x.Name2)
    bp=base.Transform2.ArrayData[9:12];ip=middle.Transform2.ArrayData[9:12];cp=inner.Transform2.ArrayData[9:12]
    if math.hypot(cp[0]-bp[0],cp[1]-bp[1])>=1e-5:
        dx,dy=bp[0]-cp[0],bp[1]-cp[1]
        for name in ('Intermediate_X_Slider-1','MGNR05R-1','MGN5C-2','MGN5C-1','Assem3-1'):
            v=list(comps[name].Transform2.ArrayData);v[9]+=dx
            if name in ('MGN5C-1','Assem3-1'):v[10]+=dy
            comps[name].Transform2=c(c(app,'GetMathUtility'),'CreateTransform',array(v))
        assert c(doc,'EditRebuild3')
        ip=middle.Transform2.ArrayData[9:12];cp=inner.Transform2.ArrayData[9:12]
        assert math.hypot(cp[0]-bp[0],cp[1]-bp[1])<1e-5,'Centre positioning failed'
    assert abs(cp[2]-bp[2]-.018)<1e-6
    added={}
    def add(key,file,angle,x,y,z):
        path=OUT/(file+'.SLDPRT');getdoc(path);activate(doc)
        comp=c(doc,'AddComponent5',str(path),0,'',False,'',x,y,z)
        assert comp is not None,('insert',file)
        comp.Transform2=transform(angle,x,y,z)
        added[key]=comp
        return comp
    for key,file,parent,angle,pos in [
        ('mountX','Servo_X_Mount_PROTOTYPE',base,0.,bp),
        ('mountY','Servo_Y_Mount_PROTOTYPE',middle,math.pi/2,ip),
        ('tabX','X_Slider_Drive_Tab_PROTOTYPE',middle,0.,ip),
        ('tabY','Y_Carriage_Drive_Tab_PROTOTYPE',carrier,0.,cp)]:
        obj=add(key,file,angle,*pos);lock(doc,parent,obj,key+'_Attachment_LAYOUT')
    for key,parent,angle,sx,sy in [('servoX',base,0.,-.060,.024),('servoY',middle,math.pi/2,-.024,-.060)]:
        cs,sn=math.cos(angle),math.sin(angle)
        # Both output faces are 8 mm behind the fixed base's bottom face.
        axisx,axisy=bp[0]+sx,bp[1]+sy
        x=axisx-(cs*.1235-sn*(-.04715));y=axisy-(sn*.1235+cs*(-.04715))
        obj=add(key,'Savox_SH0257MG_INTERFACE_REFERENCE',angle,x,y,bp[2]-.039280025)
        lock(doc,parent,obj,key+'_Case_Attachment_LAYOUT')
    for axis,hangle,sx,sy,lex,ley,lang in [('X',math.pi/2,-.060,.024,-.060,.036,0.),('Y',math.pi,-.024,-.060,-.036,-.060,math.pi/2)]:
        servo=added['servo'+axis]
        horn=add('horn'+axis,'Servo_Horn_R12_LAYOUT',hangle,bp[0]+sx,bp[1]+sy,bp[2]-.0105)
        hornseed=horn.Transform2
        ref=c(servo,'GetCorresponding',c(c(servo,'GetModelDoc2'),'FeatureByName','Measured_CAD_Output_Axis'))
        mate(doc,1,axis+'_Horn_Output_Axis',[ref,cyl(horn,0.,0.,.0026)])
        axial(doc,servo,horn,.028780025,axis+'_Horn_Axial_Envelope')
        horn.Transform2=hornseed;c(doc,'EditRebuild3')
        link=add('link'+axis,'Servo_Link_L40_PROTOTYPE',lang,bp[0]+lex,bp[1]+ley,bp[2]-.008)
        linkseed=link.Transform2
        mate(doc,1,axis+'_Horn_Link_Pivot',[cyl(horn,.012,0.,.00105),cyl(link,0.,0.,.00105)])
        axial(doc,horn,link,.0025,axis+'_Link_Stack_Gap')
        link.Transform2=linkseed;c(doc,'EditRebuild3')
        tab=added['tab'+axis];tx,ty=(-.020,.036) if axis=='X' else (-.036,-.020)
        mate(doc,1,axis+'_Link_Slider_Pivot',[cyl(link,.040,0.,.00105),cyl(tab,tx,ty,.00105)])
        for end,px,py,pz,parent in [('Horn',lex,ley,-.011,horn),('Slider',tx,ty,-.0085,tab)]:
            pin=add('pin'+axis+end,'Pivot_Pin_D2_REFERENCE',0.,bp[0]+px,bp[1]+py,bp[2]+pz)
            lock(doc,parent,pin,axis+'_'+end+'_Pin_REFERENCE')
    print('ASSEMBLY_REBUILD',c(doc,'EditRebuild3'),flush=True)
    f=c(doc,'FeatureByName','Combined_XY_Radial_Limit_6p88mm');fd=c(f,'GetDefinition')
    fd.MinimumDistance=0.;fd.MaximumDistance=math.hypot(.018,.00688)+1e-9
    assert c(f,'ModifyDefinition',fd,doc,NULL)
    state={'backup':str(backup),'base_origin':list(bp),'layout_drop_mm':3.,'added':{k:v.Name2 for k,v in added.items()}}
    Path(tempfile.gettempdir(),'CycloProp_servo_layout_state.json').write_text(json.dumps(state,indent=2))
    c(doc,'ClearSelection2',True)
    save(doc)
    c(doc,'ShowNamedView2','*Isometric',7);c(doc,'ViewZoomtofit2')
    c(doc,'SaveBMP',str(Path(tempfile.gettempdir())/'CycloProp_servo_layout.bmp'),1500,1100)

def validate():
    import numpy as np
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    state=json.loads(Path(tempfile.gettempdir(),'CycloProp_servo_layout_state.json').read_text())
    bp=state['base_origin'];names=state['added'];keys={v:k for k,v in names.items()};drop=state.get('layout_drop_mm',0.)/1000
    components={x.Name2:x for x in c(doc,'GetComponents',True)}
    seed={n:list(x.Transform2.ArrayData) for n,x in components.items()}
    newnames=set(names.values())
    mu=c(app,'GetMathUtility')
    def tr(v):return c(mu,'CreateTransform',array(v))
    def vec(angle,x,y,z):return list(transform(angle,x,y,z).ArrayData)
    def theta(displacement):
        lo,hi=-math.pi/4,math.pi/4
        for _ in range(70):
            t=(lo+hi)/2
            f=.012*math.sin(t)+math.sqrt(.040**2-(.012*(1-math.cos(t)))**2)-.040
            if f<displacement:lo=t
            else:hi=t
        return (lo+hi)/2
    records=[]
    selected_old=('XY_Fixed_Base','Intermediate_X_Slider','4-Inner_Carriage_Plate','4-Outer_Control_Ring','Inner_Race_Retainer','Outer_Race_Retainer','MGN5C-','MGNR05R-','3-Drive_Shaft-')
    for comp in c(doc,'GetComponents',False):
        if comp.Name2 not in newnames and not any(s in comp.Name2 for s in selected_old):continue
        part=c(comp,'GetModelDoc2')
        if c(part,'GetType')!=1:continue
        for j,body in enumerate(c(part,'GetBodies2',0,False) or []):
            box=c(body,'GetBodyBox');corners=np.array([[x,y,z] for x in (box[0],box[3]) for y in (box[1],box[4]) for z in (box[2],box[5])])
            records.append({'name':comp.Name2,'comp':comp,'body':body,'index':j,'new':comp.Name2 in newnames,'seed':list(c(comp,'GetTotalTransform',True).ArrayData),'corners':corners})
    def positions(dx,dy):
        poses={n:list(v) for n,v in seed.items()}
        xkeys={'mountY','tabX','servoY'}
        xykeys={'tabY'}
        for n,v in poses.items():
            k=keys.get(n)
            if n in ('Intermediate_X_Slider-1','MGNR05R-1','MGN5C-2') or k in xkeys:v[9]+=dx
            elif n in ('MGN5C-1','Assem3-1') or k in xykeys:v[9]+=dx;v[10]+=dy
        for axis,displacement,sx,sy,neutral,tx,ty in [('X',dx,-.060,.024,math.pi/2,-.020,.036),('Y',dy,-.024,-.060,math.pi,-.036,-.020)]:
            t=theta(displacement);angle=neutral-t
            shift=dx if axis=='Y' else 0.
            hx,hy=bp[0]+sx+shift,bp[1]+sy
            px,py=hx+.012*math.cos(angle),hy+.012*math.sin(angle)
            endx,endy=bp[0]+tx+dx,bp[1]+ty+(dy if axis=='Y' else 0.)
            poses[names['horn'+axis]]=vec(angle,hx,hy,bp[2]-.0075-drop)
            poses[names['link'+axis]]=vec(math.atan2(endy-py,endx-px),px,py,bp[2]-.005-drop)
            poses[names['pin'+axis+'Horn']]=vec(-t,px,py,bp[2]-.008-drop)
            poses[names['pin'+axis+'Slider']]=vec(0.,endx,endy,bp[2]-.0055-drop)
        return poses
    matefeatures=[];f=c(doc,'FirstFeature')
    while f:
        if c(f,'GetTypeName2')=='MateGroup':
            s=c(f,'GetFirstSubFeature')
            while s:
                if not c(s,'IsSuppressed'):matefeatures.append(s)
                s=c(s,'GetNextSubFeature')
        f=c(f,'GetNextFeature')
    def all_mate_errors():
        errors=[]
        for s in matefeatures:
            w=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
            er=c(s,'GetErrorCode2',w)
            if er:errors.append((s.Name,er))
        return errors
    drivers={'Intermediate_X_Slider-1','MGNR05R-1','MGN5C-2','MGN5C-1','Assem3-1'}|{names[k] for k in ('hornX','hornY','linkX','linkY')}
    radial=c(doc,'FeatureByName','Combined_XY_Radial_Limit_6p88mm')
    def drive(dx,dy):
        assert c(radial,'SetSuppression2',0,1,None)
        for fn,distance in [('LimitDistance3',.012+dx),('LimitDistance1',.012+dy)]:
            feature=c(doc,'FeatureByName',fn);fd=c(feature,'GetDefinition')
            fd.IsAdvancedMate=False;fd.Distance=distance
            assert c(feature,'ModifyDefinition',fd,doc,NULL)
        c(doc,'EditRebuild3')
        assert c(radial,'SetSuppression2',1,1,None)
        return c(doc,'EditRebuild3')
    samples=[(0.,0.)]+[(.00688*math.cos(i*math.pi/8),.00688*math.sin(i*math.pi/8)) for i in range(16)]
    summary=[];collisions=[];boolean_checks=0;intersection_cache={}
    for sample,(dx,dy) in enumerate(samples):
        poses=positions(dx,dy)
        if state.get('neutral_axis_drivers'):
            # Drive the actual mate dimensions; allow rigid followers to move through their mates.
            rebuilt=drive(dx,dy)
        else:
            for name,v in poses.items():
                if name in drivers:components[name].Transform2=tr(v)
            rebuilt=c(doc,'EditRebuild3')
        errors=all_mate_errors()
        actual={n:list(x.Transform2.ArrayData) for n,x in components.items()}
        pose_errors=[]
        for n,expected in poses.items():
            if np.max(np.abs(np.array(actual[n])-np.array(expected)))>1e-6:pose_errors.append(n)
        row={'offset_mm':[dx*1000,dy*1000],'rebuilt':rebuilt,'mate_errors':errors,'component_pose_errors':pose_errors,'collisions':[]}
        transformed=[]
        for r in records:
            n=r['name']
            if n in actual:v=actual[n]
            else:v=list(c(r['comp'],'GetTotalTransform',True).ArrayData)
            pts=r['corners']@np.array(v[:9]).reshape(3,3)+np.array(v[9:12])
            transformed.append((v,pts.min(axis=0),pts.max(axis=0)))
        for i,ra in enumerate(records):
            va,amin,amax=transformed[i]
            for j in range(i):
                rb=records[j]
                if ra['name']==rb['name'] or not (ra['new'] or rb['new']):continue
                vb,bmin,bmax=transformed[j]
                if np.any(np.minimum(amax,bmax)-np.maximum(amin,bmin)<=1e-8):continue
                ar=np.array(va[:9]).reshape(3,3);br=np.array(vb[:9]).reshape(3,3)
                relative=np.concatenate(((ar@br.T).flatten(),(np.array(va[9:12])-np.array(vb[9:12]))@br.T))
                cachekey=(i,j,tuple(np.round(relative,8)))
                if cachekey in intersection_cache:volume=intersection_cache[cachekey]
                else:
                    ac=c(ra['body'],'Copy');bc=c(rb['body'],'Copy')
                    assert c(ac,'ApplyTransform',tr(va));assert c(bc,'ApplyTransform',tr(vb))
                    er=iref();ints=c(ac,'Operations2',15901,bc,er) or []
                    volume=sum(c(b,'GetMassProperties',1.)[3]*1e9 for b in ints);boolean_checks+=1
                    intersection_cache[cachekey]=volume
                if volume>1e-6:
                    hit={'components':[ra['name'],rb['name']],'volume_mm3':volume,'offset_mm':row['offset_mm']}
                    collisions.append(hit);row['collisions'].append(hit)
        summary.append(row)
        print('SAMPLE',sample,'OFFSET_MM',row['offset_mm'],'MATE_ERRORS',len(errors),'POSE_ERRORS',pose_errors,'NEW_INTERFERENCES',len(row['collisions']),flush=True)
        if row['collisions']:print(json.dumps(row['collisions']),flush=True)
    # Restore neutral and save only a model with no active mate errors.
    if state.get('neutral_axis_drivers'):
        drive(0.,0.)
        for fn in ('LimitDistance1','LimitDistance3'):
            feature=c(doc,'FeatureByName',fn);fd=c(feature,'GetDefinition')
            fd.IsAdvancedMate=True;fd.Distance=.012;fd.MinimumDistance=.00512;fd.MaximumDistance=.01888
            assert c(feature,'ModifyDefinition',fd,doc,NULL)
        state['neutral_axis_drivers']=False
        Path(tempfile.gettempdir(),'CycloProp_servo_layout_state.json').write_text(json.dumps(state,indent=2))
    else:
        for name,v in positions(0.,0.).items():
            if name in drivers:components[name].Transform2=tr(v)
    assert c(doc,'EditRebuild3');errors=all_mate_errors()
    result={'status':'PROVISIONAL','sample_count':len(samples),'native_boolean_checks':boolean_checks,
      'native_bodies':len(records),'neutral_mate_errors':errors,'samples':summary,
      'crank_angles_at_extremes_deg':[math.degrees(theta(-.00688)),math.degrees(theta(.00688))],
      'assumptions':['Rigid components and nominal CAD geometry','Existing control ring angle held fixed','Original-original intersections and internal servo-body intersections excluded','Reference horn is not a manufactured spline','No physical fasteners except reference pivot pins modelled','No full-motion proof or load/mass approval']}
    (OUT/'PROTOTYPE_VALIDATION.json').write_text(json.dumps(result,indent=2))
    print('VALIDATION_SUMMARY',len(samples),boolean_checks,'COLLISIONS',len(collisions),'NEUTRAL_ERRORS',errors,flush=True)
    assert not errors,'Neutral model has mate errors'
    save(doc)
    return result

def clearance_fix():
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    statefile=Path(tempfile.gettempdir(),'CycloProp_servo_layout_state.json')
    state=json.loads(statefile.read_text());assert state.get('layout_drop_mm',0.)==0.
    backup=Path(tempfile.mkdtemp(prefix='CycloProp_servo_clearance_revision_'))
    for path in [ROOT/'CAD'/'Assem20.SLDASM']+list(OUT.glob('*.SLDPRT')):shutil.copy2(path,backup/path.name)
    print('CLEARANCE_BACKUP',backup,flush=True)
    # Suspend only locks whose stored relative placement changes.
    for name in ('servoX_Case_Attachment_LAYOUT','servoY_Case_Attachment_LAYOUT','X_Slider_Pin_REFERENCE','Y_Slider_Pin_REFERENCE'):
        f=c(doc,'FeatureByName',name);assert c(f,'SetSuppression2',0,1,None)
    for filename,features in [
        ('Servo_X_Mount_PROTOTYPE',[('Servo_Shelf',False),('Outboard_Riser',True)]),
        ('Servo_Y_Mount_PROTOTYPE',[('Servo_Shelf',False),('Outboard_Riser',True)]),
        ('X_Slider_Drive_Tab_PROTOTYPE',[('Link_Eye_Shelf',False),('Outboard_Web',True)]),
        ('Y_Carriage_Drive_Tab_PROTOTYPE',[('Link_Eye_Shelf',False),('Outboard_Web',True)])]:
        part=getdoc(OUT/(filename+'.SLDPRT'));activate(part)
        for name,grow in features:
            feature=c(part,'FeatureByName',name);fd=c(feature,'GetDefinition')
            assert c(fd,'AccessSelections',part,NULL)
            fd.FromOffsetDistance+=.003
            if grow:c(fd,'SetDepth',True,c(fd,'GetDepth',True)+.003)
            assert c(feature,'ModifyDefinition',fd,part,NULL)
        assert c(part,'EditRebuild3');save(part)
    part=getdoc(OUT/'Pivot_Pin_D2_REFERENCE.SLDPRT');activate(part)
    f=c(part,'FeatureByName','Reference_Shank');fd=c(f,'GetDefinition');assert c(fd,'AccessSelections',part,NULL)
    c(fd,'SetDepth',True,.0075);assert c(f,'ModifyDefinition',fd,part,NULL)
    properties(part,'2 mm reference shank x 7.5 mm; 4 mm head x 1 mm. Reserves 2.5 mm beyond mating plate for retention; actual hardware and thread selection pending.')
    assert c(part,'EditRebuild3');save(part)
    activate(doc)
    comps={x.Name2:x for x in c(doc,'GetComponents',True)};names=state['added']
    for key in ('servoX','servoY','hornX','hornY','linkX','linkY','pinXHorn','pinXSlider','pinYHorn','pinYSlider'):
        obj=comps[names[key]];v=list(obj.Transform2.ArrayData);v[11]-=.003
        obj.Transform2=c(c(app,'GetMathUtility'),'CreateTransform',array(v))
    for key,parent,newname in [
        ('servoX','XY_Fixed_Base-1','servoX_Case_Attachment_REV2'),
        ('servoY','Intermediate_X_Slider-1','servoY_Case_Attachment_REV2'),
        ('pinXSlider',names['tabX'],'X_Slider_Pin_REFERENCE_REV2'),
        ('pinYSlider',names['tabY'],'Y_Slider_Pin_REFERENCE_REV2')]:lock(doc,comps[parent],comps[names[key]],newname)
    f=c(doc,'FeatureByName','Combined_XY_Radial_Limit_6p88mm');fd=c(f,'GetDefinition')
    # Zero lower bound is sufficient because the existing stack fixes the axial separation.
    # A 1 nm distance allowance prevents floating-point flags at the nominal outer boundary.
    fd.MinimumDistance=0.;fd.MaximumDistance=math.hypot(.018,.00688)+1e-9
    assert c(f,'ModifyDefinition',fd,doc,NULL)
    state['layout_drop_mm']=3.;state['clearance_revision_backup']=str(backup)
    statefile.write_text(json.dumps(state,indent=2))
    c(doc,'ClearSelection2',True);print('CLEARANCE_REBUILD',c(doc,'ForceRebuild3',False),flush=True)
    save(doc)

def rigid_repair():
    import numpy as np
    doc=getdoc(ROOT/'CAD'/'Assem20.SLDASM',2);activate(doc)
    s=json.loads(Path(tempfile.gettempdir(),'CycloProp_servo_layout_state.json').read_text());bp=s['base_origin'];names=s['added']
    comps={x.Name2:x for x in c(doc,'GetComponents',True)}
    inner=next(x for x in c(doc,'GetComponents',False) if '4-Inner_Carriage_Plate' in x.Name2)
    for n in ('mountX_Attachment_LAYOUT','mountY_Attachment_LAYOUT','tabX_Attachment_LAYOUT','tabY_Attachment_LAYOUT','servoX_Case_Attachment_LAYOUT','servoY_Case_Attachment_LAYOUT','X_Horn_Pin_REFERENCE','X_Slider_Pin_REFERENCE','Y_Horn_Pin_REFERENCE','Y_Slider_Pin_REFERENCE'):
        assert c(c(doc,'FeatureByName',n),'SetSuppression2',0,1,None)
    # Hold both slides at neutral while defining rigid datum-plane attachments.
    for n in ('LimitDistance1','LimitDistance3'):
        f=c(doc,'FeatureByName',n);fd=c(f,'GetDefinition');fd.IsAdvancedMate=False;fd.Distance=.012
        assert c(f,'ModifyDefinition',fd,doc,NULL)
    c(doc,'EditRebuild3')
    poses={
      'mountX':(0.,0.,0.,0.),'mountY':(math.pi/2,0.,0.,.009),
      'tabX':(0.,0.,0.,.009),'tabY':(0.,0.,0.,.018),
      'servoX':(0.,-.1835,.07115,-.039280025),
      'servoY':(math.pi/2,-.07115,-.1835,-.039280025),
      'hornX':(math.pi/2,-.060,.024,-.0105),'hornY':(math.pi,-.024,-.060,-.0105),
      'linkX':(0.,-.060,.036,-.008),'linkY':(math.pi/2,-.036,-.060,-.008),
      'pinXHorn':(0.,-.060,.036,-.011),'pinXSlider':(0.,-.020,.036,-.0085),
      'pinYHorn':(0.,-.036,-.060,-.011),'pinYSlider':(0.,-.036,-.020,-.0085)}
    for key,(angle,x,y,z) in poses.items():comps[names[key]].Transform2=transform(angle,bp[0]+x,bp[1]+y,bp[2]+z)
    c(doc,'EditRebuild3')
    axisplanes=[('Right Plane',0),('Top Plane',1),('Front Plane',2)]
    parents={'mountX':comps['XY_Fixed_Base-1'],'mountY':comps['Intermediate_X_Slider-1'],
      'tabX':comps['Intermediate_X_Slider-1'],'tabY':inner,
      'servoX':comps['XY_Fixed_Base-1'],'servoY':comps['Intermediate_X_Slider-1'],
      'pinXHorn':comps[names['hornX']],'pinYHorn':comps[names['hornY']],
      'pinXSlider':comps[names['tabX']],'pinYSlider':comps[names['tabY']]}
    for key,parent in parents.items():
        child=comps[names[key]];a,x,y,z=poses[key]
        child.Transform2=transform(a,bp[0]+x,bp[1]+y,bp[2]+z)
        c(doc,'EditRebuild3')
        pt=list(parent.Transform2.ArrayData);ct=list(child.Transform2.ArrayData)
        pr=np.array(pt[:9]).reshape(3,3);cr=np.array(ct[:9]).reshape(3,3)
        delta=np.array(ct[9:12])-np.array(pt[9:12])
        for cn,ci in axisplanes:
            dots=pr@cr[ci];pi=int(np.argmax(np.abs(dots)));pn=axisplanes[pi][0]
            alignment=0 if dots[pi]>0 else 1;signed=float(delta@pr[pi]);distance=abs(signed)
            ents=[mappedplane(parent,pn),mappedplane(child,cn)]
            name=key+'_Rigid_'+cn.replace(' ','_')
            if distance<1e-8:mate(doc,0,name,ents,alignment)
            else:
                c(doc,'ClearSelection2',True)
                for ent in ents:entityselect(doc,ent)
                result=c(doc,'AddDistanceMate',alignment,False,distance,distance,distance,0,0,iref())
                assert result is not None,('rigid distance failed',name)
                result.Name=name
                newdelta=np.array(child.Transform2.ArrayData[9:12])-np.array(parent.Transform2.ArrayData[9:12])
                if abs(float(newdelta@pr[pi])-signed)>1e-6:
                    fd=c(result,'GetDefinition');fd.FlipDimension=not fd.FlipDimension
                    assert c(result,'ModifyDefinition',fd,doc,NULL)
                print('RIGID',name,flush=True)
    assert c(doc,'EditRebuild3')
    # Leave the temporary neutral drivers in place only until the validation sweep.
    s['neutral_axis_drivers']=True;Path(tempfile.gettempdir(),'CycloProp_servo_layout_state.json').write_text(json.dumps(s,indent=2))
    save(doc)

if __name__=='__main__':
    if sys.argv[1]=='parts':make_parts()
    elif sys.argv[1]=='reference':servo_reference()
    elif sys.argv[1]=='assemble':assemble()
    elif sys.argv[1]=='validate':validate()
    elif sys.argv[1]=='clearance_fix':clearance_fix()
    elif sys.argv[1]=='rigid_repair':rigid_repair()
