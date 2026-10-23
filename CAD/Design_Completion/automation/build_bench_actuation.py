"""Build supplier envelopes and a separate, recoverable bench-actuation layout.

Construction/saving only. No motion, collision, proof or test campaign is run.
The layout is deliberately separate until its cross-slot and fixture interfaces
are closed; it must not be mistaken for an accepted actuator installation.
"""
import json
import math
from pathlib import Path
import cad
from cad import c, app, NULL, iref, array, pythoncom, np

FOLDER = cad.TASK / 'Bench_Prototype'
MODELS = FOLDER / 'Actuation_Models'
MODELS.mkdir(exist_ok=True)
STATE = FOLDER / 'ACTUATION_LAYOUT.json'
cad.OUT = MODELS


def make(name, description, callback, material='6061-T6 (SS)'):
    path = MODELS / (name + '.SLDPRT')
    record = json.loads(STATE.read_text()) if STATE.exists() else {'parts': {}, 'added': {}}
    if path.exists():
        if name not in record['parts']:
            raise RuntimeError('Preserve and inspect unrecorded partial part: ' + str(path))
        return path
    doc, _ = cad.newpart(name, description)
    callback(doc)
    c(doc, 'SetMaterialPropertyName2', 'Default', cad.MAT_DB, material)
    c(doc.Extension.CustomPropertyManager(''), 'Add3', 'DESIGN_STATUS', 30,
      'DEVELOPMENT LAYOUT; INTERFACES AND TESTS NOT RELEASED', 2)
    cad.save(doc, path)
    record['parts'][name] = {'path': str(path), 'description': description,
                              'sha256': cad.hashlib.sha256(path.read_bytes()).hexdigest()}
    STATE.write_text(json.dumps(record, indent=2))
    print('SAVED_ACTUATION_PART', name, flush=True)
    return path


def actuator(doc):
    cad.box(doc, -28.2, -28.2, 28.2, 28.2, -45.2, 0, 'NA23_Motor_Envelope',
            holes=[(x, y, 2.6) for x in [-23.55, 23.55] for y in [-23.55, 23.55]])
    cad.ring(doc, 28, 0, -110.7, -45.2, 'Rear_Barrel_Envelope')
    cad.ring(doc, 28, 10.2, 0, 74.5, 'Fixed_Front_Barrel_Envelope')


def rod(doc):
    cad.ring(doc, 10, 0, 44.5, 104.5, 'Rod_At_Midstroke_30mm')
    cad.ring(doc, 6.35, 0, 104.5, 126.7, 'Quarter20_Thread_Major_Envelope')


def bracket(doc):
    holes = [(0, 0, 20)] + [(x, y, 2.75) for x in [-23.55, 23.55] for y in [-23.55, 23.55]]
    cad.box(doc, -40, -50, 40, 35, 0, 8, 'Front_Plate', holes=holes)
    cad.box(doc, -40, -50, 40, -42, -20, 50, 'Bench_Foot')
    cad.modelplane_circles(doc, 'Top Plane', [(x/1000, 0, z/1000) for x in [-28,28] for z in [-10,38]], .0033)
    cad.cut_both(doc, 'Four_M6_Foot_Clearances')


def xlink(doc):
    cad.box(doc, -30, 24.5, -10, 34, -5, 0, 'Five_mm_Attachment_Foot', holes=[(-27,28,1.7),(-13,28,1.7)])
    cad.box(doc, -26, 24.5, -14, 48.5, -75, -1.5, 'Deep_Actuator_Web')
    cad.modelplane_circles(doc, 'Right Plane', [(0,.0365,-.069)], .003175)
    cad.cut_both(doc, 'Quarter20_Axial_Thread_Major_Envelope')


def ylink(doc):
    cad.box(doc, -44, -26, -30, -14, -6, 0, 'Outboard_Foot', holes=[(-35,-23,1.7),(-35,-17,1.7)])
    cad.box(doc, -44, -26, -32, -14, -71, -1.5, 'Drop_Web')
    cad.box(doc, -58, -32, -18, -8, -85, -71, 'Cross_Slot_Block')
    # Through-X rectangular slot: Y width19.02, Z height8, opened from side.
    cad.activate(doc)
    c(doc, 'ClearSelection2', True)
    c(doc.Extension, 'SelectByID2', 'Right Plane','PLANE',0.,0.,0.,False,0,NULL,0)
    c(doc.SketchManager, 'InsertSketch', True)
    doc.SketchManager.AddToDB = True
    tr = list(doc.SketchManager.ActiveSketch.ModelToSketchTransform.ArrayData)
    pts = [np.array([0,y,z])/1000 @ np.array(tr[:9]).reshape(3,3)+np.array(tr[9:12])
           for y,z in [(-29.51,-82),(-10.49,-82),(-10.49,-74),(-29.51,-74)]]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        c(doc.SketchManager,'CreateLine',float(a[0]),float(a[1]),0.,float(b[0]),float(b[1]),0.)
    cad.close_sketch(doc)
    cad.cut_both(doc, 'X_Floating_Y_Driven_Slot')


