from cad import *
d = getdoc(ASSEMBLY, 2)
activate(d)
shaft = roots(d)['3-Drive_Shaft-1']
hold = c(d, 'FeatureByName', 'RevB_SETUP_Rotor_Angle')
fd = c(hold, 'GetDefinition')
original = {'angle': fd.Angle, 'flip': fd.FlipDimension, 'align': fd.MateAlignment}
plane = c(c(d, 'FeatureByName', 'Front Plane'), 'GetSpecificFeature2')
assert plane
print('ANGLE_BEFORE', original, 'REFERENCE', fd.ReferenceEntity, flush=True)
app.CommandInProgress = True
try:
    fd.ReferenceEntity = plane
    fd.Angle = math.radians(225.9223267454249)
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    assert c(d, 'ForceRebuild3', False)
    print('WITH_REFERENCE', math.degrees(math.atan2(tf(shaft)[1], tf(shaft)[0])), flush=True)
    fd = c(hold, 'GetDefinition')
    fd.FlipDimension = not fd.FlipDimension
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    assert c(d, 'ForceRebuild3', False)
    print('WITH_REFERENCE_FLIPPED', math.degrees(math.atan2(tf(shaft)[1], tf(shaft)[0])), flush=True)
finally:
    fd = c(hold, 'GetDefinition')
    fd.Angle = original['angle']
    fd.FlipDimension = original['flip']
    fd.MateAlignment = original['align']
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    assert c(d, 'ForceRebuild3', False)
    save(d)
    app.CommandInProgress = False
