from create_prototype_drawings import *
import re
builds=json.loads(BUILD_LOG.read_text())
bom=json.loads((TASK/'REVISED_NATIVE_MATERIAL_BOM.json').read_text())
quantities={row['part']:row['quantity'] for row in bom['rows']}
def prop(part,key):
 raw=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'');val=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
 resolved=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False);link=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
 c(part.Extension.CustomPropertyManager(''),'Get6',key,False,raw,val,resolved,link)
 return val.value or raw.value
extra={
 'RB_Endplate_Hub_Interface_RevA': ['G10/FR4 sheet, nominal thickness1.50; OD206; centre bore14.00. Quantity2.','Four blade-cartridge holes D10.02 on PCD190, at90degree spacing. Hole axes parallel to rotor axis.','Four hub-bolt clearance holesD2.80 onPCD22, clocked45degrees from blade stations.','Four lightening cutouts: contour governed by referenced native model; manufacturing contour tolerances and edge finish need release.','Cartridge hole-to-outer-edge nominal ligament2.99mm. G10 clamp crushing, waterjet damage and fatigue require review.','Flatness, hole positional tolerance, perpendicularity and dynamic balance limits await release. No18g mass target override applies.'],
 'RB_Blade_Pitch_Arm_Offset22p075_PROTOTYPE':['Machined7075-T6 proposed. Four identical offset arms.','Effective arm radius12.00; joint centre22.075 below arm datum. Existing D3/D-flat trunnion interface retained.','Boss axial thickness3.50; positive pin crossholeD1 at boss axial midplane1.75, directed along arm localX.','Line-ream arm and METAL trunnion together to1.00..1.02; proposed ISO8750 standard-duty1x8 coiled pin. Actual press retention/fatigue approval required.','Joint recessOD8/ID3.2, depth0.40. Platform3.50, local recessed thickness3.10.','Twin-web, boss and fillet contours governed by referenced native model; combined stress/fatigue and finish/tolerance release pending.','Metal trunnion construction/bond to composite blade remains undefined. Do not drill unspecified CFRP as a steel journal.'],
 'RB_Carbon_Tube_OD2_ID1_L46p527_PROTOTYPE':['Pultruded CFRP tube: OD2.00, ID1.00, cut length46.526653. Quantity4.','Assembled ball-centre distance56.526653. Insert each tube end2.50 into socket bond boreD2.10, depth2.70.','Nominal radial bond gap0.05. Adhesive, surface preparation, cure, length tolerance and pullout/fatigue qualification unresolved.','1550kg/m3 is a documented density assumption, not laminate strength or measured stock mass.'],
 'RB_Socket_Eye_D7_Sphere5p05_PROTOTYPE':['Machined7075-T6 proposed, quantity8. Socket ball centre is local origin.','Main eye OD7, thickness4.40, lower/side spherical cavityD5.05; axial mouthD4.40.','Female M6x0.35 cap interface: major envelopeD6, from localZ0.80 to2.20. Cap flange seats atZ2.20.','Open D6 body top admits D5 ball before cap installation. Thread fit, runout, tap-drill and full physical thread geometry need release.','Neck approx4x4, reaches7.50 from ball centre. Bond boreD2.10x2.70; nominal tube insertion2.50.','Qualified lubrication, wear, locking torque/process, pullout proof and cyclic tests required. Geometry is not a strength release.']}

def source_lines(name):
 part=getdoc(OUT/(name+'.SLDPRT'))
 description=prop(part,'DESIGN_DESCRIPTION')
 # Split existing dimensional definitions into readable inspection notes without inventing missing dimensions.
 lines=[x.strip() for x in re.split(r'(?<=[.;])\s+(?=[A-Z])',description) if x.strip()]
 material=next((x['assigned_material'] for x in bom['rows'] if x['part']==name+'.SLDPRT'),'')
 return ['Quantity'+str(quantities.get(name+'.SLDPRT','verify BOM'))+'. Assigned material: '+(material or 'UNASSIGNED; release hold')+'.']+lines+['RELEASE HOLD: supplied material, fits, finish, tolerances and approved loads/locking require review. Nominal thread envelopes are not tap-drill geometry.','Use model identified by SHA for referenced contour; this prototype inspection sheet does not release undimensioned manufacturing features.']

if __name__=='__main__':
 selected=[name for name in builds if name!='RB_Ball_Socket_Threaded_Retaining_Cap_PROTOTYPE']
 selected.extend(extra)
 for i,name in enumerate(selected,201):
  lines=extra.get(name) or source_lines(name)
  if name in builds:
   row=builds[name];size=max(abs(row['box_m'][j+3]-row['box_m'][j]) for j in range(3));scale=min(8.,.080/size)
  else:scale=.35 if 'Endplate' in name else 2. if 'Arm_' in name else 1.
  drawing(name,'CP-RB-'+str(i),lines,scale)
 drawing('RB_Assem20_Design_RevB','CP-RB-001',[
 'PROTOTYPE BENCH ASSEMBLY; no fabrication/operating release.',
 'Four NACA0012-intent Part1 blades, span220, chord38, pivot9.5; rotor pitch radius95.',
 'Eight retained F693ZZ-envelope cartridges. Blade nominal endfloat0.40total, centred0.20each side. Two hub shims0.65 preserve blade/shaft stations.',
 'Four rod centre distances56.526653; carbon-tube cut length46.526653. Eight capped spherical joints and four arm crosspins installed.',
 'Physical Oldham ring timing, neutral phase-15.8253856deg relative blade radial stations; prototype pitch approximately-34.9897 to+34.9911deg nominal.',
 'RELEASE HOLD: coupling play exceeds nominal pitch margin; loaded35degree compliance and continuous moving clearances unverified.',
 'SERVO SCREEN FAILED: present Xservo inertia-only requirement0.280Nm exceeds published0.216Nm at6V. Replacement/redesign and approved loads required.',
 'MASS: native reference sum about1.11kg; blade, rails and bearing assumptions prevent a measured-hardware claim. See REVISED_NATIVE_MATERIAL_BOM.csv.',
 'Current rotor setup angle remains a construction drive; XY setup distances retain saved pose. Usable travel/constraints require final consolidation.',
 'Assembly order, tolerance/fit register and physical verification plan are separate controlled review inputs. No aerodynamic/structural certification claimed.'
 ],.28,True)

