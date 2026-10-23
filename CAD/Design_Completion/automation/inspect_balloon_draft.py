from cad import *
s=json.loads((TASK/'ASSEMBLY_BALLOON_DRAWING_STATE.json').read_text());doc=c(app,'GetOpenDocumentByName',s['drawing']);assert doc
print('SHEETS',c(doc,'GetSheetNames'),flush=True)
v=c(doc,'GetFirstView')
while v:
 notes=c(v,'GetNotes') or []
 print('VIEW',c(v,'GetName2'),'NOTES',len(notes),flush=True)
 for n in notes[:4]:
  print('LABEL',repr(c(n,'GetBomBalloonText',True)),'STYLE',c(n,'GetBomBalloonTextStyle',True),'TEXT',repr(c(n,'GetText')),flush=True)
 v=c(v,'GetNextView')
