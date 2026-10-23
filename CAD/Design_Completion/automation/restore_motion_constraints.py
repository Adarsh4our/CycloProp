from cad import *
STATE=TASK/'RESTORED_MOTION_CONSTRAINTS.json';assert not STATE.exists()
d=getdoc(ASSEMBLY,2);activate(d);ro=roots(d)
recovery=TASK/'Recovery/Before_Restoring_Motion';recovery.mkdir()
assert c(d.Extension,'SaveAs',str(recovery/ASSEMBLY.name),0,3,NULL,iref(),iref())
watch=['3-Drive_Shaft-1','Assem3-1']+['Part1-'+str(n) for n in range(1,5)]
before={name:tf(ro[name]) for name in watch}
x=c(c(d,'FeatureByName','LimitDistance3'),'GetDefinition').Distance-.012
y=c(c(d,'FeatureByName','LimitDistance1'),'GetDefinition').Distance-.012
assert math.hypot(x,y)<=.006881
assert set_axis_positions(d,x,y,restore_limits=True)
rotor=c(d,'FeatureByName','RevB_SETUP_Rotor_Angle');assert c(rotor,'SetSuppression2',0,1,None)
assert c(d,'ForceRebuild3',False)
s={'before_transforms':before,'backup':str(recovery),'XY_saved_mm':[x*1000,y*1000],'limits':{}}
for name in ['LimitDistance3','LimitDistance1','Combined_XY_Radial_Limit_6p88mm']:
 f=c(d,'FeatureByName',name);fd=c(f,'GetDefinition')
 s['limits'][name]={'suppressed':bool(c(f,'IsSuppressed')),'advanced':bool(fd.IsAdvancedMate),'distance_mm':fd.Distance*1000,'minimum_mm':fd.MinimumDistance*1000,'maximum_mm':fd.MaximumDistance*1000}
 assert not s['limits'][name]['suppressed'] and s['limits'][name]['advanced']
for name,t in before.items():assert np.max(abs(np.array(tf(ro[name]))-t))<1e-6,(name,'pose moved on restoring limits')
s['rotor_setup_suppressed']=bool(c(rotor,'IsSuppressed'))
s['ring_setup_suppressed']=bool(c(c(d,'FeatureByName','RevB_SETUP_Ring_Angle'),'IsSuppressed'))
s['mate_errors']=errors(active_mates(d));STATE.write_text(json.dumps(s,indent=2));assert not s['mate_errors'],s['mate_errors']
save(d)
s.update({'complete':True,'status':'Native axis and existing radial travel limits restored; independent construction-angle holds suppressed. Saved shaft/blade/carriage poses preserved.','assembly_sha256':hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest(),'limits_of_check':['Native rebuild/mates and saved transforms checked. No additional free-drag/full-motion campaign after these geometry changes.','Physical loaded backlash, tolerance variation and supplier/operating release remain unverified.']});STATE.write_text(json.dumps(s,indent=2));print('USABLE_MOTION_LIMITS_RESTORED',json.dumps(s['limits']),flush=True)
