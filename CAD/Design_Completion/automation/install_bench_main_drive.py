"""Supplier-backed main-drive layout in the isolated rotor, with explicit interface holds."""
import cad
from cad import c, app, NULL, iref, array, pythoncom
from pathlib import Path
import json
import math

FOLDER = cad.TASK / 'Bench_Prototype'
STATE = FOLDER / 'MAIN_DRIVE_LAYOUT.json'
MODELS = FOLDER / 'Hardware_Models'
MODELS.mkdir(exist_ok=True)
cad.OUT = MODELS
cad.BUILD_LOG = MODELS / 'PARTS.json'


def screw(doc, dia, length, head_d, head_h):
    cad.ring(doc, head_d, 0, -head_h, 0, 'Head_Envelope')
    cad.ring(doc, dia, 0, 0, length, 'Thread_Major_Envelope')


def nut(doc, dia, af, height):
    cad.sketch(doc)
    radius = af / math.sqrt(3)
    cad.polygon(doc, [(radius*math.cos(i*math.pi/3), radius*math.sin(i*math.pi/3)) for i in range(6)])
    cad.circle(doc, 0, 0, dia/2)
    cad.extrude(doc, 0, height, 'Nut_Thread_Major_Envelope')


def case(doc):
    cad.box(doc, -37.25, -30.25, 37.25, 30.25, 0, 108.9, 'Conservative_Manufacturer_Case_Envelope', holes=[(0, 0, 7.1)])
    cad.ring(doc, 50, 14.2, -2, 0, 'D50_Pilot_Envelope')


def coupling(doc):
    cad.ring(doc, 34, 6, 0, 17, 'D6_Clamp_Hub_Envelope')
    cad.ring(doc, 34, 14, 17, 38.4, 'D14_Hub_And_Disc_Envelope')


def beam(doc):
    cad.box(doc, -110, -6, 110, 6, 0, 6, 'Header_Crossbeam',
            holes=[(-105, 0, 1.7), (105, 0, 1.7), (-42, 0, 3.3), (42, 0, 3.3)])


def plate(doc):
    points = [(x, y, 3.3) for x in [-42, 42] for y in [-36, 36]]
    p = 35 / math.sqrt(2)
    points += [(x, y, 2.75) for x in [-p, p] for y in [-p, p]]
    cad.box(doc, -50, -50, 50, 50, 0, 8, 'Motor_Adapter_Plate', holes=[(0, 0, 25.05), *points])


def guard(doc):
    cad.ring(doc, 90, 14, 0, 2, 'Guard_Flange')
    cad.ring(doc, 60, 56, 2, 52, 'Coupling_Contact_Cover')
    cad.face_circles(doc, 2, 0, [(x/1000, y/1000, 0.) for x in [-20, 20] for y in [-36, 36]], .0017)
    cad.cut(doc, 'Four_M3_Guard_Fixing_Holes', .00201)


def build():
    definitions = [
        ('BD_IDS_C60AP_400W_CASE_ENVELOPE', 'Supplier IDS-C60AP-48V400W:48V,1.27Nm rated,3000rpm rated,case108.9 long,shaft14x30,pilot50. Conservative74.5x60.5 case; connector/ear/hole details require OEM CAD. No hardware mass inferred.', '6061-T6 (SS)', case),
        ('BD_IDS_OUTPUT_SHAFT_D14_REFERENCE', 'Rotating D14x30 output envelope separate from fixed motor case; attach to main rotor for geometric motion only. OEM rotor, key and internal bearing details omitted.', 'AISI 4340 Steel, normalized', lambda d: cad.ring(d, 14, 0, 0, 30, 'Motor_Rotor_Output_Envelope')),
        ('BD_MP3438_6_14_COUPLER_ENVELOPE', 'Supplier MP3438 ordered6/14:OD34 L38.4,4Nm rated,10000rpm. Clamp/disc envelope only. Actual hub penetration, key clearance, clamp screw shape and1.5Nm seating torque must follow supplied drawing.', '6061-T6 (SS)', coupling),
        ('BD_Motor_Header_Crossbeam', '6061-T6 bar220x12x6; M3 clear atx+/-105; M6 clear atx+/-42. Two atbaseY+/-36; mounting pads/loaded alignment require inspection.', '6061-T6 (SS)', beam),
        ('BD_Motor_Adapter_Plate', '6061-T6 plate100x100x8; bore50.10; fourD5.5 PCD70 at45+90n; supportD6.6 at(+/-42,+/-36). Motor screw/nut stack not released without OEM flange/ear detail.', '6061-T6 (SS)', plate),
        ('BD_Motor_Standoff_OD12_ID6p4_L58', 'Four6061-T6 spacersOD12 ID6.4 L58 between crossbeamtop314 and platelower372. One-piece spacers; torque/clamp fatigue and alignment require checks.', '6061-T6 (SS)', lambda d: cad.ring(d, 12, 6.4, 0, 58, 'Spacer')),
        ('BD_M6x90_ISO4762_REFERENCE', 'Purchased M6x1x90 grade8.8 minimum; headD10 H6; envelope omits drive/thread. Verify supplier thread runout and nut engagement.', 'AISI 4340 Steel, normalized', lambda d: screw(d, 6, 90, 10, 6)),
        ('BD_M6_Nut_AF10_H5_REFERENCE', 'M6x1 grade8 nut AF10 H5 nominal; thread envelope; actual locking/torque process remains release item.', 'AISI 4340 Steel, normalized', lambda d: nut(d, 6, 10, 5)),
        ('BD_M6_Washer_6p4x12x1p6_REFERENCE', 'M6 washer6.4x12x1.6 supplier reference, hardness/finish pending.', 'AISI 4340 Steel, normalized', lambda d: cad.ring(d, 12, 6.4, 0, 1.6, 'Washer')),
        ('BD_M3x16_REFERENCE', 'M3x0.5x16 grade8.8; head5.5x3. Standard reference, not hardware mass or drive geometry.', 'AISI 4340 Steel, normalized', lambda d: screw(d, 3, 16, 5.5, 3)),
        ('BD_Coupling_Contact_Guard', 'Steel coverOD60 ID56 H50 withOD90 H2 flange and fourD3.4 at(+/-20,+/-36). Contact cover only; no fragment containment certification.', 'AISI 4340 Steel, normalized', guard),
        ('BD_Guard_Spacer_OD6_ID3p4_L4', 'Four6061 spacers4mm; guard flange318 supported from crossbeamtop314.', '6061-T6 (SS)', lambda d: cad.ring(d, 6, 3.4, 0, 4, 'Spacer')),
    ]
    for name, description, material, callback in definitions:
        cad.make_part(name, description, material, callback)


