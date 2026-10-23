"""Serial native CAD continuation. Explicit phases; never run historical mutation scripts."""
from pathlib import Path
import tempfile

exec((Path(tempfile.gettempdir()) / 'cycloprop_frame_hub_connections.py').read_text().rsplit('\nif __name__', 1)[0])

OUT = ROOT / 'CAD/Design_Completion'
LOG = OUT / 'COMPLETION_PROGRESS.json'


def c(o, name, *args):
    if name not in o._olerepr_.mapFuncs:
        o._FlagAsMethod(name)
    return getattr(o, name)(*args)


def progress(key, value):
    state = json.loads(LOG.read_text()) if LOG.exists() else {}
    state[key] = value
    LOG.write_text(json.dumps(state, indent=2))
    print(key, json.dumps(value), flush=True)


def ring(d, od, bore, z0, z1, name):
    sketch(d)
    circle(d, 0, 0, od / 2)
    if bore:
        circle(d, 0, 0, bore / 2)
    return extrude(d, z0, z1, name)


def make_part(name, description, build):
    path = OUT / (name + '.SLDPRT')
    if path.exists():
        print('EXISTING_PART', name, flush=True)
        return path
    d, path = newpart(name, description)
    build(d)
    finish(d, path)
    progress(name, {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'status': 'native geometry; not fabrication released'})
    return path


def frame_parts():
    def bottom(d):
        box(d, -110, -90, 110, 90, -8, -4, 'Outer_Frame_Rails', opening=(-100, -80, 100, 80))
        box(d, -5, -85, 5, 85, -8, -4, 'Centre_Spine')
        ring(d, 24, 0, -8, -4, 'Pedestal_Landing')
        for y in [-70, 70]:
            box(d, -28, y-4, 28, y+4, -8, -4, 'Fixed_Base_Landing_' + str(y))
        points = [(x/1000, y/1000, -.004) for x in [-105, 105] for y in [-85, 85]]
        points += [(x/1000, y/1000, -.004) for x in [-24, 24] for y in [-70, 70]]
        face_circles(d, 2, -.004, points, .0017)
        cut(d, 'Eight_M3_Clearance', .00401)
        points = [(8.3*math.cos(math.pi/6+i*2*math.pi/3)/1000,
                   8.3*math.sin(math.pi/6+i*2*math.pi/3)/1000, -.004) for i in range(3)]
        face_circles(d, 2, -.004, points, .0011)
        cut(d, 'Pedestal_Three_M2_Clearance', .00401)

    make_part('RevB_Cage_Lower_Frame_PROTOTYPE',
              '4mm lower frame Z-8..-4 relative fixed-base underside; outboard tube centres (+/-105,+/-85). '
              'Candidate 6061-T6; strength, tolerance and full actuator clearance require checks.', bottom)

    def top(d):
        box(d, -110, -90, 110, 90, 302, 306, 'Outer_Frame_Rails', opening=(-100, -80, 100, 80))
        box(d, -5, -85, 5, 85, 302, 306, 'Upper_Bearing_Spine')
        ring(d, 22, 11.4, 299.7, 306, 'Bearing_Upper_Shoulder')
        ring(d, 20, 13, 294.7, 299.71, 'Upper_686ZZ_Seat')
        # Open the spine through the bearing's centre, including above the shoulder.
        face_circles(d, 2, .306, [(0., 0., .306)], .0057)
        cut(d, 'Shaft_Clearance', .0063)
        face_circles(d, 2, .306, [(x/1000,y/1000,.306) for x in [-105,105] for y in [-85,85]], .0017)
        cut(d, 'Four_M3_Clearance', .00401)
        points=[(8.3*math.cos(math.pi/6+i*2*math.pi/3)/1000,8.3*math.sin(math.pi/6+i*2*math.pi/3)/1000,.2947) for i in range(3)]
        face_circles(d,2,.2947,points,.001)
        cut(d,'Upper_Cap_M2_Thread_Envelopes',.004)

    make_part('RevB_Cage_Upper_Support_PROTOTYPE',
              'Upper support underside Z302, upper bearing seat Z294.7..299.7; 3 M2x0.4 cap threads, '
              'CAD major envelopes D2. Candidate 6061-T6 machined part; loads and fit unreleased.', top)
    make_part('RevB_Cage_Tube_OD8_ID6_L306_PROTOTYPE',
              'OD8 ID6 L306 tube, four required between Z-4 and302. Candidate pultruded CFRP; '
              'end compression, buckling, material and vibration unverified.',
              lambda d: ring(d,8,6,0,306,'Tube'))
    make_part('RevB_Cage_TieRod_M3_L325_REFERENCE',
              'M3x0.5 threaded rod cut325, four required; geometry major-diameter envelope only. '
              'Nominal Z-13.5..311.5, washers and nuts at both ends. Grade/preload unreleased; mass penalty recorded.',
              lambda d:ring(d,3,0,0,325,'Thread_Envelope'))
    make_part('RevB_Base_Spacer_OD6_ID3p4_L4',
              'Four spacers between cage lower-frame top Z-4 and fixed-base underside Z0; material 6061-T6 proposed.',
              lambda d:ring(d,6,3.4,0,4,'Spacer'))

    def pedestal(d):
        ring(d,22,0,-4,0,'Mounting_Flange')
        ring(d,6,0,0,31.01,'Central_Post')
        ring(d,20,0,31,33,'Closed_Bottom')
        ring(d,20,11.4,33,41.5,'Shaft_And_Clip_Cavity')
        ring(d,20,13,41.5,46.5,'Lower_686ZZ_Seat')
        points=[(8.3*math.cos(math.pi/6+i*2*math.pi/3)/1000,8.3*math.sin(math.pi/6+i*2*math.pi/3)/1000,0.) for i in range(3)]
        face_circles(d,2,0.,points,.001)
        cut(d,'Base_M2_Thread_Envelopes',.00401)
        face_circles(d,2,.0465,[(x,y,.0465) for x,y,z in points],.001)
        cut(d,'Top_Cap_M2_Thread_Envelopes',.004)

    make_part('RevB_Lower_Bearing_Pedestal_PROTOTYPE',
              'Turned steel pedestal proposed: D6 column through carriage, OD20 lower-bearing head, '
              '686ZZ seat Z41.5..46.5 and TOP outer-race cap. Existing D20.5 moving bores give only0.37mm '
              'nominal clearance at e6.88; tolerance/deflection closure required before release.',pedestal)
    make_part('RevB_Lower_Bearing_Top_Cap_PROTOTYPE',
              'OD22 ID11.4 H1 top cap at Z46.5, 3xD2.2 on PCD16.6. Retains outer bearing race; '
              'contact land, shaft clip clearance and stiffness unreleased.',
              lambda d: cap(d))


