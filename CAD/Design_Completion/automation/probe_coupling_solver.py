from cad import *
d = getdoc(ASSEMBLY, 2)
activate(d)
hold = c(d, 'FeatureByName', 'RevB_SETUP_Rotor_Angle')
fd = c(hold, 'GetDefinition')
original_angle = fd.Angle
print('ORIGINAL_ANGLE', original_angle, flush=True)
st = json.loads((TASK / 'COUPLING_INTEGRATION_STATE.json').read_text())

def show(label):
    ro = roots(d)
    ringco = next(co for co in c(d, 'GetComponents', False) if logical(co.Name2).endswith('/4-Outer_Control_Ring-1'))
    row = {}
    for key, co in [('shaft', ro['3-Drive_Shaft-1']), ('ring', ringco), ('input', c(d, 'GetComponentByName', st['added']['Input'])),
                    ('blade', ro['Part1-1'])]:
        t = tf(co)
        row[key] = {'angle': math.degrees(math.atan2(t[1], t[0])), 'fixed': c(co, 'IsFixed')}
    print(label, json.dumps(row), flush=True)

app.CommandInProgress = True
try:
    show('BEFORE')
    fd.Angle = original_angle + math.radians(10)
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    assert c(d, 'ForceRebuild3', False)
    show('AFTER_ANGLE_DRIVE')
    print('MATE_ERRORS', errors([hold] + [c(d, 'FeatureByName', n) for n in st['mates']]), flush=True)
finally:
    fd = c(hold, 'GetDefinition')
    fd.Angle = original_angle
    assert c(hold, 'ModifyDefinition', fd, d, NULL)
    c(d, 'ForceRebuild3', False)
    save(d)
    app.CommandInProgress = False
