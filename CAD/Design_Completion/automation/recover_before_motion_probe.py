from cad import *
source = TASK / 'Recovery/Before_Coupling_Integration' / ASSEMBLY.name
assert source.is_file()
recovery = TASK / 'Recovery/Direct_Transform_Probe'
recovery.mkdir(parents=True, exist_ok=False)
d = getdoc(ASSEMBLY, 2)
activate(d)
save(d)
shutil.copy2(ASSEMBLY, recovery / ASSEMBLY.name)
for name in ['COUPLING_INTEGRATION_STATE.json', 'COUPLING_DRIVE_CHECK.json']:
    shutil.move(str(TASK / name), str(recovery / name))
c(app, 'CloseDoc', c(d, 'GetTitle'))
shutil.copy2(source, ASSEMBLY)
d = getdoc(ASSEMBLY, 2)
activate(d)
assert len(roots(d)) == 311
original = json.loads((recovery / 'COUPLING_INTEGRATION_STATE.json').read_text())
shaft = tf(roots(d)['3-Drive_Shaft-1'])
assert np.max(abs(np.array(shaft) - original['original_shaft_transform'])) < 1e-7
ringco = next(co for co in c(d, 'GetComponents', False) if logical(co.Name2).endswith('/4-Outer_Control_Ring-1'))
assert np.max(abs(np.array(tf(ringco)) - original['original_ring_transform'])) < 1e-7
print('RECOVERED_PRE_INTEGRATION_311_ROOTS_ORIGINAL_POSE', flush=True)
