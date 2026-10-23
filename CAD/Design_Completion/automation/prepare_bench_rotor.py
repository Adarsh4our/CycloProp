"""Pack current live rotor into a new reference tree before development edits."""
from cad import *
from datetime import datetime, timezone
import subprocess

folder = TASK / 'Bench_Prototype/Bench_Rotor'
report = TASK / 'Bench_Prototype/ROTOR_ISOLATION.json'
assert not report.exists() and (not folder.exists() or not any(folder.iterdir()))
folder.mkdir(exist_ok=True)
recovery = TASK / 'Bench_Prototype/Starting_Live'
recovery.mkdir(exist_ok=True)
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in OUT.glob('*') if p.suffix.upper() in ('.SLDPRT', '.SLDASM') and not p.name.startswith('~$')}
d = getdoc(ASSEMBLY, 2)
live_copies = []
for name in ['RB_Assem20_Design_RevB.SLDASM', 'RB_Assem3.SLDASM', 'RB_Blade_Bearing_Cartridge_Set_PROTOTYPE.SLDASM']:
    doc = c(app, 'GetOpenDocumentByName', str(OUT / name))
    if doc and c(doc, 'GetSaveFlag'):
        path = recovery / name
        if not path.exists():
            assert c(doc.Extension, 'SaveAs', str(path), 0, 3, NULL, iref(), iref())
        live_copies.append(str(path))
source = recovery / 'Bench_Development_Source.SLDASM'
if not source.exists():
    assert c(d.Extension, 'SaveAs', str(source), 0, 3, NULL, iref(), iref())
copydoc = getdoc(source, 2, readonly=True)
app.CommandInProgress = True
try:
    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                    str(TASK / 'automation/pack_bench_native.ps1')], check=True)
    raw = json.loads((TASK / 'Bench_Prototype/BENCH_PACK_RESULT.json').read_text(encoding='utf-8-sig'))
    status = raw[1].get('value', raw[1]) if isinstance(raw[1], dict) else raw[1]
    assert status is not None and all(s == 0 for s in status), status
finally:
    app.CommandInProgress = False
working = folder / 'BD_Bench_Development_Source.SLDASM'
assert working.exists()
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in before.items())
state = {'utc': datetime.now(timezone.utc).isoformat(), 'assembly': str(working),
         'source': str(ASSEMBLY), 'source_native_hashes': before,
         'preserved_dirty_copies': live_copies, 'pack_go_status': list(status),
         'status': 'NEW DEVELOPMENT REFERENCE TREE; NATIVE RESOLUTION/MOTION CHECKS PENDING',
         'note': 'Original live assembly and original source files preserved. New candidate is not a physical or fabrication acceptance.'}
report.write_text(json.dumps(state, indent=2))
c(app, 'CloseDoc', c(copydoc, 'GetTitle'))
candidate = getdoc(working, 2)
activate(candidate)
print('BENCH_ROTOR_ISOLATED', str(working), len(status), flush=True)