def head(doc):
    cad.box(doc, -22,-12,22,12,0,12,'Crosshead_Base')
    cad.box(doc,-4,-12,4,12,12,23,'Shoe_Upriser')
    cad.box(doc,-8,-28,8,0,12,20,'Adapter_Bridge')
    cad.box(doc,-8,-28,8,-12,20,32,'Threaded_Rod_Adapter')
    cad.modelplane_circles(doc,'Top Plane',[(-.014,0,.006),(.014,0,.006)],.005)
    cad.cut_both(doc,'Two_Bronze_Bush_Housings')
    cad.modelplane_circles(doc,'Top Plane',[(0,0,.026)],.003175)
    cad.cut_both(doc,'Quarter20_Adapter_Major_Envelope')


def shoe(doc):
    cad.box(doc,-4,-9.5,4,9.5,0,6,'Bronze_Shoe',holes=[(0,0,2.25)])
    cad.face_circles(doc,2,.006,[(0.,0.,.006)],.00375)
    cad.cut(doc,'M4_Head_Counterbore',.0042)


def post(doc):
    cad.box(doc,-8,-8,8,8,0,38,'Shaft_Support')
    cad.modelplane_circles(doc,'Top Plane',[(0,0,.030)],.004)
    cad.cut_both(doc,'D8_Guide_Shaft_Seat')
    cad.face_circles(doc,2,0,[(0.,0.,0.)],.0025)
    cad.cut(doc,'M5_Bottom_Thread_Major_Envelope',.008)


