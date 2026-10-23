from cad import *

def housing(d):
    ring(d, 10, 8, -1, 1.5, 'D10_Pilot_And_M10x0p5_Thread_Envelope')
    ring(d, 10, 7.4, 1.5, 1.8, 'Outer_Race_Inner_Shoulder_ID7p4')
    ring(d, 14, 7.4, 1.5, 1.8, 'Inboard_G10_Retention_Flange_H0p3')
    ring(d, 14, 8, -1.6, -1, 'M14x0p5_Bearing_Cap_Boss')
    ring(d, 14, 9.6, -2.5, -1.6, 'Flanged_Race_Pocket_D9p6')

def cap(d):
    ring(d, 16, 8.2, -3, -2.5, 'Outer_Flange_Contact_Annulus_ID8p2')
    ring(d, 16, 14, -2.5, -1.3, 'M14x0p5_Internal_Thread_Envelope')

def bearing(d):
    ring(d, 8, 3, -2.5, 1.5, 'F693ZZ_External_Envelope_3x8x4')
    ring(d, 9.5, 3, -2.5, -1.6, 'Flange_9p5x0p9')

def shim(d):
    ring(d, 28, 14.05, 3, 3.65, 'Hub_Endplate_Axial_Clearance_Shim_H0p65')
    points = [(.011 * math.cos(math.pi / 4 + i * math.pi / 2), .011 * math.sin(math.pi / 4 + i * math.pi / 2), .00365) for i in range(4)]
    face_circles(d, 2, .00365, points, .0014)
    cut(d, 'Four_D2p8_PCD22', .00066)

def bolt(d):
    ring(d, 4.5, 0, 0, 2.5, 'ISO4762_M2p5_Head_Envelope')
    ring(d, 2.5, 0, -10, 0, 'M2p5x0p45x10_Thread_Major_Envelope')

app.CommandInProgress = True
try:
    make_part('RB_Blade_Bearing_Cartridge_PROTOTYPE',
              'Proposed7075-T6 bearing cartridge. Endplate outside datumZ0, insideZ1.5. D10 pilot0..1.5 intoD10.02 plate hole. '
              'Inboard flangeOD14 H0.3, M10x0.5 external retaining threadZ-1..0. '
              'F693ZZ seatD8 Z-1.6..1.5, flange pocketD9.6 Z-2.5..-1.6, inner shoulderID7.4. '
              'M14x0.5 cap bossZ-2.5..-1. Thread solids are major envelopes; grooves/chamfers and fits require drawings. '
              'Outer-race shoulder contact land, housing fit, G10 crushing, nut torque and oscillatory bearing life await release.',
              '7075-T6 (SN)', housing)
    make_part('RB_Blade_Cartridge_M10_Retaining_Nut_PROTOTYPE',
              'Custom round OD14 M10x0.5 x1mm retaining nut, major-hole envelopeD10. '
              'Clamps1.5mm G10 between nutZ-1..0 and cartridge flangeZ1.5..1.8. '
              'Thread strip/preload and anti-loosening validation required; spanner feature pending manufacturing definition.',
              '7075-T6 (SN)', lambda d: ring(d, 14, 10, -1, 0, 'M10x0p5_Thin_Retaining_Nut'))
    make_part('RB_Blade_Bearing_Outer_Cap_PROTOTYPE',
              'OD16 M14x0.5 bearing retaining cap. Annular faceID8.2 contacts only F693ZZ flangeOD9.5 atZ-2.5, '
              'clear of nominalOD8 bearing body/shields. Nominal0.3mm gap to M10nut accommodates bearing-width tolerance. '
              'Thread geometry is envelope; spanner feature, torque/locking, tolerances and actual outer-flange contact await release.',
              '7075-T6 (SN)', cap)
    make_part('RB_F693ZZ_3x8x4_FLANGE9p5x0p9_ENVELOPE',
              'Purchased bearing external envelope per retained SMB F693ZZ supplier drawing, 3x8x4 flange9.5x0.9. '
              'Source ratingsC55kgf C0 18kgf; not an oscillatory-duty approval. Internal rolling geometry omitted. '
              '4340 library is a steel density proxy, NOT actual52100 material or reliable bearing mass. '
              'Do not fabricate this annulus. Supplier contact lands, delivered clearance class/lubricant and fitted life require verification.',
              'AISI 4340 Steel, normalized', bearing)
    make_part('RB_Blade_Inner_Race_Spacer_OD4_ID3p05_H0p3',
              'Steel inner-race-only spacerOD4 ID3.05 H0.3 Z1.5..1.8. Keeps blade thrust off shield/outer shoulder. '
              'Actual supplier inner-race contact land and journal fit must be verified; ground faces parallel and deburred before release.',
              'AISI 4340 Steel, normalized', lambda d: ring(d, 4, 3.05, 1.5, 1.8, 'Inner_Race_Spacer_H0p3'))
    make_part('RB_Blade_Thrust_Film_OD4_ID3p05_H0p15',
              'PTFE film washerOD4 ID3.05 H0.15 Z1.8..1.95. Nominal blade/washer clearance0.2 each end '
              'after both endplates move outward0.65. PTFE grade, creep, wear and incoming thickness require qualification; '
              'library PTFE is only the provisional material basis.',
              'PTFE (general)', lambda d: ring(d, 4, 3.05, 1.8, 1.95, 'PTFE_Thrust_Film_H0p15'))
    make_part('RB_Hub_Endplate_Shim_H0p65_PROTOTYPE',
              '6061 annular hub shimOD28 ID14.05 H0.65, fourD2.8 PCD22 at45+90n. '
              'Moves each endplate outward0.65 while preserving shaft crosspin/hub/blade/arm stations. '
              'Remaining hub pilot engagement0.85; flatness/runout and bolted-stack tolerance require release.',
              '6061-T6 (SS)', shim)
    make_part('RB_M2p5x10_Hub_Screw_REFERENCE',
              'ISO4762 M2.5x0.45x10 nominal envelope, head4.5x2.5, thread major solid. '
              'Replaces8mm reference after0.65mm hub shim, nominal nut protrusion1.85mm. '
              '4340 density proxy only; availability, fastener grade, tolerances and locking not verified.',
              'AISI 4340 Steel, normalized', bolt)
finally:
    app.CommandInProgress = False
