from cad import *
import textwrap
from datetime import datetime,timezone
FOLDER=TASK/'Drawings_Prototype';FOLDER.mkdir(exist_ok=True)
INDEX=FOLDER/'DRAWING_INDEX.json'
index=json.loads(INDEX.read_text()) if INDEX.exists() else {'status':'PROTOTYPE / NOT RELEASED FOR FABRICATION','drawings':{}}
def note(doc,text,x,y,height=.0026):
 c(doc,'ClearSelection2',True);obj=c(doc,'InsertNote',text);assert obj
 ann=c(obj,'GetAnnotation');assert c(ann,'SetPosition2',x,y,0.)
 fmt=c(ann,'GetTextFormat',0);fmt.CharHeight=height;fmt.TypeFaceName='Arial';assert c(ann,'SetTextFormat',0,False,fmt)
 return obj
def drawing(part_name,number,lines,scale=5.,assembly=False):
 model=OUT/(part_name+('.SLDASM' if assembly else '.SLDPRT'));assert model.exists()
 source_hash=hashlib.sha256(model.read_bytes()).hexdigest()
 if number in index['drawings']:
  old=index['drawings'][number];assert old['model_sha256']==source_hash and Path(old['drawing']).exists() and Path(old['pdf']).exists();return
 path=FOLDER/(number+'.SLDDRW');pdf=FOLDER/(number+'.pdf');assert not path.exists() and not pdf.exists()
 getdoc(model,2 if assembly else 1)
 template=c(app,'GetUserPreferenceStringValue',10);assert Path(template).exists()
 doc=c(app,'NewDocument',template,8,.420,.297);assert doc
 sheet=c(doc,'GetCurrentSheet');assert c(sheet,'SetSize',8,.420,.297)
 outlines=[]
 for name,x,y in [('*Front',.075,.180),('*Right',.195,.180),('*Isometric',.090,.095)]:
  view=c(doc,'CreateDrawViewFromModelView3',str(model),name,x,y,0.);assert view
  view.UseSheetScale=0;view.ScaleDecimal=scale
  bounds=list(c(view,'GetOutline'));factor=min(1.,.090/(bounds[2]-bounds[0]),.080/(bounds[3]-bounds[1]));view.ScaleDecimal*=factor
  outlines.append({'view':name,'outline_m':list(c(view,'GetOutline'))})
 note(doc,'CYCLOPROP  |  '+number+'  |  REV B  |  PROTOTYPE',.015,.281,.0035)
 note(doc,'NOT RELEASED FOR FABRICATION  -  NOMINAL DIMENSIONS IN mm',.015,.269,.003)
 note(doc,'MODEL: '+part_name,.015,.259,.0024)
 note(doc,'MODEL SHA256: '+source_hash,.015,.251,.002)
 text='DIMENSION / INTERFACE DEFINITION\n\n'+'\n'.join('\n'.join(textwrap.wrap(x,69,break_long_words=False,break_on_hyphens=False)) for x in lines)
 note(doc,text,.270,.239,.0026)
 note(doc,'View scale '+str(scale)+':1. All dimensions nominal unless a limit is explicitly stated.\nRelease holds apply: fits, loaded clearances, locking, fatigue and supplied material.\nThread solids show major envelopes; DO NOT use as tap-drill sizes.',.015,.042,.0024)
 assert c(doc,'ForceRebuild3',False)
 save(doc,path);activate(doc);save(doc,pdf)
 index['drawings'][number]={'model':str(model),'model_sha256':source_hash,'drawing':str(path),'drawing_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pdf':str(pdf),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'view_outlines':outlines,'scope':'Native referenced views plus dimensional/interface notes; no fabrication release. PDF visual inspection pending.'}
 INDEX.write_text(json.dumps(index,indent=2));print('DRAWING_AND_PDF',number,flush=True)
 c(app,'CloseDoc',c(doc,'GetTitle'))
 # Close source windows after preserving unsaved task data; assembly references remain loaded.
 if not assembly:
  source=getdoc(model)
  if c(source,'GetSaveFlag'):
   recovery=TASK/'Recovery/Drawing_Window_Snapshots';recovery.mkdir(exist_ok=True)
   target=recovery/model.name
   if not target.exists():assert c(source.Extension,'SaveAs',str(target),0,3,NULL,iref(),iref())
  c(app,'CloseDoc',c(source,'GetTitle'))

 activate(getdoc(ASSEMBLY,2))

if __name__=='__main__':
 drawing('RB_Ball_Socket_Threaded_Retaining_Cap_PROTOTYPE','CP-RB-108',[
 'MATERIAL: machined7075-T6, proposed. Quantity8.',
 'DATUM A: flange underside. DATUM B: thread axis. Ball centre lies2.20 belowA onB.',
 'Flange OD7.00; thickness0.50 aboveA. Male thread major OD6.00; length1.40 belowA.',
 'External thread M6x0.35. Thread class/runout and tool clearance require release; native model is a major envelope.',
 'Spherical seat diameter5.05, concentric with the specified ball centre. Through mouth diameter4.40.',
 'Two diametrically opposed tool notches: width0.60, radial depth0.35, through flange0.50. Notch centre plane throughB.',
 'Match to D5.00 ball and mating female-thread socket body. Open cap to insert ball; seat flange on body top.',
 'HOLD: qualify spherical fit/finish/lubrication, thin thread geometry, tightening torque and anti-loosening.',
 'HOLD: pullout, wear and cyclic fatigue tests. No operating-speed release or physical results available.',
 'Inspection: check free articulation after locking; verify ball cannot escape and rod centres remain56.526653 apart.'
 ],8.)
