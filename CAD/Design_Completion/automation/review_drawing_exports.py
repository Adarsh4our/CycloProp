from pathlib import Path
import fitz,json,hashlib
from PIL import Image,ImageDraw
folder=Path('CAD/Design_Completion/Drawings_Prototype');idx=json.loads((folder/'DRAWING_INDEX.json').read_text());rows=[];thumbs=[]
previous=json.loads((folder/'PDF_QA.json').read_text()) if (folder/'PDF_QA.json').exists() else {}
visual={r['drawing']:r.get('visual_review','not individually inspected') for r in previous.get('drawings',[])}
visual['CP-RB-003']='All3sheets rendered and text bounds checked; two balloon sheets visually inspected. Native label/attachment and BOM reconciliation in ASSEMBLY_BALLOON_DRAWING_STATE.json.'
for number,row in idx['drawings'].items():
 doc=fitz.open(row['pdf']);assert len(doc)>=1
 current_hash=hashlib.sha256(Path(row['model']).read_bytes()).hexdigest()
 freshness='matches recorded drawing source' if current_hash==row['model_sha256'] else 'historical source differs; geometry and drawing currency not reverified'
 renders=[];sizes=[]
 for i,page in enumerate(doc):
  text=page.get_text();outside=[]
  for b in page.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for span in line['spans']:
     r=fitz.Rect(span['bbox'])
     if r.x0<0 or r.y0<0 or r.x1>page.rect.width+.5 or r.y1>page.rect.height+.5:outside.append(span['text'])
     if r.x0>700 and 'Educational' not in span['text']:sizes.append(span['size'])
  assert 'NOT RELEASED FOR FABRICATION' in text,(number,i,'missing status')
  assert number in text and row['model_sha256'] in text,(number,i,'missing identity')
  assert not outside,(number,i,outside)
  png=folder/(number+('_PAGE_'+str(i+1) if len(doc)>1 else '')+'.png')
  page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(str(png));renders.append(str(png))
  thumb=Image.open(png).convert('RGB');thumb.thumbnail((900,637));thumbs.append((number+' p'+str(i+1),thumb.copy()))
 rows.append({'drawing':number,'page_count':len(doc),'source_freshness':freshness,'recorded_source_sha256':row['model_sha256'],'current_source_sha256':current_hash,'text_bounds':'passed','identity_and_model_sha256':'passed','release_status':'present','minimum_right_notes_size_pt':min(sizes) if sizes else None,'render':renders[0],'renders':renders,'visual_review':visual.get(number,'not individually inspected')})
for start in range(0,len(thumbs),8):
 canvas=Image.new('RGB',(1800,4*675),'#dddddd');draw=ImageDraw.Draw(canvas)
 for offset,(name,im) in enumerate(thumbs[start:start+8]):
  x=(offset%2)*900;y=(offset//2)*675;draw.text((x+10,y+8),name,fill='black');canvas.paste(im,(x,y+30))
 canvas.save(folder/('QA_CONTACT_'+str(start//8+1)+'.png'))
(folder/'PDF_QA.json').write_text(json.dumps({'scope':'All indexed PDFs/pages rendered; bounds, captured source identity and release marks checked. Current source freshness reported separately; historical mismatches do not establish current drawing currency. Visual review tracked separately; not fabrication certification.','drawings':rows},indent=2));print('PDF_TEXT_AND_RENDER_QA',len(rows),'drawings',sum(r['page_count'] for r in rows),'pages passed')
