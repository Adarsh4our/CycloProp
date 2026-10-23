from cad import *
source=TASK/'Materials/CycloProp_Prototype_Densities.sldmat'
target=Path(r'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\custom materials\CycloProp_Prototype_Densities.sldmat')
assert not target.exists(), 'Do not overwrite installed material database'
shutil.copy2(source,target)
p=getdoc(OUT/'RB_Endplate_Hub_Interface_RevA.SLDPRT')
c(p,'SetMaterialPropertyName2','Default',str(target),'G10_FR4_1850_DENSITY_ONLY_PROVISIONAL')
db=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
print('MATERIAL_READBACK',repr(c(p,'GetMaterialPropertyName2','Default',db)),db.value,flush=True)
mp=c(p.Extension,'CreateMassProperty2');print('MASS_DENSITY',mp.Mass*1000,mp.Mass/mp.Volume,flush=True)
(TASK/'Materials/DATABASE_INSTALLATION.json').write_text(json.dumps({'source':str(source),'installed_copy':str(target),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reason':'SolidWorks requires database in a configured Material Databases folder; no preferences or existing databases modified. Portable copy retained with project. Density-only assumptions; no FE properties.','material_readback':c(p,'GetMaterialPropertyName2','Default',db),'database_readback':db.value},indent=2))
