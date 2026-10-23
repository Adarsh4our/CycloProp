from cad import *
result={}
for name in ['RB_M2x10_Ball_Compact_Screw_REFERENCE','RB_M2x12_Socket_Cap_REFERENCE']:
 p=getdoc(OUT/(name+'.SLDPRT'));result[name]={'box':exact_box(c(p,'GetBodies2',0,False)[0]),'volume_mm3':c(c(p,'GetBodies2',0,False)[0],'GetMassProperties',1.)[3]*1e9}
(TASK/'ARM_FASTENER_REPLACEMENT_INSPECTION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
