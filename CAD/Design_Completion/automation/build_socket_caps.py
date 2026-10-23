from cad import *
app.Visible = True

tool_path = ROOT / 'CAD/Rotor_Integration/Ball_Link_Prototype/Socket_Cavity_Tool_D5p05.SLDPRT'
tool_doc = getdoc(tool_path, readonly=True)
sphere = c(c(tool_doc, 'GetBodies2', 0, False)[0], 'Copy')
tool_hash = hashlib.sha256(tool_path.read_bytes()).hexdigest()

def cap(d):
    ring(d, 6, 4.4, .8, 2.2, 'M6x0p35_Male_Thread_Major_Envelope')
    ring(d, 7, 4.4, 2.2, 2.7, 'Ball_Retention_Cap_Flange')
    f = c(d, 'CreateFeatureFromBody3', c(sphere, 'Copy'), False, 1)
    assert f
    f.Name = 'Existing_D5p05_Spherical_Cavity_Tool'
    bodies = c(d, 'GetBodies2', 0, False)
    assert len(bodies) == 2
    # The sphere tool is larger than this small annular cap.
    bodies = sorted(bodies, key=lambda b: c(b, 'GetMassProperties', 1.)[3])
    f = c(d.FeatureManager, 'InsertCombineFeature', 15902, bodies[0], array([bodies[1]], pythoncom.VT_DISPATCH))
    assert f
    f.Name = 'Upper_Spherical_Bearing_Seat_D5p05'
    face_rectangles(d, 2.7, [(-3.6, -.3, -3.15, .3), (3.15, -.3, 3.6, .3)], 'Opposed_Pin_Tool_Notches', .5)
    box_m = exact_box(c(d, 'GetBodies2', 0, False)[0])
    assert abs(box_m[2] - .0008) < 1e-8 and abs(box_m[5] - .0027) < 1e-8, box_m

app.CommandInProgress = True
try:
    path = make_part('RB_Ball_Socket_Threaded_Retaining_Cap_PROTOTYPE',
              'Machined7075-T6 capped ball joint, replacing impossible assumed rigid insertion throughD4.4mouth. '
              'Male M6x0.35 envelope Z0.8..2.2, flangeOD7 Z2.2..2.7, throughmouthD4.4, matchedD5.05 spherical cavity. '
              'Two opposed0.6wide0.35radial notches for pin tool. Body female pocketD6 toZ0.8 opens forD5ball insertion. '
              'Nominal ball centres/tube insertion unchanged. Actual helical threads, thread runouts/fit, bearing surface finish/lubrication, '
              'locking process, tightening torque, repeated pullout, wear and fatigue require release and physical proof; no speed rating.',
              '7075-T6 (SN)', cap)
    (TASK / 'SOCKET_CAP_PART_DEFINITION.json').write_text(json.dumps({
        'part': str(path), 'spherical_tool_source': str(tool_path), 'tool_sha256': tool_hash,
        'assembly_sequence': ['Remove cap; insert ballD5 through bodyD6opening.',
                              'Screw cap onto female thread until flange seats; verify specified spherical clearance and free articulation.',
                              'Apply qualified anti-loosening process and proof-mark; no qualifying torque/process is yet established.',
                              'Install existing ball mounting bolt/spacers without clamping the socket.'],
        'limits': ['Cap is built but not installed until SOCKET_CAP_INTEGRATION_STATE.json reports completion.',
                   '7075-T6 replaces unspecified/PA12 candidate intent to enable precision machined thin fine threads; wear/lubrication qualification pending.',
                   'M6x0.35 is a custom fine thread, not an assumed off-the-shelf component.',
                   'Spherical surface retains misalignment freedom required by blade axial running clearance.']}, indent=2))
finally:
    app.CommandInProgress = False