def main():
    app.CommandInProgress = True
    try:
        make('BA_NA23C60_T4A_CASE_REFERENCE','Zaber NA23C60-T4A supplier dimensional envelope. Stroke60,body56.4,mountpitch47.1,D5.2 through,L nominal208.4. Drawing-chain207.4 discrepancy1mm and pilot/connector details HOLD. Envelope is not supplier CAD or hardware mass.',actuator)
        make('BA_NA23C60_T4A_ROD_REFERENCE','Midstroke30; D10x60 rod plus1/4-20x22.2 major envelope. Exact extension datum and permissible side load require OEM confirmation.',rod,'AISI 4340 Steel, normalized')
        make('BA_NEMA23_Bench_Bracket','6061 plate8,foot8;40mm clearance bore,47.1 square mount patternD5.5; fourM6foot holes. Bent/welded/machined process and stiffness not released.',bracket)
        make('BA_X_Actuator_Drop_Link','Separate replacement candidate for original Xtab: foot5,primaryM3at(-27,28),(-13,28);12x24deepweb. Female1/4-20 thread major CAD. Original footprint must be reconciled before installation.',xlink,'7075-T6 (SN)')
        make('BA_Y_Cross_Slot_Drop_Link','Replacement Ytab candidate: outboardfoot6,2M3at(-35,-23/-17),12x12web;40mmXslot,19.02Yfinishedwidth,8Zheight. Matching carriage ear and rail/fastener clearance required.',ylink,'7075-T6 (SN)')
        make('BA_Y_Guided_Crosshead','Twin D10 bush housings on28mmXcentres,12mm base,shoe upriser and1/4-20 adapter. Thread/bush retention/guide alignment not released.',head,'7075-T6 (SN)')
        make('BA_Y_Bronze_Sliding_Shoe','Bronze shoe8x19x6 withD4.5through andD7.5x4.2counterbore. Material grade/finish/lubrication HOLD; generic bronze density only.',shoe,'Bronze')
        make('BA_D8_Guide_Shaft_L126','Ground steelD8x126; proposedh6,hardness/straightness/finish require supplier selection. No friction/life claim.',lambda d:cad.ring(d,8,0,0,126,'Guide_Shaft'),'AISI 4340 Steel, normalized')
        make('BA_Guide_Support_Post','16squarex38,shaftaxis30abovebottom,D8throughY,M5bottom8deep. Positive axial shaft collars and clamp screws required, not yet installed.',post)
        make('BA_Bronze_Bush_10_8_L15','BushOD10ID8.02L15, proposed press fit/line ream; actual bronze grade,fit and retention HOLD.',lambda d:cad.ring(d,10,8.02,0,15,'Sleeve'),'Bronze')
        make('BA_Bench_Plate_650_12','650squarex12 plate; fixture mounting hole coordinates not released. Secure to a rigid bench before any use.',lambda d:cad.box(d,-325,-325,325,325,0,12,'Bench_Plate'))
        def column(d):
            cad.ring(d,16,6.6,0,102,'Frame_Bench_Column')
            cad.face_circles(d,2,.102,[(0.,0.,.102)],.006)
            cad.cut(d,'Upper_Nut_Clearance_Pocket',.008)
        make('BA_Frame_Bench_Column_L102','OD16ID6.6L102 withD12x8topcounterbore to clear original frame lower nut. Extended one-piece tie rods and bench fastening remain required.',column)
        state=json.loads(STATE.read_text())
        isolation=json.loads((FOLDER/'ROTOR_ISOLATION.json').read_text())
        rotor=Path(isolation['assembly'])
        layout=FOLDER/'BA_Bench_Actuation_Layout.SLDASM'
        if layout.exists():
            d=cad.getdoc(layout,2)
        else:
            template=c(app,'GetUserPreferenceStringValue',9)
            d=c(app,'NewDocument',template,0,0.,0.)
            cad.save(d,layout)
        cad.activate(d)
        # Uses the source rotor's original global datum; keep the rotor rigid in
        # this separate layout. Its internal kinematics remain in the rotor file.
        inspect=json.loads((FOLDER/'ACTUATION_START_INSPECTION.json').read_text())
        xp=next(r for r in inspect if 'X_Slider_Drive_Tab_' in r['name'])['pos_mm']
        yp=next(r for r in inspect if 'Y_Carriage_Drive_Tab_' in r['name'])['pos_mm']
        rd=cad.getdoc(rotor,2)
        bc=c(rd,'GetComponentByName','BD_RB_XY_Fixed_Base-1')
        origin=np.array(cad.tf(bc)[9:12])
        cad.activate(d)
        state['assembly']=str(layout)
        state['source_rotor']=str(rotor)
        def insert(key,file,point,R=None):
            if key in state['added']:return
            path=rotor if file=='ROTOR' else MODELS/(file+'.SLDPRT')
            cad.getdoc(path,2 if file=='ROTOR' else 1)
            cad.activate(d)
            pos=np.zeros(3) if file=='ROTOR' else origin+np.array(point)/1000
            co=c(d,'AddComponent5',str(path),0,'',False,'',*map(float,pos))
            if not co:raise RuntimeError(('Insertion failed',key))
            cad.set_transform(co,pos,np.eye(3) if R is None else np.array(R))
            c(d,'ClearSelection2',True)
            c(co,'Select4',False,NULL,False)
            c(d,'FixComponent')
            state['added'][key]=co.Name2
            STATE.write_text(json.dumps(state,indent=2))
            print('LAYOUT_COMPONENT',key,flush=True)
        RX=[[0,1,0],[0,0,1],[1,0,0]]
        RY=[[-1,0,0],[0,0,1],[0,1,0]]
        insert('Rotor','ROTOR',[0,0,0])
        insert('Bench','BA_Bench_Plate_650_12',[0,0,-122])
        for i,(x,y) in enumerate([(x,y) for x in [-105,105] for y in [-85,85]]):
            insert('FrameColumn'+str(i),'BA_Frame_Bench_Column_L102',[x,y,-110])
        for axis,R,pt in [('X',RX,[-140.7+xp[0],36.5,-60]),('Y',RY,[-38,-162.7+yp[1],-60])]:
            insert(axis+'Case','BA_NA23C60_T4A_CASE_REFERENCE',pt,R)
            insert(axis+'Rod','BA_NA23C60_T4A_ROD_REFERENCE',pt,R)
            insert(axis+'Bracket','BA_NEMA23_Bench_Bracket',pt,R)
        insert('XDrop','BA_X_Actuator_Drop_Link',xp)
        insert('YDrop','BA_Y_Cross_Slot_Drop_Link',yp)
        insert('YHead','BA_Y_Guided_Crosshead',[-38,-20+yp[1],-86])
        insert('YShoe','BA_Y_Bronze_Sliding_Shoe',[-38,-20+yp[1],-63])
        shaftR=[[1,0,0],[0,0,-1],[0,1,0]]
        for i,x in enumerate([-52,-24]):
            insert('YGuideShaft'+str(i),'BA_D8_Guide_Shaft_L126',[x,-88,-80],shaftR)
            insert('YBush'+str(i),'BA_Bronze_Bush_10_8_L15',[x,-27.5+yp[1],-80],shaftR)
            for j,y in enumerate([-70,20]):
                insert('YGuideSupport'+str(i)+str(j),'BA_Guide_Support_Post',[x,y,-110])
        cad.save(d)
        state.update(status='SEPARATE STATIC DEVELOPMENT LAYOUT; NOT INSTALLED OR MOTION VERIFIED',
                     tests='NOT RUN: user requested no further tests',
                     legacy_servo='Original inadequate servos remain in rotor reference; proposed replacements are shown separately and overlap old tabs. They must be removed during final integration.',
                     holds=['Replace rotor X/Y tabs and strengthen their moving-plate attachments; do not stack new links over old tabs.',
                            'Install physical X-floating/Y-driving cross-slot constraint and external Yguide; supplier actuator side-load capacity is not assumed.',
                            'Finish bench holes, extended tie rods, all mounting fasteners, shaft collars, bush retention and thread runouts.',
                            'Confirm OEM extension datum, body stack1mm discrepancy, connectors and flange mounting hardware.',
                            'Motion, clearance, material, stiffness, thermal, holding duty and physical tests not performed.'])
        state['assembly_sha256']=cad.hashlib.sha256(layout.read_bytes()).hexdigest()
        STATE.write_text(json.dumps(state,indent=2))
        print('ACTUATION_LAYOUT_SAVED',layout,flush=True)
    finally:
        app.CommandInProgress=False


if __name__=='__main__':main()
