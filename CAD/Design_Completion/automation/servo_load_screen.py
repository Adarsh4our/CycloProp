from pathlib import Path
import math,json
import numpy as np
source=Path(__file__).with_name('inertia_screen.py').read_text(encoding='utf-8-sig')
# Reuse the documented rigid planar inertia calculation without rewriting its historical report.
exec(source.split('\nres=',1)[0])
def displacement(t):return .012*math.sin(t)+math.sqrt(.040**2-(.012*(1-math.cos(t)))**2)-.040
lo,hi=-math.pi/4,math.pi/4
for _ in range(70):
 t=(lo+hi)/2
 if displacement(t)<.00688:lo=t
 else:hi=t
t=(lo+hi)/2
root=math.sqrt(.040**2-(.012*(1-math.cos(t)))**2)
jac=.012*math.cos(t)-(.012*(1-math.cos(t)))*.012*math.sin(t)/root
assert abs(displacement(t)-.00688)<1e-12
step=1e-6;assert abs((displacement(t+step)-displacement(t-step))/(2*step)-jac)<1e-10
peak_x=float(abs(net[:,0]).max())
peak_torque_x=peak_x*abs(jac)
peak_torque_y=float(abs(net[:,1]).max())*.012
catalog=2.2*9.80665*.01
result={'status':'FAILS provisional inertia-only X-axis torque screen at2640RPM; not a certified load or servo duty assessment','source':'https://www.teamsavox.com/product/sh-0257mgp/','supplier_pdf':'https://web.teamsavox.com/wp-content/uploads/2025/06/SH-0257MGP_SpecSheet.pdf','retrieved_date':'2026-10-23','supplier_model':'SH-0257MG+; original assembly case envelope remains unverified against newer supplier revision','supplier_6V_torque_kgf_cm':2.2,'supplier_6V_torque_Nm':catalog,'supplier_4p8V_torque_kgf_cm':1.8,'supplier_6V_speed_s_per60deg':.09,'supplier_operating_travel_deg':90,'supplier_nominal_spline':'21T D4.8','existing_official_STEP_crown_D_mm':5.,'geometry_basis':'Existing R12horn/L40link, transverse offset12mm slider-crank; X eccentricity+6.88mm, Y0; virtual work tau=Fx*dx/dtheta. Does not equate supplier torque with continuous holding capability.','crank_departure_from_neutral_deg':math.degrees(t),'X_slider_Jacobian_m_per_rad':jac,'inertia_only_peak_X_force_N':peak_x,'inertia_only_peak_X_torque_Nm':peak_torque_x,'inertia_only_peak_Y_torque_Nm_at_Y0':peak_torque_y,'X_required_over_supplier_torque':peak_torque_x/catalog,'mass_assumption_kg_per_blade':m,'blade_pitch_inertia_assumption_kg_m2':J,'rpm':2640,'decision':'Do not release present servo selection for operating-speed use. Require suitably rated replacement or actuator/mechanical-advantage redesign after approved loads; preserve35deg pitch target and baseline2640RPM inputs.','excluded':['Aerodynamic hinge loads','Oldham inertia/friction reaction','Guide/bearing friction','Stop/jam loads','Measured blade inertia','Servo thermal duty, backlash and dynamic torque-speed behavior'],'physical_interface_holds':['Supplier must reconcile D4.8 nominal with D5.0 STEP output; no delivered hardware exists','Confirm exact case/ear/axis and horn retention screw dimensions from selected revision','Compatible commercial horn or custom spline fit qualification','Holding/thermal duty and dynamic response at declared loads and6V supply']}
assert peak_torque_x>catalog
Path('CAD/Design_Completion/SERVO_LOAD_AND_INTERFACE_SCREEN.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

