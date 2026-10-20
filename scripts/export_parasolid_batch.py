import hashlib
import json
from pathlib import Path

import pythoncom
from win32com.client import VARIANT
from win32com.client.dynamic import Dispatch


root = Path(__file__).resolve().parents[1] / 'CAD'
output = root / '2025'
sources = sorted(
    (p for p in root.rglob('*') if p.suffix.lower() in ('.sldprt', '.sldasm')
     and not p.name.startswith('~$') and output not in p.parents),
    key=lambda p: (p.suffix.lower() == '.sldasm', str(p)),
)
assert sources, 'No SolidWorks source files found'
hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
sw = Dispatch('SldWorks.Application')
sw._FlagAsMethod('OpenDoc6', 'GetOpenDocumentByName', 'ActivateDoc3', 'CloseDoc')
previous = {}
if (output / 'conversion_report.json').exists():
    previous = {r['source']: r for r in json.loads((output / 'conversion_report.json').read_text(encoding='utf-8'))}
records = []


def integer_ref():
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)


for source in sources:
    target = (output / source.relative_to(root)).with_suffix('.x_t')
    record = {'source': str(source), 'output': str(target)}
    opened = False
    doc = None
    try:
        if target.exists():
            assert b'PARASOLID' in target.read_bytes()[:256], 'Invalid existing file'
            record.update(previous.get(str(source), {}))
            record['status'] = 'existing'
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            doc = sw.GetOpenDocumentByName(str(source))
            if doc is None:
                errors, warnings = integer_ref(), integer_ref()
                doc = sw.OpenDoc6(str(source), 1 if source.suffix.lower() == '.sldprt' else 2,
                                  3, '', errors, warnings)
                record.update(open_errors=errors.value, open_warnings=warnings.value)
                opened = doc is not None
            assert doc is not None, 'SolidWorks could not open document'
            doc._FlagAsMethod('GetTitle', 'ClearSelection2')
            activation_error = integer_ref()
            active = sw.ActivateDoc3(doc.GetTitle(), False, 0, activation_error)
            assert active is not None, f'Activation failed: {activation_error.value}'
            if source.suffix.lower() == '.sldasm':
                doc._FlagAsMethod('ResolveAllLightWeightComponents')
                record['resolve_result'] = doc.ResolveAllLightWeightComponents(False)
            doc.ClearSelection2(True)
            extension = doc.Extension
            extension._FlagAsMethod('SaveAs')
            errors, warnings = integer_ref(), integer_ref()
            ok = extension.SaveAs(str(target), 0, 1, VARIANT(pythoncom.VT_DISPATCH, None), errors, warnings)
            record.update(save_errors=errors.value, save_warnings=warnings.value)
            assert ok and errors.value == 0, f'Export failed: {errors.value}'
            assert target.is_file() and target.stat().st_size > 256, 'Empty export'
            assert b'PARASOLID' in target.read_bytes()[:256], 'Invalid Parasolid header'
            record['status'] = 'exported'
        record['bytes'] = target.stat().st_size
    except Exception as exc:
        import traceback
        traceback.print_exc()
        record.update(status='failed', error=str(exc))
    finally:
        if opened and doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception as exc:
                record['close_warning'] = str(exc)
    records.append(record)
    print(json.dumps(record), flush=True)
    (output / 'conversion_report.json').write_text(json.dumps(records, indent=2), encoding='utf-8')

assert all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[p] for p in sources), 'Source file changed'
sw._FlagAsMethod('GetDocumentDependencies2')
for record in records:
    if Path(record['source']).suffix.lower() == '.sldasm':
        dependencies = sw.GetDocumentDependencies2(record['source'], True, True, False) or ()
        record['dependencies'] = list(dependencies)
        record['unavailable_dependency_paths'] = [str(p) for p in dependencies[1::2] if not Path(p).is_file()]
        print(json.dumps({'assembly': record['source'], 'unavailable_dependency_paths': record['unavailable_dependency_paths']}), flush=True)
(output / 'conversion_report.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
failures = [r for r in records if r['status'] == 'failed']
print(f'Finished: {len(records) - len(failures)}/{len(records)} outputs available', flush=True)
raise SystemExit(bool(failures))
