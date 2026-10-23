"""Construct support/timing candidates; no verification campaign (user opt-out)."""
import cad
from cad import c
import json

F = cad.TASK / 'Bench_Prototype'
S = F / 'DETAIL_CANDIDATES.json'
record = json.loads(S.read_text()) if S.exists() else {'changes': {}}
recovery = F / 'Before_Detail_Candidates'
recovery.mkdir(exist_ok=True)
isolation = json.loads((F / 'ROTOR_ISOLATION.json').read_text())
assembly = cad.Path(isolation['assembly'])


def preserve(path):
    target = recovery / path.name
    if not target.exists():
        cad.shutil.copy2(path, target)
    return cad.getdoc(path)


def persist():
    S.write_text(json.dumps(record, indent=2))


cad.app.CommandInProgress = True
try:
    postpath = assembly.parent / 'BD_RB_Lower_Bearing_Pedestal_R2_PROTOTYPE.SLDPRT'
    post = preserve(postpath)
    for name, diameter, z0, z1 in [('Bench_D12_Root_To8p5',12,0,8.5),('Bench_D10_Mid_Collar_12p5_To17p5',10,12.5,17.5)]:
        if not c(post,'FeatureByName',name):
            cad.ring(post,diameter,0,z0,z1,name)
    cad.save(post)
    record['changes']['post']={'path':str(postpath),'sha256':cad.hashlib.sha256(postpath.read_bytes()).hexdigest(),
        'definition':'One-piece normalized4340 candidate: D12 stem rootZ0..8.5 and D10 collarZ12.5..17.5; retainD5.5 elsewhere/head/seat. Added native bosses represent machined one-piece stock, not bonded collars.',
        'holds':'Nominal adjacent plate Zgaps0.5mm; fillets must stay within these bands. Actual post free-body load, stress/fatigue and moving clearance not verified.'}
    persist()
    floatpath=assembly.parent/'BD_RB_Oldham_Floating_Disk_PROTOTYPE.SLDPRT'
    floating=preserve(floatpath)
    for axis in ['UpperX','LowerY']:
        for radial in [-1,1]:
            lo,hi=sorted([radial*24,radial*44])
            for side in [-1,1]:
                small,large=sorted([side*2.015,side*2.06])
                name='Bench_'+axis+'_W4p030_'+str(radial)+'_'+str(side)
                if not c(floating,'FeatureByName',name):
                    if axis=='UpperX':cad.box(floating,lo,small,hi,large,2,4,name)
                    else:cad.box(floating,small,lo,large,hi,0,2,name)
    cad.save(floating)
    record['changes']['timing']={'path':str(floatpath),'sha256':cad.hashlib.sha256(floatpath.read_bytes()).hexdigest(),
        'definition':'Active slide padsR24..44 nowW4.030 nominal; central relieved portions retain oldW4.1. Slot depth2 unchanged. Proposed finished padwidth4.030+/-0.005 against finishedtongue4.000+/-0.005; measure all four pads.',
        'pilot_fit':'Unchanged nominalD3/D3.02 CAD. Proposed selective finished pin3.000..3.003,pocket3.015..3.020: diametricgap0.012..0.020. These limits require manufacturing approval.',
        'holds':'POM thermal/creep/friction and surface treatment not qualified. No sliding, motion, backlash or collision tests run.'}
    persist()
    xp=F/'Actuation_Models/BA_X_Actuator_Drop_Link.SLDPRT'
    x=preserve(xp)
    if not c(x,'FeatureByName','Bench_X_Bore_Lower_Ligament'):
        cad.box(x,-26,24.5,-14,48.5,-75,-68.99,'Bench_X_Bore_Lower_Ligament')
        cad.modelplane_circles(x,'Right Plane',[(0,.0365,-.069)],.003175)
        cad.cut_both(x,'Bench_Complete_Quarter20_Major_Envelope')
    cad.save(x)
    ac=json.loads((F/'ACTUATION_LAYOUT.json').read_text())
    ac['parts']['BA_X_Actuator_Drop_Link']['sha256']=cad.hashlib.sha256(xp.read_bytes()).hexdigest()
    (F/'ACTUATION_LAYOUT.json').write_text(json.dumps(ac,indent=2))
    d=cad.getdoc(assembly,2)
    cad.activate(d)
    cad.save(d)
    layout=F/'BA_Bench_Actuation_Layout.SLDASM'
    ld=cad.getdoc(layout,2)
    cad.activate(ld)
    cad.save(ld)
    ac['assembly_sha256']=cad.hashlib.sha256(layout.read_bytes()).hexdigest()
    (F/'ACTUATION_LAYOUT.json').write_text(json.dumps(ac,indent=2))
    record.update(status='GEOMETRY CANDIDATES SAVED; TESTS NOT RUN AT USER REQUEST',
                  assembly=str(assembly),assembly_sha256=cad.hashlib.sha256(assembly.read_bytes()).hexdigest(),
                  verification='No final mate/rebuild-error inspection, motion, collision or physical test campaign performed. Construction/save operations only.',
                  release='HOLD')
    persist()
    print('DETAIL_CANDIDATES_SAVED',flush=True)
finally:
    cad.app.CommandInProgress=False
