"""Build native separate-material blade candidate; leave working rotor untouched."""
import json
import copy
import xml.etree.ElementTree as ET
from pathlib import Path
import cad
from cad import c, app, array, pythoncom, NULL, iref

FOLDER = cad.TASK / 'Bench_Prototype'
cad.OUT = FOLDER
cad.BUILD_LOG = FOLDER / 'NATIVE_PART_RECORD.json'
DEFINITION = json.loads((FOLDER / 'BLADE_CONSTRUCTION.json').read_text())


def poly_sketch(doc, row, name):
    if name == 'core':
        row = {'exterior_mm': DEFINITION['profiles']['skin']['interiors_mm'][0], 'interiors_mm': []}
    cad.sketch(doc)
    loops = [row['exterior_mm']] if name == 'core' else [row['exterior_mm'], *row['interiors_mm']]
    for loop in loops:
        for p, q in zip(loop, loop[1:]):
            if sum((a-b)**2 for a, b in zip(p, q)) < 1e-14:
                continue
            c(doc.SketchManager, 'CreateLine', p[0]/1000, p[1]/1000, 0., q[0]/1000, q[1]/1000, 0.)
    cad.extrude(doc, 0, 220, 'Defined_Material_Section_L220')
    if name == 'core':
        cad.face_circles(doc, 2, 0., [(.0095, 0., 0.)], .0018)
        cad.cut(doc, 'Spar_Bond_Channel_D3p6', .22001)
        for key in ['UD_upper', 'UD_lower']:
            source = cad.getdoc(FOLDER / ('BP_Blade_' + key + '.SLDPRT'))
            tool = c(c(source, 'GetBodies2', 0, False)[0], 'Copy')
            cad.activate(doc)
            main = c(doc, 'GetBodies2', 0, False)[0]
            assert c(doc, 'CreateFeatureFromBody3', tool, False, 1)
            bodies = c(doc, 'GetBodies2', 0, False)
            other = next(b for b in bodies if b.Name != main.Name)
            assert c(doc.FeatureManager, 'InsertCombineFeature', 15902, main, array([other], pythoncom.VT_DISPATCH))


def material_database():
    ET.register_namespace('mstns', 'http://www.solidworks.com/sldmaterials')
    ET.register_namespace('sldcolorswatch', 'http://www.solidworks.com/sldcolorswatch')
    source = cad.TASK / 'Materials/CycloProp_Prototype_Densities.sldmat'
    tree = ET.parse(source)
    classification = tree.getroot().find('classification')
    template = classification.find('material')
    for name, density in [('BLADE_CFRP_1550_PROVISIONAL', 1550), ('BLADE_CORE_52_PROVISIONAL', 52)]:
        node = copy.deepcopy(template)
        node.set('name', name)
        node.find('physicalproperties/DENS').set('value', str(density))
        classification.append(node)
    dest = FOLDER / 'Bench_Blade_Densities.sldmat'
    tree.write(dest, encoding='utf-16', xml_declaration=True)
    installed = Path(r'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\custom materials') / dest.name
    if not installed.exists():
        cad.shutil.copy2(dest, installed)
    assert cad.hashlib.sha256(dest.read_bytes()).digest() == cad.hashlib.sha256(installed.read_bytes()).digest()
    return str(installed)


def trunnion(doc, upper=False):
    source_path = cad.TASK / 'RevB_Isolated/RB_Part1.SLDPRT'
    source = cad.getdoc(source_path)
    body = c(c(source, 'GetBodies2', 0, False)[0], 'Copy')
    z0, z1 = (220, 232) if upper else (-12, 0)
    tool = c(c(app, 'GetModeler'), 'CreateBodyFromCyl', array([.0095, 0., z0/1000, 0., 0., 1., .0015, (z1-z0)/1000]))
    error = iref()
    intersection = c(body, 'Operations2', 15901, tool, error)
    assert intersection and len(intersection) == 1 and not error.value
    cad.activate(doc)
    feature = c(doc, 'CreateFeatureFromBody3', intersection[0], False, 1)
    assert feature
    feature.Name = 'Retained_Exact_Journal_Flat_And_Pin_Interface'
    cad.sketch(doc)
    cad.circle(doc, 9.5, 0, 1.2)
    cad.extrude(doc, 190 if upper else 0, 220 if upper else 30, 'D2p4_Bond_Stem_L30')


