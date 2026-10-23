from cad import *
d = getdoc(ASSEMBLY, 2)
activate(d)
stpath = TASK / 'COUPLING_INTEGRATION_STATE.json'
s = json.loads(stpath.read_text())
old = c(d, 'FeatureByName', 'RevB_Oldham_Input_D6_Bore_D2_Crosspin')
ringhold = c(d, 'FeatureByName', 'RevB_SETUP_Ring_Angle')
app.CommandInProgress = True
try:
    assert c(old, 'SetSuppression2', 0, 1, None)
    assert c(ringhold, 'SetSuppression2', 1, 1, None)
    assert c(d, 'ForceRebuild3', False)
    ro = roots(d)
    shaft = ro['3-Drive_Shaft-1']
    driver = c(d, 'GetComponentByName', s['added']['Input'])
    st, it = tf(shaft), tf(driver)
    phase = (math.atan2(it[1], it[0]) - math.atan2(st[1], st[0])) % (2 * math.pi)
    print('RESTORED_INPUT_PHASE', math.degrees(phase), flush=True)
    assert abs(math.degrees(phase) - 164.17461441081947) < .001
    c(d, 'ClearSelection2', True)
    assert c(old, 'Select2', False, 0)
    assert c(d.Extension, 'DeleteSelection2', 0)
    lock(d, shaft, driver, 'RevB_Oldham_Input_D6_Bore_D2_Crosspin')
    assert c(ringhold, 'SetSuppression2', 0, 1, None)
    assert c(d, 'ForceRebuild3', False)
    assert not errors([c(d, 'FeatureByName', n) for n in s['mates']])
    save(d)
    s['phase_restoration'] = 'Restored with original rotor/ring angle datums; input lock recreated. Direct-transform probe superseded by mate-driven motion check.'
    s['assembly_sha256'] = hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest()
    stpath.write_text(json.dumps(s, indent=2))
finally:
    app.CommandInProgress = False
