from cad import *
source = TASK / 'Recovery/Before_Cartridge_Axial_Refinement'
rejected = TASK / 'Recovery/Rejected_Cartridge_Signed_Offsets'
rejected.mkdir(parents=True, exist_ok=False)
records = json.loads(BUILD_LOG.read_text())
shutil.copy2(BUILD_LOG, rejected / BUILD_LOG.name)
for original in source.glob('*.SLDPRT'):
    path = OUT / original.name
    part = getdoc(path)
    assert c(part.Extension, 'SaveAs', str(rejected / original.name), 0, 3, NULL, iref(), iref())
    c(app, 'CloseDoc', c(part, 'GetTitle'))
    shutil.copy2(original, path)
    part = getdoc(path)
    records[path.stem].update(inspect_part(part))
    records[path.stem]['mass_g'] = c(part.Extension, 'CreateMassProperty2').Mass * 1000
    records[path.stem]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    records[path.stem].pop('axial_refinement', None)
    print('RESTORED_UNINSTALLED_PART', original.name, flush=True)
BUILD_LOG.write_text(json.dumps(records, indent=2))