def main():
    original_hash = cad.hashlib.sha256((cad.TASK / 'RevB_Isolated/RB_Part1.SLDPRT').read_bytes()).hexdigest()
    original_mat = cad.MAT_DB
    custom_mat = material_database()
    # Preserve only the unfiled document owned by an interrupted attempt here.
    pending = c(app, 'GetFirstDocument')
    while pending:
        next_doc = c(pending, 'GetNext')
        if not c(pending, 'GetPathName') and c(pending, 'FeatureByName', 'Defined_Material_Section_L220'):
            backup = FOLDER / 'Recovery_Unassigned_Skin_Attempt.SLDPRT'
            assert not backup.exists()
            assert c(pending.Extension, 'SaveAs', str(backup), 0, 3, NULL, iref(), iref())
            c(app, 'CloseDoc', c(pending, 'GetTitle'))
        pending = next_doc
    paths = []
    app.CommandInProgress = True
    try:
        for name, row in DEFINITION['profiles'].items():
            print('BUILD_CONSTITUENT', name, flush=True)
            cad.MAT_DB = custom_mat
            material = 'BLADE_CORE_52_PROVISIONAL' if name == 'core' else 'BLADE_CFRP_1550_PROVISIONAL'
            path = cad.make_part('BP_Blade_' + name,
                                 'Separate manufactured blade constituent. Refer BLADE_CONSTRUCTION.json for layup, density assumptions and release holds. '
                                 'NACA0012 chord38/span220/pivot9.5 preserved. Not for fabrication until process/load/tolerance holds close.',
                                 material, lambda d, row=row, name=name: poly_sketch(d, row, name))
            record = json.loads(cad.BUILD_LOG.read_text())[path.stem]
            assert abs(record['mass_g']/1000 - row['mass_kg']) < 1e-6, (name, record['mass_g'], row['mass_kg'])
            paths.append(path)
        cad.MAT_DB = original_mat
        for upper in [False, True]:
            path = cad.make_part('BP_Blade_' + ('Upper' if upper else 'Lower') + '_Metal_Trunnion',
                                 '4340 normalized proposal. Exact retained external journal/flat/crosshole plusD2.4x30 bond stem, '
                                 '0.05mm radial bond gap in sparID2.5. Ground journal fit, transition fillet, dielectric isolation, '
                                 'bond preparation/cure, torsion/root bending/fatigue, crosspin and pullout proof remain holds.',
                                 'AISI 4340 Steel, normalized', lambda d, upper=upper: trunnion(d, upper))
            paths.append(path)
        path = FOLDER / 'BP_Manufactured_Blade_Candidate.SLDASM'
        assert not path.exists(), 'Inspect completed candidate rather than replacing it'
        template = c(app, 'GetUserPreferenceStringValue', 9)
        doc = c(app, 'NewDocument', template, 0, 0., 0.)
        assert doc
        cad.save(doc, path)
        for part in paths:
            cad.getdoc(part)
            cad.activate(doc)
            co = c(doc, 'AddComponent5', str(part), 0, '', False, '', 0., 0., 0.)
            assert co
            if c(co, 'IsFixed'):
                c(doc, 'ClearSelection2', True)
                assert c(co, 'Select4', False, NULL, False)
                c(doc, 'UnfixComponent')
            cad.set_transform(co, [0., 0., 0.], cad.np.eye(3))
            c(doc, 'ClearSelection2', True)
            assert c(co, 'Select4', False, NULL, False)
            c(doc, 'FixComponent')
        assert c(doc, 'ForceRebuild3', False)
        mp = c(doc.Extension, 'CreateMassProperty2')
        status = {'assembly': str(path), 'parts': [str(p) for p in paths], 'native_mass_kg': mp.Mass,
                  'analytical_mass_without_adhesive_allowance_kg': DEFINITION['assembled_mass_estimate_kg'] - .0005,
                  'mass_scope': 'Geometry/material estimate. Adhesive/seam allowance0.5g separate; not measured hardware.',
                  'representation': 'Constituents fixed at common blade datums to represent bonded manufacture; bond strength not demonstrated.',
                  'status': 'NATIVE MANUFACTURING CANDIDATE; NOT INSTALLED IN ROTOR / NOT FABRICATION RELEASED'}
        assert abs(mp.Mass - status['analytical_mass_without_adhesive_allowance_kg']) < .00015
        cad.save(doc)
        status['sha256'] = cad.hashlib.sha256(path.read_bytes()).hexdigest()
        (FOLDER / 'BLADE_NATIVE_BUILD.json').write_text(json.dumps(status, indent=2))
        assert original_hash == cad.hashlib.sha256((cad.TASK / 'RevB_Isolated/RB_Part1.SLDPRT').read_bytes()).hexdigest()
        print('BLADE_MANUFACTURING_CANDIDATE_BUILT', json.dumps(status), flush=True)
    finally:
        app.CommandInProgress = False
        cad.MAT_DB = original_mat


if __name__ == '__main__':
    main()