def main():
    app.CommandInProgress = True
    try:
        build()
        isolation = json.loads((FOLDER / 'ROTOR_ISOLATION.json').read_text())
        assembly = Path(isolation['assembly'])
        d = cad.getdoc(assembly, 2)
        cad.activate(d)
        root = c(d, 'GetComponents', True)
        base = next(co for co in root if Path(c(co, 'GetPathName')).name == 'BD_RB_XY_Fixed_Base.SLDPRT')
        shaft = next(co for co in root if Path(c(co, 'GetPathName')).name == 'BD_RB_3-Drive_Shaft.SLDPRT')
        header = next(co for co in root if Path(c(co, 'GetPathName')).name == 'BD_RB_Cage_Upper_Support_PROTOTYPE.SLDPRT')
        origin = cad.np.array(cad.tf(base)[9:12])
        state = json.loads(STATE.read_text()) if STATE.exists() else {'added': {}, 'assembly': str(assembly), 'status': 'IN PROGRESS'}
        if not (FOLDER / 'Before_Main_Drive.SLDASM').exists():
            assert c(d.Extension, 'SaveAs', str(FOLDER / 'Before_Main_Drive.SLDASM'), 0, 3, NULL, iref(), iref())
        sp = c(shaft, 'GetModelDoc2')
        if not c(sp, 'FeatureByName', 'Bench_OnePiece_Shaft_End_To315'):
            cad.shutil.copy2(Path(c(sp, 'GetPathName')), FOLDER / 'Before_Main_Drive_Shaft.SLDPRT')
            cad.sketch(sp)
            cad.circle(sp, 0, 0, 3)
            cad.extrude(sp, 275, 315, 'Bench_OnePiece_Shaft_End_To315')
            cad.save(sp)
        hp = c(header, 'GetModelDoc2')
        if not c(hp, 'FeatureByName', 'Bench_Motor_Crossbeam_Four_D3p4'):
            cad.shutil.copy2(Path(c(hp, 'GetPathName')), FOLDER / 'Before_Main_Drive_Header.SLDPRT')
            cad.face_circles(hp, 2, .308, [(x/1000, y/1000, .308) for x in [-105,105] for y in [-36,36]], .0017)
            cad.cut(hp, 'Bench_Motor_Crossbeam_Four_D3p4', .00401)
            cad.save(hp)

        def insert(key, file, point, moving=False, flip=False):
            if key in state['added']:
                return
            path = MODELS / (file + '.SLDPRT')
            if not path.exists():
                path = assembly.parent / (file + '.SLDPRT')
            assert path.exists(), path
            cad.getdoc(path)
            cad.activate(d)
            co = c(d, 'AddComponent5', str(path), 0, '', False, '', *map(float, origin + cad.np.array(point)/1000))
            assert co
            cad.set_transform(co, origin + cad.np.array(point)/1000, cad.np.diag([1,-1,-1]) if flip else cad.np.eye(3))
            cad.lock(d, shaft if moving else base, co, 'Bench_Drive_' + key)
            state['added'][key] = co.Name2
            STATE.write_text(json.dumps(state, indent=2))
        insert('MotorCase', 'BD_IDS_C60AP_400W_CASE_ENVELOPE', [0,0,380])
        insert('MotorOutput', 'BD_IDS_OUTPUT_SHAFT_D14_REFERENCE', [0,0,350], True)
        insert('Coupler', 'BD_MP3438_6_14_COUPLER_ENVELOPE', [0,0,330.8], True)
        insert('Plate', 'BD_Motor_Adapter_Plate', [0,0,372])
        for i, y in enumerate([-36,36]):
            insert('Beam'+str(i), 'BD_Motor_Header_Crossbeam', [0,y,308])
            for j, x in enumerate([-105,105]):
                key = str(i)+str(j)
                insert('BeamBolt'+key,'BD_M3x16_REFERENCE',[x,y,304])
                insert('BeamWasher'+key,'BD_RB_M3_Washer_REFERENCE',[x,y,314])
                insert('BeamNut'+key,'BD_RB_M3_Nut_REFERENCE',[x,y,314.5])
            for j, x in enumerate([-42,42]):
                key=str(i)+str(j)
                insert('Post'+key,'BD_Motor_Standoff_OD12_ID6p4_L58',[x,y,314])
                insert('PostBolt'+key,'BD_M6x90_ISO4762_REFERENCE',[x,y,308])
                insert('PostWasher'+key,'BD_M6_Washer_6p4x12x1p6_REFERENCE',[x,y,380])
                insert('PostNut'+key,'BD_M6_Nut_AF10_H5_REFERENCE',[x,y,381.6])
        insert('Guard','BD_Coupling_Contact_Guard',[0,0,318])
        for i, (x,y) in enumerate([(x,y) for x in [-20,20] for y in [-36,36]]):
            key=str(i)
            insert('GuardPost'+key,'BD_Guard_Spacer_OD6_ID3p4_L4',[x,y,314])
            insert('GuardBolt'+key,'BD_M3x16_REFERENCE',[x,y,320],flip=True)
            insert('GuardWasher'+key,'BD_RB_M3_Washer_REFERENCE',[x,y,307.5])
            insert('GuardNut'+key,'BD_RB_M3_Nut_REFERENCE',[x,y,305.1])
        assert c(d, 'ForceRebuild3', False)
        state['mate_errors'] = cad.errors(cad.active_mates(d))
        state['supplier_sources'] = {
            'motor': 'https://www.omc-stepperonline.com/ids-series-400w-canopen-rs485-pulse-integrated-dc-servo-motor-1-27nm-179-85oz-in-17-bit-absolute-encoder-ids-c60ap-48v400w',
            'coupling': 'https://www.omc-stepperonline.com/6mm-16mm-optional-bore-flexible-double-disc-coupling-34x38mm-shaft-coupler-mp3438-xx-xx'}
        state['shaft'] = {'manufacture': 'One-piece4340 normalized proposal; solid localZ2..315,overall313mm, D6; retain all old grooves/crossholes. Added CAD cylinder is not a welded extension.',
                          'baseline_preserved': 'CalculationD6x260 and14.8V unchanged; this is a separate48V bench drive.'}
        state['nominal_interfaces'] = {'coupler_bottom_mm':330.8,'coupler_top_mm':369.2,'shaft_end_mm':346.575,
                                        'motor_shaft_tip_mm':350,'motor_face_mm':380,
                                        'shaft_tip_separation_mm':3.425,'lower_hub_engagement_mm':15.775,
                                        'upper_hub_engagement_mm':19.2,'guard_radial_coupler_gap_mm':11}
        state['holds'] = ['Exact OEM case/ear/connector CAD and motor mounting bolt/nut stack; fasteners at motor ears not installed or released.',
                          'Coupling penetration/actual clamp hardware and shaft grip; alignment/runout must follow supplier drawing.',
                          'Header/motor-mount load/fastener tolerance and vibration checks; contact cover is not fragment containment.',
                          'Motor torque-speed/regen/current-control commissioning and independent overspeed/coast-stop interface.',
                          'External actuator installation, final moving-clearance campaign and physical proof remain outstanding.']
        state['status'] = 'MAIN DRIVE DEVELOPMENT LAYOUT INSTALLED; OEM FASTENING/VERIFICATION HOLDS REMAIN'
        cad.save(d)
        state['assembly_sha256'] = cad.hashlib.sha256(assembly.read_bytes()).hexdigest()
        STATE.write_text(json.dumps(state, indent=2))
        print('MAIN_DRIVE_LAYOUT', len(state['added']), 'components; mate errors', state['mate_errors'], flush=True)
    finally:
        app.CommandInProgress = False


if __name__ == '__main__':
    main()