def cap(d):
    sketch(d);circle(d,0,0,11);circle(d,0,0,5.7)
    for i in range(3):circle(d,8.3*math.cos(math.pi/6+i*2*math.pi/3),8.3*math.sin(math.pi/6+i*2*math.pi/3),1.1)
    extrude(d,0,1,'Cap')


def coupling_parts():
    def output(d):
        ring(d,92,40,0,4,'Output_Annulus')
        # Output tongues are along Y. The floating disk slides along Y on this member.
        for sgn in [-1,1]:box(d,-2,min(sgn*28,sgn*38),2,max(sgn*28,sgn*38),3.99,6,'Output_Tongue_'+str(sgn))
    make_part('RevB_Oldham_Output_CANDIDATE',
              'Candidate Oldham output annulus OD92 ID40 H4, Y tongues W4 L10 H2 at R28..38. '
              'Intended base Z39.5; output attachment and running fits not released. Not yet an implemented timing drive.',output)
    def disk(d):
        ring(d,92,40,0,4,'Floating_Disk')
        # Bottom Y slots and top X slots; slots intentionally open at inner and outer diameters.
        for axis,level,name in [(1,0.,'Bottom_Y_Slots'),(0,.004,'Top_X_Slots')]:
            activate(d)
            face=next(f for b in c(d,'GetBodies2',0,False) for f in c(b,'GetFaces') if c(c(f,'GetSurface'),'IsPlane') and abs(c(f,'GetBox')[2]-level)<1e-8 and abs(c(f,'GetBox')[5]-level)<1e-8)
            c(d,'ClearSelection2',True);assert c(face,'Select4',False,NULL);c(d.SketchManager,'InsertSketch',True);d.SketchManager.AddToDB=True
            # The symmetric rectangles are invariant to the face sketch's sign reversal.
            if axis==1:rect(d,-2.05,-47,2.05,47)
            else:rect(d,-47,-2.05,47,2.05)
            close_sketch(d);cut(d,name,.002)
    make_part('RevB_Oldham_Floating_Disk_CANDIDATE',
              'Candidate annular floating disk OD92 ID40 H4; orthogonal slots4.1wide2deep. '
              'Nominal0.1mm lateral tongue clearance admits angular backlash. Material/wear/friction/load unverified. '
              'Intended Z43.7..47.7; no full-cycle native test yet.',disk)
    def input_part(d):
        ring(d,92,24,0,4,'Input_Annulus')
        for sgn in [-1,1]:box(d,min(sgn*28,sgn*38),-2,max(sgn*28,sgn*38),2,-2,.01,'Input_Tongue_'+str(sgn))
        box(d,-22,-3,22,3,3.99,7,'Bridge_Above_Bearing_Cap')
        ring(d,14,6,4,12.1,'Shaft_Hub')
        face_circles(d,2,.0121,[(0.,0.,.0121)],.003)
        cut(d,'D6_Shaft_Bore',.00811)
    make_part('RevB_Oldham_Input_CANDIDATE',
              'Candidate input plate OD92 ID24 H4 with downward X tongues; raised bridge andD6hub. '
              'Intended base Z47.9, top60.0; positive shaft fastening not defined/implemented yet. '
              'Keep separate from working assembly until interfaces and clearances close.',input_part)


def main():
    app.CommandInProgress=True
    try:
        if sys.argv[1]=='frame-parts':frame_parts()
        elif sys.argv[1]=='coupling-parts':coupling_parts()
        else:raise ValueError('Unknown explicit phase')
    finally:
        app.CommandInProgress=False


if __name__=='__main__':main()
