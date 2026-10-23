from cad import *


def screw(d, diameter, length, head_d, head_h):
    ring(d, head_d, 0, -head_h, 0, 'Head_Envelope')
    ring(d, diameter, 0, 0, length, 'Thread_Major_Envelope')


app.CommandInProgress = True
try:
    for name, diameter, length, head_d, head_h in [
        ('RB_M3x16_Base_Screw_REFERENCE', 3., 16., 5.5, 3.),
        ('RB_M2x8_Pedestal_Screw_REFERENCE', 2., 8., 3.8, 2.),
        ('RB_M2x5_Bearing_Cap_Screw_REFERENCE', 2., 5., 3.8, 2.)]:
        make_part(name,
                  'Purchased ISO4762 dimensional reference M'+str(diameter)+'x'+str(length)+
                  '; solid head/thread major envelopes, drive and helical thread omitted. '
                  '4340 library is a provisional steel mass proxy, not a certified fastener grade. '
                  'Specify grade8.8 minimum, supplier tolerances and approved tightening/locking before procurement.',
                  'AISI 4340 Steel, normalized',
                  lambda d, dia=diameter, le=length, hd=head_d, hh=head_h: screw(d, dia, le, hd, hh))
finally:
    app.CommandInProgress = False
