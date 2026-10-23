from cad import *


def bottom(d):
    box(d, -110, -90, 110, 90, -8, -4, 'Lower_Perimeter', opening=(-100, -80, 100, 80))
    box(d, -5, -85, 5, 85, -8, -4, 'Centre_Spine')
    ring(d, 24, 0, -8, -4, 'Pedestal_Landing')
    for y in [-70, 70]:
        box(d, -28, y - 4, 28, y + 4, -8, -4, 'Base_Landing_' + str(y))
    points = [(x / 1000, y / 1000, -.004) for x in [-105, 105] for y in [-85, 85]]
    points += [(x / 1000, y / 1000, -.004) for x in [-24, 24] for y in [-70, 70]]
    face_circles(d, 2, -.004, points, .0017)
    cut(d, 'Eight_M3_Clearance', .00401)
    points = [(8.3 * math.cos(math.pi / 6 + i * 2 * math.pi / 3) / 1000,
               8.3 * math.sin(math.pi / 6 + i * 2 * math.pi / 3) / 1000, -.004) for i in range(3)]
    face_circles(d, 2, -.004, points, .0011)
    cut(d, 'Pedestal_Three_M2_Clearance', .00401)


def top(d):
    box(d, -110, -90, 110, 90, 304, 308, 'Upper_Perimeter', opening=(-100, -80, 100, 80))
    box(d, -5, -85, 5, 85, 304, 308, 'Bearing_Spine')
    ring(d, 22, 11.4, 299.9, 308, 'Upper_Outer_Race_Stop')
    ring(d, 20, 13, 294.5, 299.91, 'Floating_Outer_Race_Seat')
    face_circles(d, 2, .308, [(0., 0., .308)], .0057)
    cut(d, 'Shaft_Clip_Clearance', .00811)
    face_circles(d, 2, .308, [(x / 1000, y / 1000, .308) for x in [-105, 105] for y in [-85, 85]], .0017)
    cut(d, 'Four_Tie_Rod_Clearance', .00401)
    points = [(8.3 * math.cos(math.pi / 6 + i * 2 * math.pi / 3) / 1000,
               8.3 * math.sin(math.pi / 6 + i * 2 * math.pi / 3) / 1000, .2945) for i in range(3)]
    face_circles(d, 2, .2945, points, .001)
    cut(d, 'Three_M2_Top_Cap_Thread_Major_Envelopes', .0043)


def pedestal(d):
    ring(d, 22, 0, -4, 0, 'Mounting_Flange')
    ring(d, 5.5, 0, 0, 32.81, 'D5p5_Central_Post')
    ring(d, 20, 0, 32.8, 35, 'Closed_Floor_Below_Shaft_Nose')
    ring(d, 20, 11.4, 35, 41.5, 'Shaft_And_Clip_Clearance')
    ring(d, 20, 13, 41.5, 46.5, 'Lower_686ZZ_Seat')
    for z, depth, name in [(-.004, .0036, 'Base_Three_M2_Blind_Thread_Major_Envelopes'),
                            (.0465, .0043, 'Top_Cap_Three_M2_Blind_Thread_Major_Envelopes')]:
        points = [(8.3 * math.cos(math.pi / 6 + i * 2 * math.pi / 3) / 1000,
                   8.3 * math.sin(math.pi / 6 + i * 2 * math.pi / 3) / 1000, z) for i in range(3)]
        face_circles(d, 2, z, points, .001)
        cut(d, name, depth)


def cap(d):
    sketch(d)
    circle(d, 0, 0, 11.)
    circle(d, 0, 0, 5.7)
    for i in range(3):
        circle(d, 8.3 * math.cos(math.pi / 6 + i * 2 * math.pi / 3),
               8.3 * math.sin(math.pi / 6 + i * 2 * math.pi / 3), 1.1)
    extrude(d, 0, 1, 'Outer_Race_Cap')


app.CommandInProgress = True
try:
    make_part('RB_Cage_Lower_Frame_PROTOTYPE',
              'Lower cage Z-8..-4, tube centres(+/-105,+/-85), four base attachment centres(+/-24,+/-70). '
              '6061-T6 proposed. Native nominal geometry; actuator clearance, stiffness and preload not released.',
              '6061-T6 (SS)', bottom)
    make_part('RB_Cage_Upper_Support_PROTOTYPE',
              'Header Z304..308; upper bearing seat294.5..299.9 gives0.4mm nominal outer-race axial float '
              'around bearing294.7..299.7. D13H7 proposed; three M2x0.4 threads, D1.6 pilot depth5.1/full thread4.0. '
              'Actual bearing ring lands, load, thermal float, fits and tool access require validation.',
              '6061-T6 (SS)', top)
    make_part('RB_Cage_Tube_OD8_ID6_L308_PROTOTYPE',
              'Four OD8 ID6 L308 compression sleeves between Z-4 and304 with separate M3 tie rods. '
              '6061-T6 tube selected for first prototype, not CFRP. Compression/buckling/preload/vibration require checks.',
              '6061-T6 (SS)', lambda d: ring(d, 8, 6, 0, 308, 'Compression_Tube'))
    make_part('RB_Cage_TieRod_M3_L327_REFERENCE',
              'Four M3x0.5 threaded tie rods cut327 at Z-13.5..313.5. Washer/nut stacks defined separately. '
              'Library4340 assigned only as provisional steel density/strength proxy; procurement grade must be specified.',
              'AISI 4340 Steel, normalized', lambda d: ring(d, 3, 0, 0, 327, 'Thread_Major_Envelope'))
    make_part('RB_Base_Spacer_OD6_ID3p4_L4',
              'Four spacers from cage topZ-4 to base undersideZ0, OD6 ID3.4 L4. 6061-T6 proposed; preload/web checks pending.',
              '6061-T6 (SS)', lambda d: ring(d, 6, 3.4, 0, 4, 'Base_Spacer'))
    make_part('RB_Lower_Bearing_Pedestal_R2_PROTOTYPE',
              'Turned4340 normalized reference: flangeOD22 Z-4..0, solidD5.5stem toZ32.8, OD20head, '
              'shaft/clip bore11.4 from35..41.5, bearingD13H7 seat41.5..46.5 with integral bottom shoulder. '
              'D20.5 moving bores retain0.62mm nominal clearance at e6.88 before budgets. '
              'Three M2x0.4 base blind threads full3.0/pilot3.6; top threads full4.0/pilot5.1. '
              'CAD shows major diameter envelopes. Root fillets, approved loads, fatigue, fit and heat-treatment certification remain holds.',
              'AISI 4340 Steel, normalized', pedestal)
    make_part('RB_Lower_Bearing_Top_Cap_PROTOTYPE',
              'OD22 ID11.4 H1, threeD2.2 holesPCD16.6 at30/150/270deg, placedZ46.5. '
              'Outer-race-only cap; torque, ring contact lands, thread fit and cap bending need checks.',
              '6061-T6 (SS)', cap)
finally:
    app.CommandInProgress = False
