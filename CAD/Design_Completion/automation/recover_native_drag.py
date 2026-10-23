from cad import *
source = TASK / 'Recovery/Before_Native_Drag_Check' / ASSEMBLY.name
recovery = TASK / 'Recovery/Native_Drag_Probe'
recovery.mkdir(parents=True, exist_ok=False)
d = getdoc(ASSEMBLY, 2)
save(d)
shutil.copy2(ASSEMBLY, recovery / ASSEMBLY.name)
shutil.move(str(TASK / 'COUPLING_DRIVE_CHECK.json'), str(recovery / 'COUPLING_DRIVE_CHECK.json'))
c(app, 'CloseDoc', c(d, 'GetTitle'))
shutil.copy2(source, ASSEMBLY)
d = getdoc(ASSEMBLY, 2)
activate(d)
assert len(roots(d)) == 323
print('RECOVERED_COUPLING_BEFORE_DRAG', flush=True)
