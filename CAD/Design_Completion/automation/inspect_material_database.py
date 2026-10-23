raise RuntimeError('Historical material-database debug draft; do not rerun. See Materials/DATABASE_INSTALLATION.json and completed material assignment states.')
from cad import *
print('DATABASES',c(app,'GetMaterialDatabases'),flush=True)
p=getdoc(OUT/'RB_Endplate_Hub_Interface_RevA.SLDPRT')
file=TASK/'Materials/CycloProp_Prototype_Densities.sldmat'
c(p,'SetMaterialPropertyName2','Default',str(file),'G10_FR4_1850_DENSITY_ONLY_PROVISIONAL')
db=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
print('READBACK',c(p,'GetMaterialPropertyName2','Default',db),db.value,flush=True)
mp=c(p.Extension,'CreateMassProperty2');print('MASS_DENSITY',mp.Mass*1000,mp.Mass/mp.Volume,flush=True)
