from cad import *

ANGLES = [math.pi / 8 + i * math.pi / 2 for i in range(4)]


def output(d):
    ring(d, 68, 40, 0, 4, 'Output_Plate')
    for sign in [-1, 1]:
        box(d, -2, min(sign * 28, sign * 38), 2, max(sign * 28, sign * 38), 3.99, 6,
            'Y_Tongue_' + str(sign))
    points = [(.030 * math.cos(a), .030 * math.sin(a), .004) for a in ANGLES]
    face_circles(d, 2, .004, points, .0011)
    cut(d, 'Four_M2_Clearance', .00401)
    face_circles(d, 2, .004, points, .0021)
    cut(d, 'Four_90deg_Countersinks_D4p2', .0011, True)
    face_circles(d, 2, 0., [(x, y, 0.) for x, y, z in points], .00151)
    cut(d, 'Four_Standoff_Pilot_Pockets_D3p02', .0011)


def floating(d):
    ring(d, 52, 40, 0, 4, 'Relieved_Floating_Ring')
    for sign in [-1, 1]:
        box(d, min(sign * 24, sign * 44), -4, max(sign * 24, sign * 44), 4, 0, 4,
            'X_Slide_Pad_' + str(sign))
        box(d, -4, min(sign * 24, sign * 44), 4, max(sign * 24, sign * 44), 0, 4,
            'Y_Slide_Pad_' + str(sign))
    face_rectangles(d, 0, [(-2.05, -45, 2.05, 45)], 'Lower_Y_Slots_W4p1_H2', 2.)
    face_rectangles(d, 4, [(-45, -2.05, 45, 2.05)], 'Upper_X_Slots_W4p1_H2', 2.)


def input_part(d):
    ring(d, 68, 24, 0, 4, 'Input_Plate')
    for sign in [-1, 1]:
        box(d, min(sign * 28, sign * 38), -2, max(sign * 28, sign * 38), 2, -2, .01,
            'Downward_X_Tongue_' + str(sign))
    box(d, -22, -3, 22, 3, 3.99, 7, 'Bridge_Above_Lower_Cap')
    ring(d, 14, 6, 4, 12.1, 'Shaft_Hub')
    face_circles(d, 2, .0121, [(0., 0., .0121)], .003)
    cut(d, 'D6_Shaft_Bore_Through_Bridge', .00811)
    modelplane_circles(d, 'Right Plane', [(0., 0., .0086)], .001)
    cut_both(d, 'DIN1481_D2_Crosspin_Hole')


def pilot_standoff(d):
    ring(d, 5, 2.2, 0, 9, 'Shoulder_Spacer_L9')
    ring(d, 3, 2.2, -1, 0, 'Lower_Torque_Pilot_D3')
    ring(d, 3, 2.2, 9, 10, 'Upper_Torque_Pilot_D3')


def countersunk_screw(d):
    activate(d)
    cone = c(c(app, 'GetModeler'), 'CreateBodyFromCone', array([0., 0., 0., 0., 0., -1., .002, .001, .001]))
    assert cone
    f = c(d, 'CreateFeatureFromBody3', cone, False, 1)
    assert f
    f.Name = '90deg_Head_D4_H1'
    ring(d, 2, 0, -18, -.999, 'M2x18_Overall_Length_Envelope')


app.CommandInProgress = True
try:
    make_part('RB_Oldham_Output_PROTOTYPE',
              'Output plateOD68 ID40 H4 atZ39.5; Y tonguesW4 L10 H2 onR28..38. Four mounting holesPCD60 at22.5+90n deg. '
              'M2x18 CSK head recessed0.1; D3.02x1.1 lower pilot pockets for shouldered torque spacers. '
              '7075-T6 proposed; hardcoat allowance, contact loads, edge radii and fits require release.',
              '7075-T6 (SN)', output)
    make_part('RB_Oldham_Floating_Disk_PROTOTYPE',
              'Relieved POM floating member ID40, centralOD52, four8wide pads toR44, H4. '
              'Underside Y/topside X slots4.1wide2deep. IntendedZ43.7..47.7; nominal face gaps0.2, '
              'tongue engagement1.8. Includes backlash; not zero-backlash. C0.15 mating tongue edges andR0.05MAX slot corners proposed. '
              'Wear, thermal fit, creep, friction, fatigue and2640RPM qualification remain holds.',
              'POM Acetal Copolymer', floating)
    make_part('RB_Oldham_Input_PROTOTYPE',
              'Input plateOD68 ID24 H4 atZ47.9; downward X tonguesW4 L10 H2. Raised bridge, OD14 D6hub '
              'toZ60.0. D2 crosspin atlocalZ8.6 (baseZ56.5) gives positive shaft torque and axial retention. '
              'Pin clock angle is set in shaft drill feature; manufacture using assembly datum. '
              '7075-T6 proposed; shaft crosshole fatigue, pin strength and assembly access require verification.',
              '7075-T6 (SN)', input_part)
    make_part('RB_Oldham_Output_Pilot_Standoff_L9',
              'Four shouldered steel torque spacers: bodyOD5 ID2.2 L9 with OD3 x1 pilots both ends. '
              'Ring/output pocketsD3.02 depth1.1 leave0.1 tip clearance, shoulders define9mm spacing. '
              'Pilot fit/backlash and screw preload require release; normalized4340 proposed.',
              'AISI 4340 Steel, normalized', pilot_standoff)
    make_part('RB_M2x18_Oldham_CSK_Screw_REFERENCE',
              'M2x0.4x18 countersunk overall-length envelope, 90deg headD4 H1, recessed0.1 in outputplate. '
              'Nominal4mm ring thread engagement and0.7mm bottom clearance. Purchased supplier form/grade/length tolerances pending. '
              '4340 library is only a steel reference, not grade certification; drive omitted.',
              'AISI 4340 Steel, normalized', countersunk_screw)
finally:
    app.CommandInProgress = False
